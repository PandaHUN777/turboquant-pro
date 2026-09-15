"""Exact top-100 cosine ground truth for the npy arms, and a check of the ann-benchmarks GT.

    python -m rabitq_public.gt --dataset wiki1024-10m --data-root /data
    python -m rabitq_public.gt --check glove-100-angular --data-root /data

Written to ``<data-root>/gt/<dataset>.npy`` (int64 corpus positions, best first). The
check recomputes exact top-10 for the first 200 queries of an ann-benchmarks arm and
records how well the provided neighbours agree with it.
"""

from __future__ import annotations

import argparse
import json
import os

import numpy as np

from .datasets import Dataset

TOP = 100
GT_BLOCK = 50_000  # keeps the score and argpartition temporaries near 1 GiB for 1,000-2,000 queries


def exact_topk(ds: Dataset, queries: np.ndarray, k: int = TOP) -> np.ndarray:
    best_s = np.full((len(queries), k), -np.inf, np.float32)
    best_i = np.full((len(queries), k), -1, np.int64)
    for start, blk in ds.blocks(GT_BLOCK):
        s = queries @ blk.T
        kk = min(k, s.shape[1])
        part = np.argpartition(-s, kk - 1, axis=1)[:, :kk]
        cs = np.concatenate([best_s, np.take_along_axis(s, part, axis=1)], axis=1)
        ci = np.concatenate([best_i, part + start], axis=1)
        sel = np.argpartition(-cs, k - 1, axis=1)[:, :k]
        best_s = np.take_along_axis(cs, sel, axis=1)
        best_i = np.take_along_axis(ci, sel, axis=1)
    order = np.argsort(-best_s, axis=1, kind="stable")
    return np.take_along_axis(best_i, order, axis=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dataset")
    g.add_argument("--check")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.data_root, "gt"), exist_ok=True)
    if a.dataset:
        out = os.path.join(a.data_root, "gt", f"{a.dataset}.npy")
        if not os.path.exists(out):
            ds = Dataset(a.dataset, a.data_root)
            tmp = out[:-4] + ".tmp.npy"
            np.save(tmp, exact_topk(ds, ds.queries))
            os.replace(tmp, out)
        print("gt", out, flush=True)
        return
    ds = Dataset(a.check, a.data_root)
    q = ds.queries[:200]
    mine = exact_topk(ds, q, 10)
    agree = float(
        np.mean(
            [len(np.intersect1d(mine[i], ds.gt[i, :10])) / 10 for i in range(len(q))]
        )
    )
    rec = dict(
        dataset=a.check, queries=len(q), provided_vs_exact_recall10=round(agree, 5)
    )
    with open(os.path.join(a.data_root, "gt", f"{a.check}.check.json"), "w") as f:
        json.dump(rec, f)
    print(rec, flush=True)


if __name__ == "__main__":
    main()
