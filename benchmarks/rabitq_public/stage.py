"""Stage the registered datasets onto the shared volume, inside a 2 GiB memory budget.

    python -m rabitq_public.stage --data-root /data [--only ann|wiki1024|dbpedia1536|dbpedia3072]

- ann-benchmarks HDF5 files are streamed from ann-benchmarks.com.
- The Hugging Face corpora are rebuilt with the same row order as the Atlas copies made by
  ``generic_download.py`` (parquet files in sorted order, rows in file order, 1M-row parts,
  then ``queries.npy`` from the first 1,000 rows past the cap). Parts are written through a
  memory map in record batches, so memory is one batch rather than a 1M-row buffer.

Resumable: a finished part is never rewritten (write to ``.tmp``, then rename), and a
``DONE`` marker closes each dataset. ``hashes.json`` records the sha256 of every part's
float32 payload, for comparison with the preregistered data identities.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.request

import numpy as np

ANN = ("glove-100-angular", "nytimes-256-angular", "deep-image-96-angular")
HF = {
    # name: (repo, config, column, cap rows, part count, write queries)
    "wiki1024": (
        "CohereLabs/wikipedia-2023-11-embed-multilingual-v3",
        "en",
        "emb",
        10_000_000,
        10,
        False,
    ),
    "dbpedia1536": (
        "KShivendu/dbpedia-entities-openai-1M",
        "data",
        "openai",
        990_000,
        1,
        True,
    ),
    "dbpedia3072": (
        "Qdrant/dbpedia-entities-openai3-text-embedding-3-large-1536-1M",
        "data",
        "text-embedding-3-large-1536-embedding",
        990_000,
        1,
        True,
    ),
}
PART = 1_000_000
QN = 1000


def _retry(fn, what, tries=8):
    for k in range(tries):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            wait = min(300, 10 * 2**k)
            print(f"retry {k + 1}/{tries} {what}: {e!r}; waiting {wait}s", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"gave up: {what}")


def stage_ann(root: str) -> None:
    d = os.path.join(root, "ann")
    os.makedirs(d, exist_ok=True)
    for name in ANN:
        dst = os.path.join(d, f"{name}.hdf5")
        if os.path.exists(dst):
            continue

        def get(name=name, dst=dst):
            # the site answers 403 to urllib's default User-Agent
            req = urllib.request.Request(
                f"http://ann-benchmarks.com/{name}.hdf5",
                headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) tqp-rbq-stage"},
            )
            with urllib.request.urlopen(req, timeout=120) as r:
                with open(dst + ".tmp", "wb") as f:
                    while chunk := r.read(8 << 20):
                        f.write(chunk)
            os.replace(dst + ".tmp", dst)

        _retry(get, name)
        print("staged", dst, os.path.getsize(dst), flush=True)


def payload_sha(path: str) -> str:
    arr = np.load(path, mmap_mode="r")
    h = hashlib.sha256()
    with open(path, "rb") as f:
        f.seek(arr.offset)
        while b := f.read(64 << 20):
            h.update(b)
    return h.hexdigest()


def stage_hf(root: str, name: str) -> None:
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download, list_repo_files

    repo, config, col, cap, nparts, want_q = HF[name]
    out = os.path.join(root, name)
    os.makedirs(out, exist_ok=True)
    if os.path.exists(os.path.join(out, "DONE")):
        return
    files = sorted(
        f
        for f in _retry(lambda: list_repo_files(repo, repo_type="dataset"), "list")
        if f.startswith(f"{config}/") and f.endswith(".parquet")
    )
    done_parts = sum(
        os.path.exists(os.path.join(out, f"part_{i:03d}.npy")) for i in range(nparts)
    )
    skip = done_parts * PART  # rows already banked in finished parts
    total, part, fill, mm = skip, done_parts, 0, None
    queries: list[np.ndarray] = []
    qgot = 0
    for fname in files:
        if total >= cap and (qgot >= QN or not want_q):
            break
        local = _retry(
            lambda f=fname: hf_hub_download(repo, f, repo_type="dataset"), fname
        )
        pf = pq.ParquetFile(local)
        for batch in pf.iter_batches(batch_size=20_000, columns=[col]):
            emb = np.stack(batch.column(0).to_numpy(zero_copy_only=False)).astype(
                np.float32
            )
            i = 0
            if skip > 0:
                adv = min(skip, len(emb))
                skip -= adv
                i = adv
            while i < len(emb):
                if total < cap:
                    if mm is None:
                        rows = min(PART, cap - part * PART)
                        mm = np.lib.format.open_memmap(
                            os.path.join(out, f"part_{part:03d}.tmp.npy"),
                            mode="w+",
                            dtype=np.float32,
                            shape=(rows, emb.shape[1]),
                        )
                    take = min(len(mm) - fill, len(emb) - i)
                    mm[fill : fill + take] = emb[i : i + take]
                    fill += take
                    total += take
                    i += take
                    if fill == len(mm):
                        mm.flush()
                        del mm
                        mm = None
                        tmp = os.path.join(out, f"part_{part:03d}.tmp.npy")
                        os.replace(tmp, os.path.join(out, f"part_{part:03d}.npy"))
                        print(f"{name} part {part} done ({total} rows)", flush=True)
                        part, fill = part + 1, 0
                elif want_q and qgot < QN:
                    take = min(QN - qgot, len(emb) - i)
                    queries.append(emb[i : i + take])
                    qgot += take
                    i += take
                else:
                    break
            if total >= cap and (qgot >= QN or not want_q):
                break
        os.unlink(local)
    if want_q:
        np.save(os.path.join(out, "queries.npy"), np.concatenate(queries)[:QN])
    hashes = {
        f"{name}/part_{i:03d}.npy": payload_sha(os.path.join(out, f"part_{i:03d}.npy"))
        for i in range(nparts)
    }
    if want_q:
        hashes[f"{name}/queries.npy"] = payload_sha(os.path.join(out, "queries.npy"))
    with open(os.path.join(out, "hashes.json"), "w") as f:
        json.dump(hashes, f, indent=1)
    with open(os.path.join(out, "DONE"), "w") as f:
        f.write(f"{total} rows, {part} parts, {qgot} queries\n")
    print(f"{name} DONE", flush=True)


def file_sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while b := f.read(64 << 20):
            h.update(b)
    return h.hexdigest()


def verify(root: str, only: str | None) -> None:
    """Compare staged data with the registered identities; exit non-zero on any mismatch."""
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "DATA_MANIFEST.json"), encoding="utf-8") as f:
        manifest = json.load(f)["files"]
    got = {}
    for name in HF:
        if only in (None, name):
            with open(os.path.join(root, name, "hashes.json"), encoding="utf-8") as f:
                got.update(json.load(f))
    if only in (None, "ann"):
        for n in ANN:
            got[f"ann/{n}.hdf5"] = file_sha(os.path.join(root, "ann", f"{n}.hdf5"))
    bad = [k for k, v in got.items() if manifest[k]["sha256"] != v]
    with open(os.path.join(root, f"VERIFY-{only or 'all'}.json"), "w") as f:
        json.dump(dict(checked=sorted(got), mismatched=bad), f, indent=1)
    if bad:
        raise SystemExit("DATA MISMATCH against DATA_MANIFEST.json: " + ", ".join(bad))
    print(f"VERIFIED {len(got)} files against DATA_MANIFEST.json", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--only", choices=("ann", *HF))
    a = ap.parse_args()
    if a.only in (None, "ann"):
        stage_ann(a.data_root)
    for name in HF:
        if a.only in (None, name):
            stage_hf(a.data_root, name)
    verify(a.data_root, a.only)
    print("STAGE_DONE", flush=True)


if __name__ == "__main__":
    main()
