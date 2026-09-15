"""Stop our own NRP pods that sit under the cluster's utilization floors.

    python utilization_guard.py --selector app=tqp-rbq --apply

The cluster requires 20-200% of requested CPU and 20-150% of requested memory, measured as a
time average; pods at or below 1 CPU and 2 GiB are exempt. A snapshot of `kubectl top` is not
evidence of compliance: on 2026-09-15 eight campaign pods were flagged at 1-4% CPU while a
snapshot showed several at ~3.7 of 4 cores, because long CephFS-bound phases sink the average.

This samples `kubectl top` every --interval seconds, keeps a rolling window per pod, and once a
pod is older than --grace reports (or with --apply deletes) the Job of any pod whose windowed
mean falls below --floor of its request. It never touches pods it did not match, and without
--apply it only prints, so it can run alongside a campaign as an alarm before the cluster's own.
"""

from __future__ import annotations

import argparse
import collections
import json
import subprocess
import time

EXEMPT_CPU, EXEMPT_MEM = 1.0, 2.0 * 2**30


def sh(*args, ns):
    cmd = ["kubectl", "-n", ns, "--request-timeout=40s", *args]
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=90, stdin=subprocess.DEVNULL
    )


def parse_cpu(v):
    """Kubernetes CPU quantity -> cores."""
    v = v.strip()
    if v.endswith("m"):
        return float(v[:-1]) / 1000
    if v.endswith("n"):
        return float(v[:-1]) / 1e9
    if v.endswith("u"):
        return float(v[:-1]) / 1e6
    return float(v)


def parse_mem(v):
    """Kubernetes memory quantity -> bytes."""
    v = v.strip()
    units = {
        "Ki": 2**10,
        "Mi": 2**20,
        "Gi": 2**30,
        "Ti": 2**40,
        "K": 1e3,
        "M": 1e6,
        "G": 1e9,
    }
    for u, mul in units.items():
        if v.endswith(u):
            return float(v[: -len(u)]) * mul
    return float(v)


def requests(ns, selector):
    """{pod: (cpu_cores, mem_bytes, job_name, age_s)} for running pods matching the selector."""
    r = sh(
        "get",
        "pods",
        "-l",
        selector,
        "--field-selector=status.phase=Running",
        "-o",
        "json",
        ns=ns,
    )
    if r.returncode:
        return {}
    now = time.time()
    out = {}
    for p in json.loads(r.stdout).get("items", []):
        res = p["spec"]["containers"][0].get("resources", {}).get("requests", {})
        if not res.get("cpu") or not res.get("memory"):
            continue
        job = next(
            (
                o["name"]
                for o in p["metadata"].get("ownerReferences", [])
                if o["kind"] == "Job"
            ),
            None,
        )
        start = p["status"].get("startTime")
        age = (
            now - time.mktime(time.strptime(start, "%Y-%m-%dT%H:%M:%SZ"))
            if start
            else 0.0
        )
        out[p["metadata"]["name"]] = (
            parse_cpu(res["cpu"]),
            parse_mem(res["memory"]),
            job,
            age,
        )
    return out


def usage(ns):
    """{pod: (cpu_cores, mem_bytes)} from metrics-server."""
    r = sh("top", "pods", "--no-headers", ns=ns)
    out = {}
    for line in r.stdout.splitlines():
        f = line.split()
        if len(f) >= 3:
            out[f[0]] = (parse_cpu(f[1]), parse_mem(f[2]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--namespace", default="ssu-atlas-ai")
    ap.add_argument("--selector", default="app=tqp-rbq")
    ap.add_argument("--interval", type=float, default=60.0)
    ap.add_argument("--window", type=int, default=15, help="samples kept per pod")
    ap.add_argument(
        "--grace", type=float, default=900.0, help="seconds before a pod is judged"
    )
    ap.add_argument(
        "--floor",
        type=float,
        default=0.25,
        help="fraction of request (cluster's is 0.20)",
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="delete the offending Job (default: report only)",
    )
    a = ap.parse_args()

    hist = collections.defaultdict(lambda: collections.deque(maxlen=a.window))
    acted = set()
    while True:
        req, use = requests(a.namespace, a.selector), usage(a.namespace)
        for pod, (rc, rm, job, age) in sorted(req.items()):
            if pod in use:
                hist[pod].append(use[pod])
            h = hist[pod]
            if age < a.grace or len(h) < a.window or job in acted:
                continue
            mc = sum(x[0] for x in h) / len(h)
            mm = sum(x[1] for x in h) / len(h)
            low = []
            if rc > EXEMPT_CPU and mc < a.floor * rc:
                low.append(f"cpu {mc:.2f}/{rc:g} cores = {100 * mc / rc:.0f}%")
            if rm > EXEMPT_MEM and mm < a.floor * rm:
                low.append(
                    f"mem {mm / 2**30:.1f}/{rm / 2**30:.1f} GiB = {100 * mm / rm:.0f}%"
                )
            if not low:
                continue
            stamp = time.strftime("%FT%TZ", time.gmtime())
            print(f"{stamp} UNDER-USED {pod} job={job} " + "; ".join(low), flush=True)
            if a.apply and job:
                r = sh("delete", "job", job, ns=a.namespace)
                print(
                    f"{stamp} {'DELETED' if not r.returncode else 'DELETE FAILED'} {job} {r.stderr.strip()}",
                    flush=True,
                )
                acted.add(job)
        for pod in list(hist):
            if pod not in req:
                del hist[pod]
        time.sleep(a.interval)


if __name__ == "__main__":
    main()
