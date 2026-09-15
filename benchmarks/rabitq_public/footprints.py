"""Memory sizing for NRP cells: an explicit model, corrected by measurement.

NRP counts over-requesting as a violation (usage must sit at 20-150% of the memory request),
and a guessed request is how four CPU pods were OOM-killed on 2026-09-03. So requests come
from measurements. The model below only chooses the first request for one *calibration*
cell per (arm, method): the largest configuration, seed 0, a real registered cell. Its
measured peak anonymous memory sets a per-class correction factor, and every other cell in
the class is sized as model x factor. ``submit_pool.py`` refuses a non-calibration cell
whose class has no measurement.

    python -m rabitq_public.footprints --results /data/results    # print factors and requests

Model terms (bytes; N rows, d dim, T threads, L nlist, o PCA dim, cs code bytes):
corpus in RAM (hdf5 arms: 2 N d 4 while normalizing; npy arms: 3 blocks of 250k rows),
training samples and their float64 copies, the index arrays, per-block encode temporaries,
and search scratch (tq kernel: a re-blocked code copy plus N x 12 bytes per thread).
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os

from .grid import DIMS, ROWS, cells

GIB = 2**30
BASE = 0.7 * GIB
BLOCK = 250_000
HDF5 = ("glove-100-angular", "nytimes-256-angular", "deep-image-96-angular")
NQ = {
    "glove-100-angular": 2000,
    "nytimes-256-angular": 2000,
    "deep-image-96-angular": 2000,
}


def _corpus(ds):
    n, d = ROWS[ds], DIMS[ds]
    if ds in HDF5:
        return 2 * n * d * 4
    extra = (
        9 * n if ds == "wiki1024-10m" else 0
    )  # keep-map and mask for the held-out queries
    return 3 * BLOCK * d * 4 + extra


def _rabitq_code(d, bits):
    return math.ceil(d * bits / 8) + 12


def model_bytes(cell, threads):
    ds, m = cell["dataset"], cell["method"]
    n, d = ROWS[ds], DIMS[ds]
    total = BASE + _corpus(ds)
    pca_fit = 100_000 * d * 20 + d * d * 8
    if m == "tq":
        o = cell["out_dim"]
        total += pca_fit + n * (2 * o + 8) + threads * n * 12 + BLOCK * o * 16
    elif m == "rabitq_flat":
        total += 200_000 * d * 8 + n * _rabitq_code(d, cell["bits"]) + BLOCK * d * 8
    elif m == "rabitq_ivf":
        L = cell["nlist"]
        total += (
            40 * L * d * 8 + n * (_rabitq_code(d, cell["bits"]) + 8) + BLOCK * d * 8
        )
    elif m == "pca_rabitq_ivf":
        L, o = cell["nlist"], cell["out_dim"]
        total += (
            pca_fit
            + 40 * L * (d + o) * 4 * 2
            + n * (_rabitq_code(o, cell["bits"]) + 8)
            + BLOCK * (d + o) * 8
        )
    elif m == "rabitqlib_ivf":
        L = cell["nlist"]
        # corpus copy is memory-mapped (page cache); allow one internal float32 copy of the
        # largest cluster batch plus the codes
        total += (
            40 * L * d * 8 + n * 4 + n * _rabitq_code(d, cell["bits"]) + BLOCK * d * 8
        )
    elif m in ("pq", "opq"):
        total += 200_000 * d * 8 + n * cell["m"] + BLOCK * d * 8 + d * d * 8
    return total


def cpu_for(cell):
    """1 CPU (exempt class) when the model fits 2 GiB with margin, else 4."""
    return 1 if model_bytes(cell, 1) * 1.25 <= 2 * GIB else 4


def calibration_cells():
    """The largest-memory configuration of each (arm, method), seed 0."""
    best = {}
    for c in cells():
        if c["seed"] != 0:
            continue
        key = (c["dataset"], c["method"])
        if key not in best or model_bytes(c, 4) > model_bytes(best[key], 4):
            best[key] = c
    return list(best.values())


def factors(results_dir):
    """Per-class measured/model ratio from finished calibration cells."""
    out = {}
    calib = {c["cell_id"]: c for c in calibration_cells()}
    for p in glob.glob(os.path.join(results_dir, "*.json")):
        with open(p, encoding="utf-8") as f:
            r = json.load(f)
        cid = r["cell"]["cell_id"]
        if cid not in calib or not r.get("peak_anon_gib"):
            continue
        c = calib[cid]
        out[f"{c['dataset']}/{c['method']}"] = dict(
            cell=cid,
            measured_gib=r["peak_anon_gib"],
            model_gib=round(model_bytes(c, r["threads"]) / GIB, 3),
            factor=round(r["peak_anon_gib"] * GIB / model_bytes(c, r["threads"]), 3),
        )
    return out


def sizing(cell, factors_path=None, calibrating=False):
    """(cpu, estimated peak GiB, source) or None when the class is unmeasured.

    ``factors_path`` is the JSON the driver writes from the ``--emit-factors`` job log.
    """
    cpu = cpu_for(cell)
    est = model_bytes(cell, cpu) / GIB
    if calibrating:
        return cpu, est, "model"
    if not factors_path or not os.path.exists(factors_path):
        return None
    with open(factors_path, encoding="utf-8") as fh:
        f = json.load(fh).get(f"{cell['dataset']}/{cell['method']}")
    if f is None:
        return None
    return cpu, est * max(f["factor"], 0.25), "measured-factor"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results")
    ap.add_argument("--emit-factors", action="store_true", help="one log line")
    a = ap.parse_args()
    if a.emit_factors:
        print("FACTORS_JSON " + json.dumps(factors(a.results)), flush=True)
        return
    for c in sorted(calibration_cells(), key=lambda c: (c["dataset"], c["method"])):
        cpu = cpu_for(c)
        print(
            f"{c['cell_id']:48s} cpu={cpu} model={model_bytes(c, cpu) / GIB:6.2f} GiB request={math.ceil(1.25 * model_bytes(c, cpu) / GIB)} Gi"
        )
    if a.results:
        print(json.dumps(factors(a.results), indent=1))


if __name__ == "__main__":
    main()
