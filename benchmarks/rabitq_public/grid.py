"""The frozen cell grid of the RaBitQ public comparison (docs/PREREG_rabitq_public.md section 2).

A cell is one (dataset, method, config, seed). ``cells()`` enumerates every registered
cell; ``cell_id`` is the stable name used for the result file and the NRP Job. Editing
this file after the preregistration commit is an amendment and must be recorded there.
"""

from __future__ import annotations

import math

SEEDS = (0, 1, 2)
DIMS = {
    "glove-100-angular": 100,
    "nytimes-256-angular": 256,
    "deep-image-96-angular": 96,
    "wiki1024-10m": 1024,
    "dbpedia-ada002-1m": 1536,
    "dbpedia-3large-1536-1m": 1536,
}
ROWS = {  # corpus rows, used only to fix nlist before any data is read
    "glove-100-angular": 1_183_514,
    "nytimes-256-angular": 290_000,
    "deep-image-96-angular": 9_990_000,
    "wiki1024-10m": 9_999_000,
    "dbpedia-ada002-1m": 990_000,
    "dbpedia-3large-1536-1m": 990_000,
}
HIGH_DIM = ("wiki1024-10m", "dbpedia-ada002-1m", "dbpedia-3large-1536-1m")
RABITQ_BITS = (1, 2, 3, 4, 5)
PQ_M = {
    "glove-100-angular": (20, 25, 50),
    "nytimes-256-angular": (32, 64, 128),
    "deep-image-96-angular": (24, 32, 48),
    "wiki1024-10m": (64, 128, 256, 512),
    "dbpedia-ada002-1m": (96, 192, 384, 768),
    "dbpedia-3large-1536-1m": (96, 192, 384, 768),
}


def nlist(dataset: str) -> int:
    return 2 ** round(math.log2(4 * math.sqrt(ROWS[dataset])))


def configs(dataset: str) -> list[dict]:
    d = DIMS[dataset]
    out = [dict(method="tq", out_dim=d, bits=b) for b in (2, 3, 4)]
    if dataset in HIGH_DIM:
        out += [
            dict(method="tq", out_dim=o, bits=b)
            for o in (d // 4, d // 2)
            for b in (3, 4)
        ]
    out += [dict(method="rabitq_flat", bits=b) for b in RABITQ_BITS]
    out += [
        dict(method="rabitq_ivf", bits=b, nlist=nlist(dataset)) for b in RABITQ_BITS
    ]
    out += [
        dict(method="rabitqlib_ivf", bits=b, nlist=nlist(dataset)) for b in RABITQ_BITS
    ]
    if dataset in HIGH_DIM:
        out += [
            dict(method="pca_rabitq_ivf", out_dim=o, bits=b, nlist=nlist(dataset))
            for o in (d // 4, d // 2)
            for b in (1, 2, 3)
        ]
    out += [dict(method=m, m=k) for m in ("pq", "opq") for k in PQ_M[dataset]]
    return out


def cell_id(dataset: str, cfg: dict, seed: int) -> str:
    parts = [dataset, cfg["method"]]
    for key in ("out_dim", "bits", "m", "nlist"):
        if key in cfg:
            parts.append(f"{key[0] if key != 'out_dim' else 'd'}{cfg[key]}")
    parts.append(f"s{seed}")
    return "-".join(parts)


def cells(datasets=None) -> list[dict]:
    return [
        dict(dataset=ds, seed=s, cell_id=cell_id(ds, c, s), **c)
        for ds in (datasets or DIMS)
        for c in configs(ds)
        for s in SEEDS
    ]


if __name__ == "__main__":
    from collections import Counter

    cs = cells()
    print(len(cs), "cells")
    print(Counter(c["dataset"] for c in cs))
    print(Counter(c["method"] for c in cs))
