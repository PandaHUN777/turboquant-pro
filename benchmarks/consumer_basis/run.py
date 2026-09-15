"""Run one arm: four truncation bases x five dimensions, exact search, per-query hits.

    python -m consumer_basis.run --arm msmarco --root /data/cb --out /data/cb/results

Every vector is L2-normalized; scores are inner products (cosine). Ground truth is exact
full-dimension top-10. For basis B and dimension k, queries and corpus are mapped to k
dims and searched exactly; recorded per evaluation query:
  hits_single  |top-10 in k dims  ∩  true top-10|
  hits_rerank  |top-10 after exact full-dim rescoring of the k-dim top-100  ∩  true top-10|

Bases (all fit without the evaluation queries):
  P  eigenvectors of the corpus second moment S = E[x x^T]            (reconstruction corner)
  Q  eigenvectors of the query second moment C = E[q q^T]
  S  eigenvectors of sym(C S) = (C S + S C) / 2, same map for both sides
  O  asymmetric optimum of E[(q^T x - q^T M x)^2] over rank-k M: with
     K = C^1/2 S^1/2 = U L V^T, queries map by (C^-1/2 U_k)^T, documents by (L_k V_k^T S^-1/2)
     (Eckart-Young on the weighted bilinear form; inverse square roots floored at
     EIG_FLOOR x the largest eigenvalue)
Each basis is computed once at the largest k; smaller k are prefixes.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import time

import numpy as np

from .arms import ARMS, DIMS, EIG_FLOOR, FIT_SUBSETS, K_CAND, K_EVAL, SIGMA_ROWS


def normalize_inplace(x, block=200_000):
    for s in range(0, len(x), block):
        v = x[s : s + block]
        v /= np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-30)
    return x


def second_moment(x, block=100_000):
    d = x.shape[1]
    m = np.zeros((d, d), np.float64)
    for s in range(0, len(x), block):
        v = x[s : s + block].astype(np.float64)
        m += v.T @ v
    return m / len(x)


def eigh_desc(m):
    w, v = np.linalg.eigh((m + m.T) / 2)
    order = np.argsort(w)[::-1]
    return w[order], v[:, order]


def mat_pow(m, p):
    w, v = eigh_desc(m)
    w = np.maximum(w, EIG_FLOOR * w[0])
    return (v * w**p) @ v.T


def bases(sig, cq, kmax):
    """Return {name: (query_map (kmax, d), doc_map (kmax, d))}."""
    out = {}
    _, vp = eigh_desc(sig)
    out["P"] = (vp[:, :kmax].T, vp[:, :kmax].T)
    _, vq = eigh_desc(cq)
    out["Q"] = (vq[:, :kmax].T, vq[:, :kmax].T)
    _, vs = eigh_desc((cq @ sig + sig @ cq) / 2)
    out["S"] = (vs[:, :kmax].T, vs[:, :kmax].T)
    c_half, s_half = mat_pow(cq, 0.5), mat_pow(sig, 0.5)
    c_ihalf, s_ihalf = mat_pow(cq, -0.5), mat_pow(sig, -0.5)
    u, lam, vt = np.linalg.svd(c_half @ s_half)
    qa = (c_ihalf @ u[:, :kmax]).T
    db = (lam[:kmax, None] * vt[:kmax]) @ s_ihalf
    out["O"] = (qa, db)
    return out


WORKERS = int(os.environ.get("CB_WORKERS", "4"))


def topk(queries, corpus, k, block=32):
    """Exact top-k by inner product. Query blocks run on WORKERS threads (run BLAS with one
    thread per worker): argpartition is single-threaded, so block-level parallelism keeps
    every requested core busy instead of idling during selection."""
    from concurrent.futures import ThreadPoolExecutor

    out = np.empty((len(queries), k), np.int64)

    def one(s):
        sc = queries[s : s + block] @ corpus.T
        part = np.argpartition(-sc, k - 1, axis=1)[:, :k]
        order = np.argsort(-np.take_along_axis(sc, part, axis=1), axis=1, kind="stable")
        out[s : s + block] = np.take_along_axis(part, order, axis=1)

    with ThreadPoolExecutor(WORKERS) as ex:
        list(ex.map(one, range(0, len(queries), block)))
    return out


def hits(gt10, cand10):
    return np.array(
        [len(np.intersect1d(gt10[i], cand10[i])) for i in range(len(gt10))], np.uint8
    )


def rerank10(queries, corpus, cand):
    out = np.empty((len(queries), K_EVAL), np.int64)
    for i in range(len(queries)):
        c = cand[i]
        s = corpus[c] @ queries[i]
        out[i] = c[np.argsort(-s, kind="stable")[:K_EVAL]]
    return out


def mismatch_index(sig, cq):
    """1 - cosine similarity of the two second-moment matrices (0 = same read geometry)."""
    return float(1 - np.sum(sig * cq) / (np.linalg.norm(sig) * np.linalg.norm(cq)))


def run(arm, root, out_dir, kmax=None):
    kmax = kmax or max(DIMS)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{arm}.json")
    if os.path.exists(path):
        return path
    t0 = time.time()
    d = os.path.join(root, arm)
    corpus = normalize_inplace(
        np.array(np.load(os.path.join(d, "corpus.npy")), np.float32)
    )
    fitq = normalize_inplace(np.array(np.load(os.path.join(d, "fit.npy")), np.float32))
    evalq = normalize_inplace(
        np.array(np.load(os.path.join(d, "eval.npy")), np.float32)
    )
    sig = second_moment(corpus[:SIGMA_ROWS])
    cq = second_moment(fitq)
    gt = topk(evalq, corpus, K_EVAL)
    rec = dict(
        arm=arm,
        kind=ARMS[arm][4],
        corpus_rows=len(corpus),
        fit_rows=len(fitq),
        eval_rows=len(evalq),
        dim=corpus.shape[1],
        mismatch_index=round(mismatch_index(sig, cq), 6),
        results={},
    )
    all_bases = bases(sig, cq, kmax)
    for n in FIT_SUBSETS.get(arm, ()):
        all_bases[f"O@{n}"] = bases(sig, second_moment(fitq[:n]), kmax)["O"]
    for name, (qa, db) in all_bases.items():
        qa32, db32 = qa.astype(np.float32), db.astype(np.float32)
        cproj = np.empty((len(corpus), kmax), np.float32)
        for s in range(0, len(corpus), 200_000):
            cproj[s : s + 200_000] = corpus[s : s + 200_000] @ db32.T
        qproj = evalq @ qa32.T
        for k in DIMS:
            cand = topk(qproj[:, :k], cproj[:, :k], K_CAND)
            rec["results"][f"{name}-{k}"] = dict(
                hits_single=hits(gt, cand[:, :K_EVAL]).tolist(),
                hits_rerank=hits(gt, rerank10(evalq, corpus, cand)).tolist(),
            )
            r = rec["results"][f"{name}-{k}"]
            print(
                arm,
                name,
                k,
                "recall@10",
                round(float(np.mean(r["hits_single"])) / 10, 4),
                "rerank",
                round(float(np.mean(r["hits_rerank"])) / 10, 4),
                flush=True,
            )
        del cproj
    rec["wall_s"] = round(time.time() - t0, 1)
    with open(os.path.join(d, "hashes.json")) as f:
        rec["data"] = json.load(f)
    try:
        import resource

        rec["peak_rss_gib"] = round(
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20, 2
        )
    except ImportError:  # Windows smoke runs
        rec["peak_rss_gib"] = None
    rec["env"] = dict(
        host=platform.node(), numpy=np.__version__, commit=os.environ.get("TQP_COMMIT")
    )
    with open(path + ".tmp", "w") as f:
        json.dump(rec, f)
    os.replace(path + ".tmp", path)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    print(run(a.arm, a.root, a.out), flush=True)


if __name__ == "__main__":
    main()
