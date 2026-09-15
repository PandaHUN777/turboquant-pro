"""ADC kernel v1 vs v2: search wall time and result agreement on one node.

Both kernels are compiled in the same pod from their sources (v1 = adc_scan.cpp at
856c4cb, v2 = the current one) and run on identical synthetic codes, queries, norms and
thread counts, so the timing comparison is paired. Where v1 cannot wrap (d' <= 256) the
two must return the same scores; above that the scores may differ by design.

    python bench_adc_kernel_v2.py --v1 adc_v1.so-dir --v2 adc_v2.so-dir --out result.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import time

import numpy as np


def load(path_dir: str):
    so = next(
        f
        for f in os.listdir(path_dir)
        if f.startswith("adc_scan") and f.endswith(".so")
    )
    spec = importlib.util.spec_from_file_location(
        "adc_scan", os.path.join(path_dir, so)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def synth(n, d, bits, q, seed=0):
    rng = np.random.default_rng(seed)
    codes = np.empty((n, d), np.uint8)
    for s in range(0, n, 250_000):
        e = min(n, s + 250_000)
        codes[s:e] = rng.integers(0, 2**bits, size=(e - s, d), dtype=np.uint8)
    cent = np.sort(rng.standard_normal(2**bits)).astype(np.float32)
    cnorm = (1 + 0.1 * rng.standard_normal(n)).astype(np.float32)
    vrnorm = (1 / np.sqrt(d) * (1 + 0.05 * rng.standard_normal(n))).astype(np.float32)
    queries = (rng.standard_normal((q, d)) / np.sqrt(d)).astype(np.float32)
    qbias = np.zeros(q, np.float32)
    return codes, queries, cent, cnorm, vrnorm, qbias


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v1", required=True)
    ap.add_argument("--v2", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--queries", type=int, default=200)
    ap.add_argument("--k", type=int, default=50)
    ap.add_argument(
        "--grid", default="1000000:256,1000000:1024,10000000:256,10000000:1024"
    )
    a = ap.parse_args()
    v1, v2 = load(a.v1), load(a.v2)
    rows = []
    for spec in a.grid.split(","):
        n, d = (int(x) for x in spec.split(":"))
        args = synth(n, d, 4, a.queries)
        rec = dict(
            n=n,
            d=d,
            bits=4,
            queries=a.queries,
            k=a.k,
            threads=os.environ.get("OMP_NUM_THREADS"),
        )
        for tag, mod in (("v1", v1), ("v2", v2)):
            t = time.perf_counter()
            ids, sc = mod.search(*args, a.k, True)
            rec[f"{tag}_s"] = round(time.perf_counter() - t, 3)
            rec[f"{tag}_ids"], rec[f"{tag}_sc"] = ids, sc
        same_scores = bool(
            np.allclose(rec["v1_sc"], rec["v2_sc"], rtol=1e-5, atol=1e-6)
        )
        overlap = float(
            np.mean(
                [
                    len(np.intersect1d(rec["v1_ids"][i], rec["v2_ids"][i])) / a.k
                    for i in range(a.queries)
                ]
            )
        )
        for key in ("v1_ids", "v2_ids", "v1_sc", "v2_sc"):
            del rec[key]
        rec.update(
            speedup=round(rec["v1_s"] / rec["v2_s"], 2),
            same_scores=same_scores,
            topk_overlap=round(overlap, 4),
        )
        print(json.dumps(rec), flush=True)
        rows.append(rec)
        del args
    env = dict(
        host=platform.node(),
        cpu=open("/proc/cpuinfo")
        .read()
        .split("model name")[1]
        .split("\n")[0]
        .strip(": \t"),
    )
    with open(a.out, "w") as f:
        json.dump(dict(env=env, rows=rows), f, indent=1)


if __name__ == "__main__":
    main()
