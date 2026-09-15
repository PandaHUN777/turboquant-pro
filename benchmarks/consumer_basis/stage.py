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


def _extract(path, rows, out_path):
    import pyarrow.parquet as pq

    lo, hi = rows
    pf = pq.ParquetFile(path)
    dim = None
    mm, pos, fill = None, 0, 0
    for batch in pf.iter_batches(batch_size=20_000, columns=["emb"]):
        n = batch.num_rows
        if pos + n <= lo:
            pos += n
            continue
        emb = np.stack(batch.column(0).to_numpy(zero_copy_only=False)).astype(
            np.float32
        )
        a, b = max(lo - pos, 0), min(hi - pos, n)
        if mm is None:
            dim = emb.shape[1]
            tmp = out_path + ".tmp.npy"
            mm = np.lib.format.open_memmap(
                tmp, mode="w+", dtype=np.float32, shape=(hi - lo, dim)
            )
        if b > a:
            mm[fill : fill + (b - a)] = emb[a:b]
            fill += b - a
            if fill % 100_000 < (b - a):
                _drop_cache(out_path + ".tmp.npy", mm.flush)
                _drop_cache(path)
        pos += n
        if pos >= hi:
            break
    assert fill == hi - lo, (out_path, fill, hi - lo)
    mm.flush()
    del mm
    os.replace(out_path + ".tmp.npy", out_path)


def payload_sha(path):
    arr = np.load(path, mmap_mode="r")
    h = hashlib.sha256()
    with open(path, "rb") as f:
        f.seek(arr.offset)
        while b := f.read(64 << 20):
            h.update(b)
    return h.hexdigest()


def stage(arm, root):
    from huggingface_hub import hf_hub_download

    out = os.path.join(root, arm)
    os.makedirs(out, exist_ok=True)
    if os.path.exists(os.path.join(out, "DONE")):
        return
    corpus_file, corpus_rows, (fit_file, fit_rows), (eval_file, eval_rows), _ = ARMS[
        arm
    ]
    local = {}
    for f in {corpus_file, fit_file, eval_file}:
        local[f] = hf_hub_download(REPO, f, repo_type="dataset", revision=REVISION)
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
