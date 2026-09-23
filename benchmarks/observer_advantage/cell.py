"""Run one job and write ``<out>/<cell_id>.json`` for each of its (k, b) cells.

    python -m observer_advantage.cell --job-id msmarco-O-TQ-s0 \
        --root /data/cb --out /data/oa/results --threads 4

``--root`` holds the consumer-basis staging (``<arm>/{corpus,fit,eval}.npy`` and
``hashes.json``). Every vector is L2-normalized, as in consumer_basis. Ground
truth is exact full-dimension inner-product top-10, computed once per arm and
cached under ``<out>/gt``. For a transform with query map A and document map B,
documents enter a codec as ``B x`` (the first k rows of B) and queries search
it as ``A q``; every codec scores inner products in that space, because the
maps of O do not preserve norms. Per evaluation query each cell records

  hits_single  |codec top-10 ∩ true top-10|
  hits_rr5     |top-10 after exact full-dim rescoring of the codec top-50 ∩ true top-10|

Families (docs/PREREG_observer_advantage.md section 2), b bits per kept dim:
  TQ    PCAMatryoshka(k -> k) rotation + Lloyd-Max codes, ADCIndex inner product
  RBQ   faiss RaBitQ{b} flat, inner product, unquantized queries
  OPQ   faiss OPQ{m},PQ{m}x8, m = k b / 8, inner product
  EXACT exact search in the kept subspace (no codec): gate G0's reproduction
Codec training uses the first TRAIN_ROWS transformed corpus rows, so the seed
reaches only a codec's own randomness: TQ's rotation, OPQ's k-means. faiss
RaBitQ flat takes no seed, so its three seeds repeat one computation; the
record says so rather than implying three draws.

A finished cell is never recomputed and a partial one is never visible (write
to a temp name, then rename).
"""

from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np
from consumer_basis.arms import SIGMA_ROWS
from consumer_basis.run import (
    bases,
    hits,
    mat_pow,
    mismatch_index,
    normalize_inplace,
    second_moment,
    topk,
)

from .grid import (
    EXACT,
    FOREIGN,
    FOREIGN_C_FROM,
    K_EVAL,
    K_TOP,
    KMAX,
    TRAIN_ROWS,
    job_cells,
    jobs,
)


def _load(root, arm, name):
    return normalize_inplace(
        np.array(np.load(os.path.join(root, arm, f"{name}.npy")), np.float32)
    )


def _atomic_save(path, write):
    """``write(file)`` into a private temp file, then rename over ``path``. The
    temp name carries the pid, so concurrent jobs of one arm never share it."""
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "wb") as f:
        write(f)
    os.replace(tmp, path)


def ground_truth(root, out, arm, corpus, evalq):
    """Exact full-dimension inner-product top-10, once per arm."""
    os.makedirs(os.path.join(out, "gt"), exist_ok=True)
    path = os.path.join(out, "gt", f"{arm}.npy")
    if not os.path.exists(path):
        gt = topk(evalq, corpus, K_EVAL)
        _atomic_save(path, lambda f: np.save(f, gt))
    return np.load(path)


def balanced_o(sig, cq, kmax):
    """Basis O with its singular values split evenly between the two maps.

    consumer_basis's O is queries ``(C^-1/2 U_k)^T`` and documents
    ``L_k V_k^T S^-1/2``, with ``C^1/2 S^1/2 = U L V^T``. Any diagonal D moved
    from one map to the other leaves every score ``(A q).(B x)`` unchanged, so
    exact search cannot see the split; a codec, which quantizes ``B x`` only, can.
    For a codec that rotates and spends its bits evenly (TQ, RaBitQ), score error
    grows with ``E||B x||^2 * E||A q||^2``: ``k * sum(l^2)`` for that split and
    ``(sum l)^2`` for ``L^1/2`` on each side, the minimum over diagonal splits by
    Cauchy-Schwarz. The balanced maps also reduce to corpus PCA, as maps and up to
    a scalar, when C is proportional to S, which is the premise of the symmetric
    control; the Eckart-Young split reduces to it only in its scores.
    """
    qa, db = bases(sig, cq, kmax)["O"]
    lam = np.linalg.svd(mat_pow(cq, 0.5) @ mat_pow(sig, 0.5), compute_uv=False)
    r = np.sqrt(lam[:kmax])[:, None]
    return r * qa, db / r


def transform_maps(root, arm, transform, corpus, fitq):
    """(query_map, doc_map), each (KMAX, d) float32, and the arm's mismatch index."""
    sig = second_moment(corpus[:SIGMA_ROWS])
    cq = second_moment(fitq)
    if transform == FOREIGN:
        qa, db = balanced_o(
            sig, second_moment(_load(root, FOREIGN_C_FROM, "fit")), KMAX
        )
    elif transform == "O":
        qa, db = balanced_o(sig, cq, KMAX)
    elif transform == "Oey":
        qa, db = bases(sig, cq, KMAX)["O"]
    else:
        qa, db = bases(sig, cq, KMAX)[transform]
    return qa.astype(np.float32), db.astype(np.float32), mismatch_index(sig, cq)


def rr5(evalq, corpus, ids):
    """Top-10 after exact full-dimension rescoring of each query's first 50."""
    out = np.full((len(ids), K_EVAL), -1, np.int64)
    for i in range(len(ids)):
        c = ids[i, :K_TOP]
        c = c[c >= 0]
        s = corpus[c] @ evalq[i]
        top = c[np.argsort(-s, kind="stable")[:K_EVAL]]
        out[i, : len(top)] = top
    return out


