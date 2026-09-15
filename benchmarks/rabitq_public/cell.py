"""Run one registered cell and write ``<out>/<cell_id>.json`` (+ ``.ids.npz``).

    python -m rabitq_public.cell --cell-id <id> --data-root /data --out /data/results

Every method returns the top-50 corpus positions per query from its compressed search
alone; recall is then scored identically for all methods (docs/PREREG_rabitq_public.md
section 3): single-pass recall@10 from the first 10, and +rerank recall@10 after exact
cosine re-scoring of the first 20 (x2) and first 50 (x5) candidates. A finished cell is
never recomputed; a partial result is never visible (write to a temp name, then rename).
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import tempfile
import threading
import time

import numpy as np

from .datasets import Dataset
from .grid import cells

K = 50
QB = 0  # faiss RaBitQ query bits; 0 = unquantized queries, the most accurate setting


def m_tq(ds, c, threads):
    from turboquant_pro import ADCIndex, PCAMatryoshka

    t = time.perf_counter()
    pca = PCAMatryoshka(input_dim=ds.dim, output_dim=c["out_dim"])
    pca.fit(ds.train_sample(c["seed"], 100_000))
    pipe = pca.with_quantizer(bits=c["bits"], seed=c["seed"])
    index = ADCIndex(pipe)
    # Fill preallocated arrays block by block; ADCIndex.add on the whole stream would
    # re-concatenate its code array once per block.
    codes = np.empty((ds.n, c["out_dim"]), np.uint8)
    cnorm = np.empty(ds.n, np.float32)
    vrnorm = np.empty(ds.n, np.float32)
    for s, blk in ds.blocks():
        part = ADCIndex(pipe).add(blk)
        e = s + len(blk)
        codes[s:e], cnorm[s:e], vrnorm[s:e] = part._codes, part._cnorm, part._vrnorm
    index._codes, index._cnorm, index._vrnorm = codes, cnorm, vrnorm
    build = time.perf_counter() - t
    t = time.perf_counter()
    ids, _ = index.search(ds.queries, k=K)
    search = time.perf_counter() - t
    stored = -(-c["out_dim"] * c["bits"] // 8) + 4
    extra = dict(
        kernel=bool(index.uses_kernel), in_memory_bytes_per_vec=c["out_dim"] + 8
    )
    return np.asarray(ids), stored, build, search, extra


def _faiss(threads):
    import faiss

    faiss.omp_set_num_threads(threads)
    return faiss


def _rabitq_spec(bits):
    return "RaBitQ" if bits == 1 else f"RaBitQ{bits}"


def m_rabitq_flat(ds, c, threads):
    faiss = _faiss(threads)
    t = time.perf_counter()
    index = faiss.index_factory(
        ds.dim, _rabitq_spec(c["bits"]), faiss.METRIC_INNER_PRODUCT
    )
    faiss.downcast_index(index).qb = QB
    index.train(ds.train_sample(c["seed"], 200_000))
    for _, blk in ds.blocks():
        index.add(blk)
    build = time.perf_counter() - t
    t = time.perf_counter()
    _, ids = index.search(ds.queries, K)
    search = time.perf_counter() - t
    rq = faiss.downcast_index(index)
    return ids, int(rq.code_size), build, search, dict(qb=int(rq.qb), metric="ip")


def _ivf_rabitq(faiss, x_train, blocks, queries, dim, c):
    index = faiss.index_factory(
        dim, f"IVF{c['nlist']},{_rabitq_spec(c['bits'])}", faiss.METRIC_L2
    )
    ivf = faiss.extract_index_ivf(index)
    ivf.cp.seed = c["seed"]
    faiss.downcast_index(ivf).qb = QB
    index.train(x_train)
    for blk in blocks:
        index.add(blk)
    ivf.nprobe = c[
        "nlist"
    ]  # exhaustive: every list is scanned, so recall reflects the estimator
    t = time.perf_counter()
    _, ids = index.search(queries, K)
    search = time.perf_counter() - t
    extra = dict(
        nprobe=int(ivf.nprobe), metric="l2", qb=int(faiss.downcast_index(ivf).qb)
    )
    return ids, int(ivf.code_size), search, extra


def m_rabitq_ivf(ds, c, threads):
    faiss = _faiss(threads)
    t = time.perf_counter()
    train = ds.train_sample(c["seed"], 40 * c["nlist"])
    ids, stored, search, extra = _ivf_rabitq(
        faiss, train, (b for _, b in ds.blocks()), ds.queries, ds.dim, c
    )
    build = time.perf_counter() - t - search
    return ids, stored, build, search, extra


def m_pca_rabitq_ivf(ds, c, threads):
    from turboquant_pro import PCAMatryoshka

    faiss = _faiss(threads)
    t = time.perf_counter()
    pca = PCAMatryoshka(input_dim=ds.dim, output_dim=c["out_dim"])
    pca.fit(ds.train_sample(c["seed"], 100_000))

    def proj(x):
        return np.ascontiguousarray(pca.transform(x), dtype=np.float32)

    train = proj(ds.train_sample(c["seed"], 40 * c["nlist"]))
    ids, stored, search, extra = _ivf_rabitq(
        faiss,
        train,
        (proj(b) for _, b in ds.blocks()),
        proj(ds.queries),
        c["out_dim"],
        c,
    )
    build = time.perf_counter() - t - search
    return ids, stored, build, search, extra


def m_rabitqlib_ivf(ds, c, threads):
    import rabitqlib

    faiss = _faiss(threads)
    t = time.perf_counter()
    km = faiss.Kmeans(ds.dim, c["nlist"], niter=20, seed=c["seed"])
    km.train(ds.train_sample(c["seed"], 40 * c["nlist"]))
    quant = faiss.IndexFlatL2(ds.dim)
    quant.add(km.centroids)
    # rabitqlib.build takes the whole float32 corpus. By default that copy is a memory map on
    # scratch storage (reclaimable page cache, not anonymous memory). TQP_RBQ_SCRATCH=ram
    # keeps it in RAM instead: on the 10M x 1024 arm the build reads the map in random order,
    # and over CephFS that left the pod in disk sleep at 3% CPU.
    scratch = os.environ.get("TQP_RBQ_SCRATCH") or tempfile.gettempdir()
    spath = None
    if scratch == "ram":
        data = np.empty((ds.n, ds.dim), np.float32)
    else:
        os.makedirs(scratch, exist_ok=True)
        spath = os.path.join(scratch, f"{c['cell_id']}.corpus.npy")
        data = np.lib.format.open_memmap(
            spath, mode="w+", dtype=np.float32, shape=(ds.n, ds.dim)
        )
    cid = np.empty(ds.n, np.uint32)
    try:
        for s, blk in ds.blocks():
            data[s : s + len(blk)] = blk
            cid[s : s + len(blk)] = quant.search(blk, 1)[1][:, 0]
        if spath:
            data.flush()
        index = rabitqlib.IvfIndex(ds.dim, ds.n, c["nlist"], c["bits"], "l2")
        index.build(
            data,
            np.ascontiguousarray(km.centroids, dtype=np.float32),
            cid,
            threads,
            False,
        )
    finally:
        del data
        if spath:
            os.unlink(spath)
    build = time.perf_counter() - t
    t = time.perf_counter()
    res = index.search(ds.queries, K, c["nlist"], True, threads)
    search = time.perf_counter() - t
    ids = np.asarray(res[0], dtype=np.int64)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "ix.bin")
        index.save(p)
        file_bytes = os.path.getsize(p)
    per_vec = (file_bytes - c["nlist"] * ds.dim * 4) / ds.n
    return (
        ids,
        round(per_vec, 2),
        build,
        search,
        dict(nprobe=c["nlist"], file_bytes=file_bytes),
    )


def m_pq(ds, c, threads, opq=False):
    faiss = _faiss(threads)
    t = time.perf_counter()
    spec = f"OPQ{c['m']},PQ{c['m']}x8" if opq else f"PQ{c['m']}x8"
    index = faiss.index_factory(ds.dim, spec, faiss.METRIC_INNER_PRODUCT)
    base = faiss.downcast_index(index.index if opq else index)
    base.pq.cp.seed = c["seed"]
    index.train(ds.train_sample(c["seed"], 200_000))
    for _, blk in ds.blocks():
        index.add(blk)
    build = time.perf_counter() - t
    t = time.perf_counter()
    _, ids = index.search(ds.queries, K)
    search = time.perf_counter() - t
    return ids, int(c["m"]), build, search, dict(metric="ip")


METHODS = dict(
    tq=m_tq,
    rabitq_flat=m_rabitq_flat,
    rabitq_ivf=m_rabitq_ivf,
    pca_rabitq_ivf=m_pca_rabitq_ivf,
    rabitqlib_ivf=m_rabitqlib_ivf,
    pq=m_pq,
    opq=lambda ds, c, th: m_pq(ds, c, th, opq=True),
)


def hits_at_10(gt: np.ndarray, top: np.ndarray) -> np.ndarray:
    g = gt[:, :10]
    return np.array(
        [len(np.intersect1d(g[i], top[i][top[i] >= 0])) for i in range(len(g))],
        np.uint8,
    )


def rerank(ds: Dataset, ids: np.ndarray, depth: int) -> np.ndarray:
    cand = ids[:, :depth]
    uniq = np.unique(cand[cand >= 0])
    rows = ds.take(uniq)
    out = np.full((len(cand), 10), -1, np.int64)
    for i in range(len(cand)):
        c = cand[i][cand[i] >= 0]
        s = rows[np.searchsorted(uniq, c)] @ ds.queries[i]
        top = c[np.argsort(-s, kind="stable")[:10]]
        out[i, : len(top)] = top
    return out


def _peak_rss_gib():
    if sys.platform == "win32":
        return None
    import resource

    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20, 3)


class AnonPeak:
    """Sample RssAnon from /proc every 0.5 s.

    ru_maxrss counts file pages mapped from the memory-mapped corpus, which the kernel can
    reclaim; anonymous memory is what a pod's memory request has to cover.
    """

    def __init__(self):
        self.peak_kib = 0
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        while not self._stop.is_set():
            try:
                with open("/proc/self/status") as f:
                    for ln in f:
                        if ln.startswith("RssAnon:"):
                            self.peak_kib = max(self.peak_kib, int(ln.split()[1]))
                            break
            except OSError:
                return
            self._stop.wait(0.5)

    def __enter__(self):
        self._t.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._t.join()

    @property
    def gib(self):
        return round(self.peak_kib / 2**20, 3) if self.peak_kib else None


def environment() -> dict:
    from importlib.metadata import PackageNotFoundError, version

    import faiss

    import turboquant_pro

    try:
        rbq = version("rabitqlib")
    except PackageNotFoundError:
        rbq = None
    cpu = platform.processor()
    try:
        with open("/proc/cpuinfo") as f:
            cpu = next(
                ln.split(":", 1)[1].strip() for ln in f if ln.startswith("model name")
            )
    except (OSError, StopIteration):
        pass
    return dict(
        host=platform.node(),
        cpu=cpu,
        python=platform.python_version(),
        numpy=np.__version__,
        faiss=faiss.__version__,
        turboquant_pro=turboquant_pro.__version__,
        rabitqlib=rbq,
        commit=os.environ.get("TQP_COMMIT", "unknown"),
    )


def run(cell: dict, data_root: str, out_dir: str, threads: int) -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{cell['cell_id']}.json")
    if os.path.exists(path):
        return path
    t0 = time.time()
    with AnonPeak() as anon:
        ds = Dataset(cell["dataset"], data_root)
        if ds.gt is None:
            raise SystemExit(f"no ground truth for {cell['dataset']}; run gt.py first")
        ids, stored, build_s, search_s, extra = METHODS[cell["method"]](
            ds, cell, threads
        )
        ids = np.asarray(ids, dtype=np.int64)
        hits = dict(
            hits_single=hits_at_10(ds.gt, ids[:, :10]).tolist(),
            hits_rr2=hits_at_10(ds.gt, rerank(ds, ids, 20)).tolist(),
            hits_rr5=hits_at_10(ds.gt, rerank(ds, ids, 50)).tolist(),
        )
    rec = dict(
        cell=cell,
        n=ds.n,
        dim=ds.dim,
        nq=len(ds.queries),
        stored_bytes_per_vec=stored,
        **hits,
        build_s=round(build_s, 2),
        search_s=round(search_s, 3),
        threads=threads,
        peak_rss_gib=_peak_rss_gib(),
        peak_anon_gib=anon.gib,
        wall_s=round(time.time() - t0, 1),
        extra=extra,
        env=environment(),
        finished=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    for k in ("hits_single", "hits_rr2", "hits_rr5"):
        rec[k.replace("hits", "recall10")] = round(float(np.mean(rec[k])) / 10, 5)
    np.savez_compressed(
        os.path.join(out_dir, f"{cell['cell_id']}.ids.npz"), ids=ids.astype(np.int32)
    )
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rec, f)
    os.replace(tmp, path)
    return path


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--cell-id")
    g.add_argument("--cell-json", help="an unregistered cell, for smoke tests only")
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument(
        "--threads", type=int, default=int(os.environ.get("CELL_THREADS", "4"))
    )
    a = ap.parse_args()
    if a.cell_json:
        cell = json.loads(a.cell_json)
    else:
        cell = next(c for c in cells() if c["cell_id"] == a.cell_id)
    print(run(cell, a.data_root, a.out, a.threads), flush=True)


if __name__ == "__main__":
    main()
