"""Submit the observer-advantage campaign to NRP (run on Atlas). Operations only: nothing
here changes a scored quantity (docs/PREREG_observer_advantage.md section 7).

    python submit.py --commit <sha> --phase code
    python submit.py --commit <sha> --phase calibrate          # one job per class, under the guard
    python submit.py --commit <sha> --phase run [--maxpar N]   # every job, sized from measurement
    ... --dry-run                                              # print descriptors and preflight only

Phases, each a separate decision:

  code       One exempt pod clones the repository at the pinned commit and writes the
             packages the harness imports as ONE tar on the volume (policy: environments
             staged as a single file, never a file tree on CephFS). Every run pod unpacks it
             to /tmp and puts it ahead of the shared venv's older turboquant_pro, and records
             the commit in TQP_COMMIT.
  calibrate  The first job of each sizing class. Its usage is unknown until it runs, so it
             goes out only while the utilization guard's heartbeat is fresh; the guard
             writes what it measured to OBSERVATIONS.
  run        Every job, sized by nrp.sizing.request_for from the MEASURED usage of its class
             (the strictest reading when several exist). A class with no measurement is
             refused, never modelled.

The TQ family scans in numpy on NRP: the compiled kernel is built with -march=native, and
node types differ. Records carry the scan path and gate G3 checks it.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, "/home/claude/src/nats-bursting/python")
sys.path.insert(
    0, os.environ.get("OVB_PATH", "/archive/ahb-sjsu/tqp_rabitq_public/ovb")
)

from consumer_basis.arms import ARMS  # noqa: E402
from nrp import sizing as nrp_sizing  # noqa: E402

from observer_advantage.grid import EXACT, jobs  # noqa: E402

NS = "ssu-atlas-ai"
PVC = "tqp-rbq-data"
APP = "tqp-oa"
BATCH = "tqp-observer-advantage"
ZONE = {"topology.kubernetes.io/zone": "ucsd-nrp"}
REPO = "https://github.com/ahb-sjsu/turboquant-pro"
PACKAGES = (
    "turboquant_pro",
    "benchmarks/nrp",
    "benchmarks/consumer_basis",
    "benchmarks/rabitq_public",
    "benchmarks/observer_advantage",
)
STATE_DIR = "/archive/ahb-sjsu/tqp_observer_advantage/pool"
OBSERVATIONS = os.path.join(STATE_DIR, "observations.json")
GUARD_HEARTBEAT = os.path.join(STATE_DIR, "utilization_guard.heartbeat")
GUARD_MAX_AGE_S = 300
WANT_CPU = 4
LARGE_ROWS = 500_000


def code_tar(commit):
    return f"/data/oa/code/{commit}.tar"


def preamble(commit, cpu):
    """Threads follow the pod's CPU request: BLAS for the TQ scan and faiss, and
    CB_WORKERS for consumer_basis's exact top-k, so a 1-CPU pod does not oversubscribe.
    """
    return f"""set -euo pipefail
export PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS={cpu} OMP_NUM_THREADS={cpu} CB_WORKERS={cpu}
export TQP_COMMIT={commit}
tar -xf /data/env/env.tar -C /tmp venv
mkdir -p /tmp/code && tar -xf {code_tar(commit)} -C /tmp/code
export PATH=/tmp/venv/bin:$PATH PYTHONPATH=/tmp/code:/tmp/code/benchmarks
"""


def job_name(job, role="run"):
    """Calibration and run Jobs get different names: a name whose completed Job still
    exists is silently not resubmitted, and a watcher would report the old success."""
    prefix = "oa-c-" if role == "calibrate" else "oa-"
    return prefix + re.sub(r"[^a-z0-9-]", "-", job["job_id"].lower())


def size_class(job):
    lo, hi = ARMS[job["arm"]][1]
    return f"{job['family']}-{'large' if hi - lo >= LARGE_ROWS else 'small'}"


def calibration_jobs_on_cluster():
    """Names of calibration Jobs that exist on the cluster in any state. The run
    phase leaves their grid jobs to them: a finished one wrote its cells, and a
    running one is writing them."""
    import subprocess

    r = subprocess.run(
        [
            "kubectl",
            "-n",
            NS,
            "get",
            "jobs",
            "-l",
            "atlas.io/role=calibrate",
            "-o",
            "jsonpath={.items[*].metadata.name}",
        ],
        capture_output=True,
        text=True,
        timeout=90,
    )
    if r.returncode != 0:
        raise SystemExit(f"cannot list calibration Jobs: {r.stderr.strip()}")
    return set(r.stdout.split())


def calibrated():
    """Calibration Jobs that already completed, from the pool runner's state."""
    try:
        with open(os.path.join(STATE_DIR, "oa-calibrate.json"), encoding="utf-8") as f:
            return set(json.load(f).get("done", []))
    except (OSError, ValueError):
        return set()


