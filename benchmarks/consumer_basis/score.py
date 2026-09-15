"""Registered verdicts for the consumer-basis experiment (docs/PREREG_consumer_basis.md §4).

    python -m consumer_basis.score --results /data/cb/results [--markdown out.md]

Paired per-query difference in recall@10 (basis minus P), percentile bootstrap over the
arm's evaluation queries, 10,000 resamples, seed 0, 95% interval [lo, hi], mean m:
  BETTER if lo > 0 and m >= 0.01;  WORSE if hi < 0 and m <= -0.01;
  TIE if lo >= -0.01 and hi <= 0.01;  otherwise INCONCLUSIVE.
Primary endpoint: single-pass recall@10. Cells: arm x k for k in PRIMARY_DIMS.

H1  O vs P on asymmetric arms (msmarco, hotpotqa): HOLDS if BETTER in >= 5 of 6 cells and
    WORSE in none; REFUTED if BETTER in <= 1 or WORSE in any; else MIXED.
H2  O vs P on symmetric arms (msmarco-sym, hotpotqa-sym): HOLDS if TIE or BETTER in >= 5 of 6 cells
    and WORSE in none; REFUTED if WORSE in >= 2; else MIXED.
H3  S vs P on asymmetric arms: rule of H1.
Everything else (Q, k = 32 and 512, secondary arms, rerank endpoint) is reported, unscored.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
from collections import Counter

import numpy as np

from .arms import DIMS, PRIMARY_DIMS

N_BOOT = 10_000


def paired(a, b):
    d = (np.asarray(a, float) - np.asarray(b, float)) / 10
    rng = np.random.default_rng(0)
    means = d[rng.integers(0, len(d), size=(N_BOOT, len(d)))].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(d.mean()), float(lo), float(hi)


def verdict(m, lo, hi):
    if lo > 0 and m >= 0.01:
        return "BETTER"
    if hi < 0 and m <= -0.01:
        return "WORSE"
    if lo >= -0.01 and hi <= 0.01:
        return "TIE"
    return "INCONCLUSIVE"


def cells(recs, arms, basis, endpoint="hits_single", dims=PRIMARY_DIMS):
    out = []
    for arm in arms:
        if arm not in recs:
            continue
        r = recs[arm]["results"]
        for k in dims:
            m, lo, hi = paired(r[f"{basis}-{k}"][endpoint], r[f"P-{k}"][endpoint])
            out.append(
                dict(arm=arm, k=k, mean=m, lo=lo, hi=hi, verdict=verdict(m, lo, hi))
            )
    return out


def hypothesis(cs, rule):
    c = Counter(x["verdict"] for x in cs)
    n = len(cs)
    if n == 0:
        return "UNSCORED", dict(c)
    if rule == "gain":
        if c["BETTER"] >= n - 1 and c["WORSE"] == 0:
            return "HOLDS", dict(c)
        if c["BETTER"] <= 1 or c["WORSE"] > 0:
            return "REFUTED", dict(c)
        return "MIXED", dict(c)
    if c["TIE"] + c["BETTER"] >= n - 1 and c["WORSE"] == 0:
        return "HOLDS", dict(c)
    if c["WORSE"] >= 2:
        return "REFUTED", dict(c)
    return "MIXED", dict(c)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--markdown")
    a = ap.parse_args()
    recs = {}
    for p in glob.glob(os.path.join(a.results, "*.json")):
        with open(p) as f:
            r = json.load(f)
        recs[r["arm"]] = r
    asym, sym = ("msmarco", "hotpotqa"), ("msmarco-sym", "hotpotqa-sym")
    lines = ["## Registered hypotheses (single-pass recall@10, k in 64/128/256)", ""]
    for name, basis, arms, rule in (
        ("H1 O beats P, asymmetric", "O", asym, "gain"),
        ("H2 O ties P, symmetric", "O", sym, "tie"),
        ("H3 S beats P, asymmetric", "S", asym, "gain"),
    ):
        cs = cells(recs, arms, basis)
        v, c = hypothesis(cs, rule)
        lines.append(f"- **{name}**: {v} {c}")
        for x in cs:
            lines.append(
                f"  - {x['arm']} k={x['k']}: {x['mean']:+.4f} [{x['lo']:+.4f}, {x['hi']:+.4f}] {x['verdict']}"
            )
    lines += ["", "## All arms, recall@10 (single / rerank of top-100)", ""]
    lines.append(
        "| arm | kind | mismatch | basis | " + " | ".join(f"k={k}" for k in DIMS) + " |"
    )
    lines.append("|---|---|---:|---|" + "---|" * len(DIMS))
    for arm, r in sorted(recs.items()):
        for b in sorted(
            {key.rsplit("-", 1)[0] for key in r["results"]},
            key=lambda x: ("PQSO".find(x[0]), x),
        ):
            vals = []
            for k in DIMS:
                x = r["results"][f"{b}-{k}"]
                vals.append(
                    f"{np.mean(x['hits_single']) / 10:.3f} / {np.mean(x['hits_rerank']) / 10:.3f}"
                )
            lines.append(
                f"| {arm} | {r['kind']} | {r['mismatch_index']:.4f} | {b} | "
                + " | ".join(vals)
                + " |"
            )
    md = "\n".join(lines) + "\n"
    if a.markdown:
        with open(a.markdown, "w", encoding="utf-8") as f:
            f.write(md)
    print(md)


if __name__ == "__main__":
    main()
