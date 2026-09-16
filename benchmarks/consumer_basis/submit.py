"""Submit the consumer-basis experiment to NRP (run on Atlas): staging, then one job per arm.

    python submit.py --phase stage|run [--arms ...] [--maxpar N]

Staging pods sit in the exempt class (1 CPU, 2 GiB). Compute pods request memory from the
per-arm estimate below (corpus + 512-d projection + selection scratch), and keep their
cores busy by running selection on CB_WORKERS threads with single-threaded BLAS. Pools
use openvector-bench's PoolRunner through the nats-bursting controller.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, "/home/claude/src/nats-bursting/python")
sys.path.insert(
    0, os.environ.get("OVB_PATH", "/archive/ahb-sjsu/tqp_rabitq_public/ovb")
)

from nrp import sizing as nrp_sizing  # noqa: E402

from consumer_basis.arms import ARMS  # noqa: E402

NS = "ssu-atlas-ai"
PVC = "tqp-rbq-data"
CODE_CM = "tqp-cb-code"
BATCH = "tqp-consumer-basis"
ZONE = {"topology.kubernetes.io/zone": "ucsd-nrp"}
STATE_DIR = "/archive/ahb-sjsu/tqp_rabitq_public/pool"
# Written by benchmarks/nrp/utilization_guard.py: what each Job actually averaged last time.
OBSERVATIONS = os.path.join(STATE_DIR, "observations.json")
GUARD_HEARTBEAT = os.path.join(STATE_DIR, "utilization_guard.heartbeat")
GUARD_MAX_AGE_S = 300
PREAMBLE = """set -euo pipefail
export PYTHONUNBUFFERED=1 HF_HOME=/tmp/hf OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
tar -xf /data/env/env.tar -C /tmp venv
export PATH=/tmp/venv/bin:$PATH PYTHONPATH=/code
"""


def rows(arm):
    lo, hi = ARMS[arm][1]
    return hi - lo


def est_gib(arm, workers):
    n = rows(arm)
    return (n * 1024 * 4 + n * 512 * 4 + workers * 32 * n * 16) / 2**30 + 1.0


def observed(name):
    """This Job's measured usage from the last time it ran, or None."""
    try:
        with open(OBSERVATIONS, encoding="utf-8") as fh:
            o = json.load(fh).get(name)
    except (OSError, ValueError):
        return None
    if not o or not o.get("mean_cpu_cores") or not o.get("mean_mem_gib"):
        return None
    return nrp_sizing.Usage(
        mean_cpu_cores=o["mean_cpu_cores"],
        mean_mem_gib=o["mean_mem_gib"],
        peak_mem_gib=o.get("peak_mem_gib") or o["mean_mem_gib"],
    )


def guard_is_running():
    try:
        return time.time() - os.path.getmtime(GUARD_HEARTBEAT) < GUARD_MAX_AGE_S
    except OSError:
        return False


def descriptor(kind, arm):
    from nats_bursting import JobDescriptor, Resources, Volume

    vols = [
        Volume(name="data", mount_path="/data", claim_name=PVC),
        Volume(
            name="code",
            mount_path="/code/consumer_basis",
            config_map=CODE_CM,
            read_only=True,
        ),
    ]
    labels = {"app": "tqp-cb", "atlas.io/batch": BATCH, "atlas.io/role": kind}
    if kind == "stage":
        script = (
            PREAMBLE + f"python -m consumer_basis.stage --arm {arm} --root /data/cb\n"
        )
        res = Resources(cpu="1", memory="2Gi", ephemeral_storage="8Gi")
        est = (1.0, 1.5)
    else:
        small = rows(arm) < 200_000
        cpu = 1 if small else 4
        mem = 2 if small else math.ceil(1.25 * est_gib(arm, cpu))
        script = PREAMBLE + (
            f"export CB_WORKERS={cpu}\n"
            f"python -m consumer_basis.run --arm {arm} --root /data/cb --out /data/cb/results\n"
        )
        seen = observed(f"cb-{kind}-{arm}")
        if seen is not None:  # size from what this Job actually used last time
            cpu = nrp_sizing.cpu_request(seen.mean_cpu_cores, cpu)
            mem = max(mem, math.ceil(seen.peak_mem_gib * nrp_sizing.PEAK_HEADROOM))
            est = (seen.mean_cpu_cores, seen.mean_mem_gib)
        else:
            # Never measured: the model is a guess, so it only goes out under the guard.
            est = (0.8 * cpu, est_gib(arm, cpu))
        res = Resources(cpu=str(cpu), memory=f"{mem}Gi", ephemeral_storage="4Gi")
    name = f"cb-{kind}-{arm}"
    d = JobDescriptor(
        name=name,
        image="python:3.12",
        command=["/bin/bash", "-lc", script],
        resources=res,
        labels=labels,
        node_selector=dict(ZONE),
        backoff_limit=0,
        volumes=vols,
    )
    return d, est


def preflight(d, est_cpu, est_mem, measured):
    """Veto what the cluster would flag (rules in benchmarks/nrp/sizing.py).

    An unmeasured Job is sized from a model, which is a guess however careful; it may go out
    only while the utilization guard is watching, so a wrong guess is stopped by us in
    minutes rather than by the cluster after hours.
    """
    cpu = float(d.resources.cpu)
    mem = float(d.resources.memory.rstrip("Gi"))
    usage = nrp_sizing.Usage(
        mean_cpu_cores=est_cpu, mean_mem_gib=est_mem, peak_mem_gib=est_mem
    )
    problems = nrp_sizing.check(cpu, mem, usage)
    if problems:
        raise SystemExit(f"PREFLIGHT VETO {d.name}: " + "; ".join(problems))
    exempt = cpu <= 1 and mem <= 2
    if not measured and not exempt and not guard_is_running():
        raise SystemExit(
            f"PREFLIGHT VETO {d.name}: never measured, and no utilization guard heartbeat "
            f"newer than {GUARD_MAX_AGE_S}s at {GUARD_HEARTBEAT}"
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True, choices=("stage", "run"))
    ap.add_argument("--arms", nargs="*", default=list(ARMS))
    ap.add_argument("--maxpar", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    items = [dict(name=f"cb-{a.phase}-{arm}", arm=arm) for arm in a.arms]
    built = {}
    for it in items:
        d, (c, m) = descriptor(a.phase, it["arm"])
        preflight(d, c, m, measured=observed(d.name) is not None)
        built[it["name"]] = d
        print(d.name, d.resources.cpu, d.resources.memory, flush=True)
    if a.dry_run:
        return
    from nats_bursting import Client
    from openvector_bench.nrp_pool import PoolRunner

    def submit(item):
        with Client() as client:
            return client.submit(built[item["name"]])

    runner = PoolRunner(
        items,
        job_name=lambda it: it["name"],
        submit=submit,
        state_path=os.path.join(STATE_DIR, f"cb-{a.phase}.json"),
        ns=NS,
        maxpar=a.maxpar,
        maxtries=3,
        wedge_s=6 * 3600,
        pend_s=2700,
    )
    print("PHASE_OK" if runner.run() else "PHASE_PARKED", flush=True)


if __name__ == "__main__":
    main()