def calibration_jobs():
    """For each sizing class, the first job in grid order that has not already
    completed a calibration run. A calibration Job can finish without leaving a
    measurement (shorter than the guard's sampling); its name cannot be reused,
    and rerunning it would skip its finished cells and measure nothing, so the
    class calibrates on its next member instead."""
    done = calibrated()
    seen, out = set(), []
    for j in jobs():
        c = size_class(j)
        if c not in seen and job_name(j, "calibrate") not in done:
            seen.add(c)
            out.append(j)
    return out


def class_usage(cls):
    """The strictest measured usage among this class's Jobs, or None if none was measured:
    the highest peak (the pod must survive it) against the lowest means (the floors must
    hold for every member)."""
    try:
        with open(OBSERVATIONS, encoding="utf-8") as fh:
            obs = json.load(fh)
    except (OSError, ValueError):
        return None
    members = {
        job_name(j, role)
        for j in jobs()
        if size_class(j) == cls
        for role in ("calibrate", "run")
    }
    rows = [
        o
        for name, o in obs.items()
        if name in members and o.get("mean_cpu_cores") and o.get("mean_mem_gib")
    ]
    if not rows:
        return None
    return nrp_sizing.Usage(
        mean_cpu_cores=min(o["mean_cpu_cores"] for o in rows),
        mean_mem_gib=min(o["mean_mem_gib"] for o in rows),
        peak_mem_gib=max(o.get("peak_mem_gib") or o["mean_mem_gib"] for o in rows),
    )


def exempt_sized(cls):
    """True when this class's model fits the exempt class, so it was calibrated there."""
    members = [j for j in jobs() if size_class(j) == cls]
    return bool(members) and model_gib(members[0]) <= nrp_sizing.EXEMPT_MEM_GIB


def exempt_class_proven(cls):
    """True when this class fits the exempt class and one of its calibration Jobs
    completed there. Exempt pods (<= 1 CPU, <= 2 GiB) are not held to the
    utilization floors, so no usage measurement is needed to size them; the one
    risk is running out of memory, which a completed exempt run rules out. A
    fiqa calibration finishes in under a minute, before the guard's second
    sample, so this completion is the only evidence such a class can leave."""
    members = [j for j in jobs() if size_class(j) == cls]
    if not members or model_gib(members[0]) > nrp_sizing.EXEMPT_MEM_GIB:
        return False
    return any(job_name(j, "calibrate") in calibrated() for j in members)


def model_gib(job):
    """First-run memory request for a calibration job: the corpus as loaded (np.load plus
    the float32 copy), its KMAX projection, one k-dim codec copy of it, and 1 GiB for the
    interpreter and faiss. A model, used for nothing but the one calibration pod per class.
    """
    lo, hi = ARMS[job["arm"]][1]
    n = hi - lo
    return (2 * n * 1024 * 4 + n * 256 * 4 + 2 * n * 256 * 4) / 2**30 + 1.0


def guard_is_running():
    try:
        return time.time() - os.path.getmtime(GUARD_HEARTBEAT) < GUARD_MAX_AGE_S
    except OSError:
        return False


def descriptor(name, script, cpu, mem_gib, role):
    from nats_bursting import JobDescriptor, Resources, Volume

    return JobDescriptor(
        name=name,
        image="python:3.12",
        command=["/bin/bash", "-lc", script],
        resources=Resources(
            cpu=str(cpu), memory=f"{mem_gib}Gi", ephemeral_storage="6Gi"
        ),
        labels={"app": APP, "atlas.io/batch": BATCH, "atlas.io/role": role},
        node_selector=dict(ZONE),
        backoff_limit=0,
        volumes=[Volume(name="data", mount_path="/data", claim_name=PVC)],
    )


def code_descriptor(commit):
    tar = code_tar(commit)
    arms = " ".join(
        f"/data/cb/{a}/hashes.json" for a in sorted({j["arm"] for j in jobs()})
    )
    script = f"""set -euo pipefail
ls -la /data/env/env.tar {arms}
echo "results so far:"; ls /data/oa/results 2>/dev/null || true
if [ -f {tar} ]; then echo "already staged: {tar}"; exit 0; fi
git clone -q --filter=blob:none --no-checkout {REPO} /tmp/src
git -C /tmp/src sparse-checkout set --no-cone {" ".join(PACKAGES)}
git -C /tmp/src checkout -q {commit}
test "$(git -C /tmp/src rev-parse HEAD)" = "{commit}"
mkdir -p /data/oa/code
tar -cf {tar}.tmp.$$ -C /tmp/src {" ".join(PACKAGES)}
mv {tar}.tmp.$$ {tar}
echo "staged {tar}"
"""
    return descriptor(f"oa-code-{commit[:12]}", script, 1, 2, "code")


