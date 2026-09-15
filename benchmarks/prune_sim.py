"""Experiment 4: can the ADC scan skip vectors early, the way RaBitQ's error bounds do?

For each query the kernel's score is monotone in acc[n] = sum_j lut_u8[j][code[n][j]].
After scanning the first m dims, acc[n] <= partial_m[n] + R_m, where R_m is the sum of
the per-dim table maxima of the remaining dims (exact bound), or approximately
<= partial_m[n] + mu_m + z * sigma_m using the corpus's per-dim code frequencies
(statistical bound, can prune a true neighbour). A vector (or a whole block of 32, the
kernel's unit) is prunable once its bound's score falls below the k-th best score.

This simulation uses the oracle threshold (the final k-th best score), so it is an upper
bound on what a streaming threshold achieves. It reports, per checkpoint m and bound:
the fraction of vectors and of 32-blocks prunable, the dims-scanned saving, and recall of
the top-k after statistical pruning against the unpruned kernel ranking.

    python prune_sim.py --data-root /data --out prune_sim.json
"""

from __future__ import annotations

import argparse
import json
import sys

import numpy as np

sys.path.insert(0, "/code")


def uint8_lut(q_rot, cent):
    lut_f = (q_rot[:, None] * cent[None, :]).astype(np.float32)
    dmin = lut_f.min(axis=1)
    rmax = max(float((lut_f.max(axis=1) - dmin).max()), 1e-20)
    scale = np.float32(rmax / 255.0)
    u = np.clip(((lut_f - dmin[:, None]) / scale + 0.5).astype(np.int64), 0, 255)
    return u, scale, np.float32(dmin.sum())


def run(name, x, out_dim, bits, nq=100, k=50, seed=0):
    from turboquant_pro import ADCIndex, PCAMatryoshka

    q, c = x[:nq].copy(), x[nq:]
    pca = PCAMatryoshka(input_dim=c.shape[1], output_dim=out_dim)
    pca.fit(c[:50_000])
    ix = ADCIndex(pca.with_quantizer(bits=bits, seed=seed)).add(c)
    q_rot, qbias = ix._query_terms(q)
    codes, cent, vn, vr = ix._codes, ix._cent, ix._cnorm, ix._vrnorm
    n, d = codes.shape
    S = len(cent)
    freq = (
        np.stack([np.bincount(codes[:, j], minlength=S) for j in range(d)]) / n
    )  # (d, S)
    checkpoints = [d // 8, d // 4, d // 2, 3 * d // 4]
    zs = (2.0, 3.0, 4.0)
    agg = {}
    for qi in range(nq):
        u, scale, bias = uint8_lut(q_rot[qi], cent)
        look = u[np.arange(d)[None, :], codes]  # (n, d) int64
        csum = np.cumsum(look, axis=1)
        acc = csum[:, -1]
        score = (qbias[qi] + vn * (scale * acc + bias)) * vr
        top = np.argpartition(-score, k)[:k]
        thr = score[top].min()
        umax = u.max(axis=1)
        mean_j = (freq * u).sum(axis=1)
        var_j = (freq * u**2).sum(axis=1) - mean_j**2
        for m in checkpoints:
            part = csum[:, m - 1]
            rest_max = umax[m:].sum()
            rest_mu, rest_sd = mean_j[m:].sum(), np.sqrt(var_j[m:].sum())
            bounds = {"exact": part + rest_max}
            for z in zs:
                bounds[f"z{z:g}"] = part + rest_mu + z * rest_sd
            # ADSampling-style: extrapolate this vector's own centered partial sum to the
            # remaining dims (a neighbour that scores high early keeps scoring high), with
            # z standard deviations of the extrapolation error
            mu_pre = mean_j[:m].sum()
            scaled = part + rest_mu + (part - mu_pre) * (d - m) / m
            sd_scale = np.sqrt(var_j[m:].sum() + var_j[:m].sum() * ((d - m) / m) ** 2)
            for z in zs:
                bounds[f"ad{z:g}"] = scaled + z * sd_scale
            for bname, ub in bounds.items():
                ub_score = (qbias[qi] + vn * (scale * ub + bias)) * vr
                pr = ub_score < thr
                blocks = pr[: (n // 32) * 32].reshape(-1, 32).all(axis=1)
                kept = np.flatnonzero(~pr)
                if len(kept) >= k:
                    ktop = kept[np.argpartition(-score[kept], k - 1)[:k]]
                else:
                    ktop = kept
                rec = len(np.intersect1d(ktop, top)) / k
                key = (m, bname)
                a = agg.setdefault(key, dict(vec=[], blk=[], rec=[]))
                a["vec"].append(pr.mean())
                a["blk"].append(blocks.mean())
                a["rec"].append(rec)
    rows = []
    for (m, bname), a in sorted(agg.items()):
        vec, blk = float(np.mean(a["vec"])), float(np.mean(a["blk"]))
        rows.append(
            dict(
                arm=name,
                out_dim=d,
                bits=bits,
                checkpoint=m,
                bound=bname,
                prunable_vectors=round(vec, 4),
                prunable_blocks=round(blk, 4),
                dims_saved_vector_level=round(vec * (1 - m / d), 4),
                dims_saved_block_level=round(blk * (1 - m / d), 4),
                recall_vs_unpruned=round(float(np.mean(a["rec"])), 4),
            )
        )
        print(json.dumps(rows[-1]), flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rows", type=int, default=200_000)
    ap.add_argument(
        "--configs",
        default="dbpedia-3large-1536:dbpedia3072:1536:2,dbpedia-3large-1536:dbpedia3072:1536:4,"
        "dbpedia-3large-1536:dbpedia3072:384:4,wiki-1024:wiki1024:1024:2,"
        "wiki-1024:wiki1024:1024:4,wiki-1024:wiki1024:256:4",
    )
    a = ap.parse_args()

    def load(d):
        x = np.asarray(
            np.load(f"{a.data_root}/{d}/part_000.npy", mmap_mode="r")[: a.rows],
            np.float32,
        )
        return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-30)

    rows = []
    configs = [c.split(":") for c in a.configs.split(",")]
    loaded = {}
    for name, d, od, bits in configs:
        if d not in loaded:
            loaded = {d: load(d)}
        rows += run(name, loaded[d], int(od), int(bits))
    with open(a.out, "w") as f:
        json.dump(rows, f, indent=1)


if __name__ == "__main__":
    main()
