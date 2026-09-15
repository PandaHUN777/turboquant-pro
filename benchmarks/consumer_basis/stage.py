"""Stage one arm's corpus, fit queries and eval queries as float32 .npy (2 GiB budget).

    python -m consumer_basis.stage --arm msmarco --root /data/cb

Parquet row groups are streamed into memory maps, so memory is one batch. Writes
corpus.npy, fit.npy, eval.npy and hashes.json (sha256 of each float32 payload) under
<root>/<arm>/, and a DONE marker. The msmarco and msmarco-sym arms share one download.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os

import numpy as np

from .arms import ARMS, REPO, REVISION


def _drop_cache(path, flush=None):
    """fsync and evict a file's page cache. Inside a 2 GiB cgroup the page cache of a
    multi-GiB memory map is charged to the pod, and dirty pages OOM-killed the 1M-row
    staging jobs (same finding as benchmarks/fleet/fleet_common.drop_page_cache)."""
    if flush is not None:
        flush()
    if not hasattr(os, "posix_fadvise"):
        return
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
        os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
    finally:
        os.close(fd)


def _download(repo_file, cache_dir, chunk=8 << 20, evict_every=256 << 20):
    """Stream one dataset file to local disk, evicting its page cache as it goes.

    huggingface_hub's client left gigabytes of dirty page cache charged to the 2 GiB pod
    and the 1M-row arms were OOM-killed during download; this writer fsyncs and drops the
    cache every ``evict_every`` bytes and resumes with an HTTP Range request on retry.
    """
    import time
    import urllib.request

    from huggingface_hub import hf_hub_url

    url = hf_hub_url(REPO, repo_file, repo_type="dataset", revision=REVISION)
    dst = os.path.join(cache_dir, repo_file.replace("/", "__"))
    os.makedirs(cache_dir, exist_ok=True)
    if os.path.exists(dst):
        return dst
    part = dst + ".part"
    for attempt in range(8):
        have = os.path.getsize(part) if os.path.exists(part) else 0
        req = urllib.request.Request(url, headers={"User-Agent": "tqp-consumer-basis"})
        if have:
            req.add_header("Range", f"bytes={have}-")
        try:
            with urllib.request.urlopen(req, timeout=120) as r, open(part, "ab") as f:
                since = 0
                while block := r.read(chunk):
                    f.write(block)
                    since += len(block)
                    if since >= evict_every:
                        f.flush()
                        _drop_cache(part)
                        since = 0
            _drop_cache(part)
            os.replace(part, dst)
            return dst
        except Exception as e:  # noqa: BLE001
            wait = min(300, 10 * 2**attempt)
            print(f"retry {attempt + 1} {repo_file}: {e!r}; {wait}s", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"download failed: {repo_file}")


def _extract(path, rows, out_path):
    import pyarrow.parquet as pq

    # Plain buffered writes, not a memory map: pages written through a map stay mapped, so
    # fadvise cannot evict them, and on CephFS their writeback lagged until the 2 GiB pod was
    # OOM-killed (pyarrow's own memory stayed near 390 MiB, measured). Here dirty memory is
    # bounded by fsync + eviction every EVICT_ROWS rows.
    evict_rows = 50_000
    lo, hi = rows
    pf = pq.ParquetFile(path)
    tmp = out_path + ".tmp.npy"
    f = None
    pos, fill, since = 0, 0, 0
    try:
        for batch in pf.iter_batches(batch_size=20_000, columns=["emb"]):
            n = batch.num_rows
            if pos + n <= lo:
                pos += n
                continue
            emb = np.stack(batch.column(0).to_numpy(zero_copy_only=False)).astype(
                np.float32
            )
            a, b = max(lo - pos, 0), min(hi - pos, n)
            if f is None:
                f = open(tmp, "wb")
                header = {
                    "descr": np.lib.format.dtype_to_descr(np.dtype(np.float32)),
                    "fortran_order": False,
                    "shape": (hi - lo, emb.shape[1]),
                }
                np.lib.format.write_array_header_1_0(f, header)
            if b > a:
                f.write(np.ascontiguousarray(emb[a:b]).tobytes())
                fill += b - a
                since += b - a
                if since >= evict_rows:
                    f.flush()
                    _drop_cache(tmp)
                    _drop_cache(path)
                    since = 0
            pos += n
            if pos >= hi:
                break
    finally:
        if f is not None:
            f.close()
    assert fill == hi - lo, (out_path, fill, hi - lo)
    _drop_cache(tmp)
    arr = np.load(tmp, mmap_mode="r")
    assert arr.shape[0] == hi - lo, (tmp, arr.shape)
    del arr
    os.replace(tmp, out_path)


def payload_sha(path):
    arr = np.load(path, mmap_mode="r")
    h = hashlib.sha256()
    with open(path, "rb") as f:
        f.seek(arr.offset)
        while b := f.read(64 << 20):
            h.update(b)
    return h.hexdigest()


def stage(arm, root):
    out = os.path.join(root, arm)
    os.makedirs(out, exist_ok=True)
    if os.path.exists(os.path.join(out, "DONE")):
        return
    corpus_file, corpus_rows, (fit_file, fit_rows), (eval_file, eval_rows), _ = ARMS[
        arm
    ]
    cache = os.environ.get("CB_DOWNLOAD_DIR", "/tmp/cbdl")
    local = {f: _download(f, cache) for f in sorted({corpus_file, fit_file, eval_file})}
    for name, (f, rows) in (
        ("corpus", (corpus_file, corpus_rows)),
        ("fit", (fit_file, fit_rows)),
        ("eval", (eval_file, eval_rows)),
    ):
        p = os.path.join(out, f"{name}.npy")
        if not os.path.exists(p):
            _extract(local[f], rows, p)
        print(arm, name, np.load(p, mmap_mode="r").shape, flush=True)
    hashes = {
        n: payload_sha(os.path.join(out, f"{n}.npy")) for n in ("corpus", "fit", "eval")
    }
    with open(os.path.join(out, "hashes.json"), "w") as f:
        json.dump(dict(repo=REPO, revision=REVISION, sha256=hashes), f, indent=1)
    with open(os.path.join(out, "DONE"), "w") as f:
        f.write("ok\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, nargs="+")
    ap.add_argument("--root", required=True)
    a = ap.parse_args()
    for arm in a.arm:
        stage(arm, a.root)
    print("STAGE_DONE", flush=True)


if __name__ == "__main__":
    main()