def run_descriptor(commit, job, cpu, mem_gib, role):
    script = preamble(commit, cpu) + (
        f"python -m observer_advantage.cell --job-id {job['job_id']} "
        f"--root /data/cb --out /data/oa/results --threads {cpu}\n"
    )
    return descriptor(job_name(job, role), script, cpu, mem_gib, role)


def plan(commit, phase):
    """[(descriptor, why)] for a phase, or SystemExit naming every vetoed job."""
    if phase == "code":
        return [(code_descriptor(commit), "exempt class (1 CPU, 2 GiB)")]
    out, vetoes = [], []
    if phase == "calibrate":
        todo = calibration_jobs()
    else:  # a calibration Job has written, or is writing, its grid job's cells
        taken = calibrated() | calibration_jobs_on_cluster()
        todo = [j for j in jobs() if job_name(j, "calibrate") not in taken]
    for j in todo:
        cls = size_class(j)
        usage = class_usage(cls)
        if phase == "calibrate":
            if usage is not None or exempt_class_proven(cls):
                continue  # measured, or proven in the exempt class: the run phase sizes it
            if not guard_is_running():
                vetoes.append(
                    f"{job_name(j, phase)}: unmeasured, and no fresh guard heartbeat"
                )
                continue
            gib = model_gib(j)
            if gib <= nrp_sizing.EXEMPT_MEM_GIB:
                # policy: a cell that fits 1 CPU / 2 GiB goes in the exempt class
                cpu, mem = 1, 2
                why = f"calibrates {cls} (exempt, model {gib:.1f} GiB)"
            else:
                cpu, mem = WANT_CPU, int(gib + 0.999)
                why = f"calibrates {cls} (model {gib:.1f} GiB, under the guard)"
            out.append((run_descriptor(commit, j, cpu, mem, "calibrate"), why))
            continue
        if exempt_sized(cls) and (usage is not None or exempt_class_proven(cls)):
            # Calibrated in the exempt class, so it runs there: a pod capped at
            # 1 CPU reads 1 core whatever it could use, and a measurement taken at
            # a cap says nothing about behaviour above it.
            why = f"exempt class: {cls} was calibrated at 1 CPU / 2 GiB"
            out.append((run_descriptor(commit, j, 1, 2, "run"), why))
            continue
        req = nrp_sizing.request_for(usage, WANT_CPU)
        if isinstance(req, nrp_sizing.Refusal):
            vetoes.append(f"{job_name(j)} ({cls}): {req}")
            continue
        cpu, mem = req.cpu, req.memory_gib
        if not req.exempt:
            # A peak sampled every 30 s misses the load spike (np.load plus the
            # float32 copy, about 2x the corpus): a 6 GiB exact-search pod sized
            # from a sampled 5.3 GiB peak was OOM-killed. The request the class's
            # calibration completed at is the evidence that holds, so it is the floor.
            mem = max(mem, int(model_gib(j) + 0.999))
            bad = nrp_sizing.check(cpu, mem, usage)
            if bad:
                vetoes.append(f"{job_name(j)} ({cls}): at {mem}Gi " + "; ".join(bad))
                continue
        if req.exempt:  # no floors apply below the exempt line, so take its ceiling
            cpu, mem = 1, int(nrp_sizing.EXEMPT_MEM_GIB)
        out.append((run_descriptor(commit, j, cpu, mem, "run"), str(req)))
    if vetoes:
        raise SystemExit("PREFLIGHT VETO\n  " + "\n  ".join(vetoes))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True, help="full sha the pods run")
    ap.add_argument("--phase", required=True, choices=("code", "calibrate", "run"))
    ap.add_argument("--maxpar", type=int, default=6)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", a.commit):
        raise SystemExit("--commit must be a full 40-hex sha, so the run is pinned")
    planned = plan(a.commit, a.phase)
    for d, why in planned:
        print(d.name, d.resources.cpu, d.resources.memory, "|", why, flush=True)
    print(
        f"{len(planned)} job(s), phase {a.phase}, EXACT jobs included: "
        f"{sum(EXACT.lower() in d.name for d, _ in planned)}",
        flush=True,
    )
    if a.dry_run:
        return
    from nats_bursting import Client
    from openvector_bench.nrp_pool import PoolRunner

    built = {d.name: d for d, _ in planned}

    def submit(item):
        with Client() as client:
            return client.submit(built[item["name"]])

    os.makedirs(STATE_DIR, exist_ok=True)
    runner = PoolRunner(
        [dict(name=n) for n in built],
        job_name=lambda it: it["name"],
        submit=submit,
        state_path=os.path.join(STATE_DIR, f"oa-{a.phase}.json"),
        ns=NS,
        maxpar=1 if a.phase == "code" else a.maxpar,
        maxtries=3,
        wedge_s=8 * 3600,
        pend_s=2700,
    )
    print("PHASE_OK" if runner.run() else "PHASE_PARKED", flush=True)


if __name__ == "__main__":
    main()