# --------------------------------------------------------------------------- #
# Families: each returns (top-50 ids, stored bytes/vector, shared bytes, extra) #
# --------------------------------------------------------------------------- #


def f_tq(ck, qk, k, b, seed, threads):
    from turboquant_pro import ADCIndex, PCAMatryoshka

    pca = PCAMatryoshka(input_dim=k, output_dim=k)
    pca.fit(ck[:TRAIN_ROWS])
    pipe = pca.with_quantizer(bits=b, seed=seed)
    index = ADCIndex(pipe, metric="inner_product").add(ck)
    ids, _ = index.search(qk, k=K_TOP)
    shared = 4 * (k * k + k + len(index._cent))  # PCA basis, mean, centroid table
    extra = dict(scan="kernel" if index._kernel_scan() else "numpy", seeded=True)
    return ids, index.stored_bytes_per_row, shared, extra


def f_rbq(ck, qk, k, b, seed, threads):
    import faiss
    from rabitq_public.cell import QB, _faiss, _rabitq_spec

    _faiss(threads)
    index = faiss.index_factory(k, _rabitq_spec(b), faiss.METRIC_INNER_PRODUCT)
    faiss.downcast_index(index).qb = QB
    index.train(ck[:TRAIN_ROWS])
    index.add(ck)
    _, ids = index.search(qk, K_TOP)
    rq = faiss.downcast_index(index)
    extra = dict(scan="faiss", qb=int(rq.qb), seeded=False)
    return ids, int(rq.code_size), 4 * k, extra  # shared: the centroid


def f_opq(ck, qk, k, b, seed, threads):
    import faiss
    from rabitq_public.cell import _faiss

    _faiss(threads)
    m = k * b // 8
    index = faiss.index_factory(k, f"OPQ{m},PQ{m}x8", faiss.METRIC_INNER_PRODUCT)
    faiss.downcast_index(index.index).pq.cp.seed = seed
    index.train(ck[:TRAIN_ROWS])
    index.add(ck)
    _, ids = index.search(qk, K_TOP)
    shared = 4 * (256 * k + k * k)  # PQ codebooks, OPQ rotation
    return ids, m, shared, dict(scan="faiss", m=m, seeded=True)


FAMILIES = dict(TQ=f_tq, RBQ=f_rbq, OPQ=f_opq)


# --------------------------------------------------------------------------- #


def environment():
    from rabitq_public.cell import environment as env

    try:
        return env()
    except ImportError:  # no faiss: the TQ and EXACT families still run
        import platform

        import turboquant_pro

        return dict(
            host=platform.node(),
            python=platform.python_version(),
            numpy=np.__version__,
            turboquant_pro=turboquant_pro.__version__,
            commit=os.environ.get("TQP_COMMIT", "unknown"),
        )


def run(job: dict, root: str, out: str, threads: int) -> list[str]:
    os.makedirs(out, exist_ok=True)
    cells = job_cells(job)
    paths = [os.path.join(out, f"{c['cell_id']}.json") for c in cells]
    if all(os.path.exists(p) for p in paths):
        return paths
    arm = job["arm"]
    corpus, fitq, evalq = (_load(root, arm, n) for n in ("corpus", "fit", "eval"))
    gt = ground_truth(root, out, arm, corpus, evalq)
    qa, db, mismatch = transform_maps(root, arm, job["transform"], corpus, fitq)
    cproj = np.empty((len(corpus), KMAX), np.float32)
    for s in range(0, len(corpus), 200_000):
        cproj[s : s + 200_000] = corpus[s : s + 200_000] @ db.T
    qproj = evalq @ qa.T
    with open(os.path.join(root, arm, "hashes.json")) as f:
        data = json.load(f)
    env = environment()
    for c, path in zip(cells, paths):
        if os.path.exists(path):
            continue
        k, b = c["k"], c["b"]
        ck = np.ascontiguousarray(cproj[:, :k])
        qk = np.ascontiguousarray(qproj[:, :k])
        t0 = time.perf_counter()
        if c["family"] == EXACT:
            ids = topk(qk, ck, K_TOP)
            stored, shared, extra = None, 0, dict(scan="exact")  # no codes
        else:
            ids, stored, shared, extra = FAMILIES[c["family"]](
                ck, qk, k, b, c["seed"], threads
            )
        wall = time.perf_counter() - t0
        ids = np.asarray(ids, np.int64)
        rec = dict(
            cell=c,
            mismatch_index=round(mismatch, 6),
            corpus_rows=len(corpus),
            eval_rows=len(evalq),
            stored_bytes_per_vec=stored,
            shared_bytes=shared,
            basis_bytes=int(qa[:k].nbytes * (1 if np.array_equal(qa, db) else 2)),
            hits_single=hits(gt, ids[:, :K_EVAL]).tolist(),
            hits_rr5=hits(gt, rr5(evalq, corpus, ids)).tolist(),
            build_and_search_s=round(wall, 2),
            threads=threads,
            extra=extra,
            data=data,
            env=env,
            finished=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
        for key in ("hits_single", "hits_rr5"):
            rec[key.replace("hits", "recall10")] = round(
                float(np.mean(rec[key])) / 10, 5
            )
        _atomic_save(path, lambda f, r=rec: f.write(json.dumps(r).encode()))
        print(c["cell_id"], rec["recall10_single"], rec["recall10_rr5"], flush=True)
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-id", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=4)
    a = ap.parse_args()
    by_id = {j["job_id"]: j for j in jobs()}
    if a.job_id not in by_id:
        raise SystemExit(f"unknown job {a.job_id!r}")
    for p in run(by_id[a.job_id], a.root, a.out, a.threads):
        print(p, flush=True)


if __name__ == "__main__":
    main()
