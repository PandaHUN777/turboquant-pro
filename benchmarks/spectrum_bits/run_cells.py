"""The registered cells of docs/PREREG_spectrum_bits.md, and their scoring.

    python run_cells.py gt    --out DIR                 # ground truth + query hashes, once
    python run_cells.py run   --out DIR [--arms ...] [--seeds 0 1 2] [--threads 8]
    python run_cells.py score --out DIR [--markdown RESULTS.md]

Runs on Atlas against the staged data named in the preregistration. A cell whose
result file exists is skipped, so a run can be resumed. Scoring applies the verdict
rules of benchmarks/rabitq_public/score.py, imported rather than restated.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # benchmarks/: rabitq_public.score

WIKI = "/archive/tqp_real/wiki1024"
GLOVE = "/archive/cache/glove-100-angular.hdf5"
SEEDS = (0, 1, 2)
K = 10
RERANK = 5
TRAIN = 100_000
BLOCK = 100_000
NQ = 1000

# the public grid's uniform tq-pro configurations on these dims (section 2)
UNIFORM = {
    "wiki1024-1m": [
        (256, 3),
        (256, 4),
        (512, 3),
        (512, 4),
        (1024, 2),
        (1024, 3),
        (1024, 4),
    ],
    "glove-100-angular": [(100, 2), (100, 3), (100, 4)],
}
DIM = {"wiki1024-1m": 1024, "glove-100-angular": 100}


def uniform_bytes(out_dim: int, bits: int) -> int:
    return -(-out_dim * bits // 8) + 4


def levels(arm: str) -> list[int]:
    return sorted({uniform_bytes(d, b) for d, b in UNIFORM[arm]})


# --------------------------------------------------------------------------- #
# Data                                                                        #
# --------------------------------------------------------------------------- #


class Arm:
    def __init__(self, name: str):
        self.name = name
        self.dim = DIM[name]
        if name == "wiki1024-1m":
            self.n = 1_000_000
            self._corpus = np.load(os.path.join(WIKI, "part_000.npy"), mmap_mode="r")
            self.queries = np.ascontiguousarray(
                np.load(os.path.join(WIKI, "part_001.npy"), mmap_mode="r")[:NQ],
                dtype=np.float32,
            )
            self.provided_gt = None
        else:
            import h5py

            f = h5py.File(GLOVE, "r")
            self._corpus = np.asarray(f["train"], dtype=np.float32)
            self.n = len(self._corpus)
            self.queries = np.asarray(f["test"][:NQ], dtype=np.float32)
            self.provided_gt = np.asarray(f["neighbors"][:NQ, :K], dtype=np.int64)

    def blocks(self):
        for s in range(0, self.n, BLOCK):
            yield s, np.ascontiguousarray(
                self._corpus[s : min(s + BLOCK, self.n)], dtype=np.float32
            )

    def rows(self, idx: np.ndarray) -> np.ndarray:
        return np.ascontiguousarray(self._corpus[np.sort(idx)], dtype=np.float32)[
            np.argsort(np.argsort(idx))
        ]

    def train_sample(self, seed: int) -> np.ndarray:
        rng = np.random.default_rng(seed)
        idx = np.sort(rng.choice(self.n, TRAIN, replace=False))
        return np.ascontiguousarray(self._corpus[idx], dtype=np.float32)

    def query_hash(self) -> str:
        return hashlib.sha256(np.ascontiguousarray(self.queries).tobytes()).hexdigest()

    def exact_gt(self) -> np.ndarray:
        """Exact cosine top-K over the corpus (the 1024-d arm)."""
        q = self.queries / np.linalg.norm(self.queries, axis=1, keepdims=True)
        best_sc = np.full((NQ, 0), -np.inf, np.float32)
        best_ix = np.full((NQ, 0), -1, np.int64)
        for s, blk in self.blocks():
            blk = blk / np.maximum(np.linalg.norm(blk, axis=1, keepdims=True), 1e-30)
            sc = (q @ blk.T).astype(np.float32)
            ix = np.broadcast_to(np.arange(s, s + len(blk)), sc.shape)
            csc = np.concatenate([best_sc, sc], axis=1)
            cix = np.concatenate([best_ix, ix], axis=1)
            part = np.argpartition(-csc, K - 1, axis=1)[:, :K]
            best_sc = np.take_along_axis(csc, part, axis=1)
            best_ix = np.take_along_axis(cix, part, axis=1)
        order = np.argsort(-best_sc, axis=1)
        return np.take_along_axis(best_ix, order, axis=1)


def gt_path(out: str, arm: str) -> str:
    return os.path.join(out, f"gt_{arm}.npz")


def load_gt(out: str, arm: Arm) -> np.ndarray:
    z = np.load(gt_path(out, arm.name))
    if str(z["query_hash"]) != arm.query_hash():
        raise RuntimeError(
            f"MC2: query hash differs from the stored ground truth ({arm.name})"
        )
    return z["gt"]


def cmd_gt(a):
    os.makedirs(a.out, exist_ok=True)
    for name in a.arms:
        arm = Arm(name)
        gt = arm.provided_gt if arm.provided_gt is not None else arm.exact_gt()
        np.savez(gt_path(a.out, name), gt=gt, query_hash=arm.query_hash())
        print(name, "gt", gt.shape, "queries", arm.query_hash()[:12], flush=True)


# --------------------------------------------------------------------------- #
# Cells                                                                       #
# --------------------------------------------------------------------------- #


def cell_id(arm: str, method: str, level: int, seed: int, cfg=None) -> str:
    tag = f"d{cfg[0]}-b{cfg[1]}" if method == "uniform" else "spec"
    return f"{arm}-{method}-{tag}-B{level}-s{seed}"


def cells(arms):
    out = []
    for arm in arms:
        for d, b in UNIFORM[arm]:
            for s in SEEDS:
                out.append(
                    dict(
                        arm=arm,
                        method="uniform",
                        level=uniform_bytes(d, b),
                        cfg=(d, b),
                        seed=s,
                    )
                )
        for lvl in levels(arm):
            for s in SEEDS:
                out.append(
                    dict(arm=arm, method="spectrum", level=lvl, cfg=None, seed=s)
                )
    for c in out:
        c["cell_id"] = cell_id(c["arm"], c["method"], c["level"], c["seed"], c["cfg"])
    return out


def build_index(arm: Arm, c: dict, train: np.ndarray):
    from turboquant_pro import ADCIndex, PCAMatryoshka
    from turboquant_pro.spectrum import expected_distortion, plan_for_bytes

    extra = {}
    if c["method"] == "uniform":
        out_dim, bits = c["cfg"]
        pca = PCAMatryoshka(input_dim=arm.dim, output_dim=out_dim)
        pca.fit(train)
        pipe = pca.with_quantizer(bits=bits, seed=c["seed"])
        eig = np.asarray(pca._all_eigenvalues, dtype=np.float64)
        alloc = np.concatenate([np.full(out_dim, bits), np.zeros(arm.dim - out_dim)])
        extra.update(out_dim=out_dim, schedule=[[out_dim, bits]], nseg=1)
    else:
        full = PCAMatryoshka(input_dim=arm.dim, output_dim=arm.dim)
        full.fit(train)
        eig = np.asarray(full._all_eigenvalues, dtype=np.float64)
        out_dim, schedule = plan_for_bytes(eig, c["level"])
        pca = PCAMatryoshka(input_dim=arm.dim, output_dim=out_dim)
        pca.fit(train)
        pipe = pca.with_weighted_quantizer(bit_schedule=schedule, seed=c["seed"])
        alloc = np.concatenate(
            [
                np.repeat([b for _, b in schedule], [n for n, _ in schedule]),
                np.zeros(arm.dim - out_dim),
            ]
        )
        extra.update(
            out_dim=out_dim, schedule=[list(x) for x in schedule], nseg=len(schedule)
        )
    extra["expected_distortion"] = expected_distortion(
        eig[: arm.dim], alloc.astype(np.int64)
    )
    return ADCIndex(pipe), extra


def run_cell(arm: Arm, c: dict, gt: np.ndarray, threads: int) -> dict:
    t0 = time.perf_counter()
    train = arm.train_sample(c["seed"])
    index, extra = build_index(arm, c, train)
    del train
    for _, blk in arm.blocks():
        index.add(blk)
    build_s = time.perf_counter() - t0
    stored = int(index.stored_bytes_per_row)
    t1 = time.perf_counter()
    ids, _ = index.search(arm.queries, k=K * RERANK)
    search_s = time.perf_counter() - t1
    hits_single = [
        len(set(ids[i, :K].tolist()) & set(gt[i].tolist())) for i in range(NQ)
    ]
    q = arm.queries / np.linalg.norm(arm.queries, axis=1, keepdims=True)
    rr = np.full((NQ, K), -1, np.int64)
    for i in range(NQ):
        cand = ids[i][ids[i] >= 0]
        rows = arm.rows(cand)
        rows = rows / np.maximum(np.linalg.norm(rows, axis=1, keepdims=True), 1e-30)
        rr[i] = cand[np.argsort(-(rows @ q[i]))[:K]]
    hits_rr5 = [len(set(rr[i].tolist()) & set(gt[i].tolist())) for i in range(NQ)]
    return dict(
        cell=dict(c, cfg=list(c["cfg"]) if c["cfg"] else None),
        stored_bytes_per_vec=stored,
        void=stored > c["level"],  # MC1
        n=arm.n,
        nq=NQ,
        hits_single=hits_single,
        hits_rr5=hits_rr5,
        recall10_single=float(np.mean(hits_single)) / K,
        recall10_rr5=float(np.mean(hits_rr5)) / K,
        build_s=round(build_s, 1),
        search_s=round(search_s, 2),
        ms_per_query_top50=round(1000 * search_s / NQ, 2),
        threads=threads,
        kernel=bool(index.uses_kernel),
        index_bytes_per_row=round(index.nbytes / arm.n, 1),
        **extra,
    )


def cmd_run(a):
    import turboquant_pro

    os.makedirs(a.out, exist_ok=True)
    env = dict(
        turboquant_pro=turboquant_pro.__version__,
        commit=os.popen(
            f"git -C {os.path.dirname(os.path.dirname(HERE))} rev-parse --short HEAD"
        )
        .read()
        .strip(),
        threads=a.threads,
    )
    for name in a.arms:
        arm = Arm(name)
        gt = load_gt(a.out, arm)
        todo = [c for c in cells([name]) if c["seed"] in a.seeds]
        for c in todo:
            path = os.path.join(a.out, c["cell_id"] + ".json")
            if os.path.exists(path):
                continue
            print(f"=== {time.strftime('%H:%M:%S')} {c['cell_id']}", flush=True)
            rec = run_cell(arm, c, gt, a.threads)
            rec["env"] = env
            with open(path, "w", encoding="utf-8") as f:
                json.dump(rec, f)
            print(
                f"    stored {rec['stored_bytes_per_vec']} B  out_dim {rec['out_dim']}  "
                f"schedule {rec['schedule']}  single {rec['recall10_single']:.4f}  "
                f"rr5 {rec['recall10_rr5']:.4f}  build {rec['build_s']} s  "
                f"search {rec['search_s']} s  void={rec['void']}",
                flush=True,
            )
    print("RUN DONE", flush=True)


# --------------------------------------------------------------------------- #
# Scoring (docs/PREREG_spectrum_bits.md section 4)                             #
# --------------------------------------------------------------------------- #


def cmd_score(a):
    from rabitq_public.score import paired_ci, verdict

    recs = {}
    for fn in os.listdir(a.out):
        if fn.endswith(".json"):
            with open(os.path.join(a.out, fn), encoding="utf-8") as f:
                r = json.load(f)
            recs[r["cell"]["cell_id"]] = r
    lines = [
        "# Results — bits that follow the spectrum (docs/PREREG_spectrum_bits.md)",
        "",
    ]
    lines.append(
        f"Cells scored: {len(recs)}. Generated by `benchmarks/spectrum_bits/run_cells.py score`."
    )
    lines.append("")
    claims = {}
    for arm in a.arms:
        lines.append(f"## {arm}")
        lines.append("")
        lines.append(
            "| bytes | uniform (d, b) | uniform single | spectrum out_dim / schedule | spectrum bytes | spectrum single | diff [95% CI] | verdict | uniform rr5 | spectrum rr5 |"
        )
        lines.append("|---:|---|---:|---|---:|---:|---|---|---:|---:|")
        counts = {"BEATS": 0, "TIES": 0, "LOSES": 0, "INCONCLUSIVE": 0, "NO-CONFIG": 0}
        for lvl in levels(arm):
            # uniform: the configuration at this level with the higher mean single-pass recall
            best = None
            for d, b in UNIFORM[arm]:
                if uniform_bytes(d, b) != lvl:
                    continue
                ids = [cell_id(arm, "uniform", lvl, s, (d, b)) for s in SEEDS]
                if not all(i in recs for i in ids):
                    continue
                hits = (
                    np.mean(
                        [np.asarray(recs[i]["hits_single"], float) for i in ids], axis=0
                    )
                    / K
                )
                rr5 = (
                    np.mean(
                        [np.asarray(recs[i]["hits_rr5"], float) for i in ids], axis=0
                    )
                    / K
                )
                if best is None or hits.mean() > best[1].mean():
                    best = ((d, b), hits, rr5)
            sids = [cell_id(arm, "spectrum", lvl, s) for s in SEEDS]
            spec = [recs[i] for i in sids if i in recs]
            if best is None or len(spec) < len(SEEDS) or any(r["void"] for r in spec):
                counts["NO-CONFIG"] += 1
                why = (
                    "void (MC1)"
                    if spec and any(r["void"] for r in spec)
                    else "incomplete"
                )
                lines.append(
                    f"| {lvl} | {best[0] if best else '-'} | | {why} | | | | NO-CONFIG | | |"
                )
                continue
            sh = (
                np.mean([np.asarray(r["hits_single"], float) for r in spec], axis=0) / K
            )
            sr = np.mean([np.asarray(r["hits_rr5"], float) for r in spec], axis=0) / K
            m, lo, hi = paired_ci(sh, best[1])
            v = verdict(m, lo, hi)
            counts[v] += 1
            sched = "+".join(f"{n}@{b}" for n, b in spec[0]["schedule"])
            lines.append(
                f"| {lvl} | {best[0]} | {best[1].mean():.4f} | {spec[0]['out_dim']} / {sched} | "
                f"{spec[0]['stored_bytes_per_vec']} | {sh.mean():.4f} | {m:+.4f} [{lo:+.4f}, {hi:+.4f}] | "
                f"**{v}** | {best[2].mean():.4f} | {sr.mean():.4f} |"
            )
        lines.append("")
        n_levels = len(levels(arm))
        if arm == "wiki1024-1m":
            if counts["BEATS"] >= 4 and counts["LOSES"] == 0:
                res = "HOLDS"
            elif counts["LOSES"] >= 2 or counts["BEATS"] == 0:
                res = "REFUTED"
            else:
                res = "MIXED"
            claims["S1"] = (res, counts)
        else:
            res = (
                "HOLDS"
                if counts["LOSES"] == 0 and counts["NO-CONFIG"] < n_levels
                else "REFUTED"
            )
            claims["S2"] = (res, counts)
        lines.append(f"Counts over {n_levels} byte levels: {counts}.")
        lines.append("")
        lines.append("Per cell (MC3: segments and expected distortion):")
        lines.append("")
        lines.append(
            "| cell | stored B | out_dim | schedule | nseg | E[distortion] | single | rr5 | build s | search s (top-50) |"
        )
        lines.append("|---|---:|---:|---|---:|---:|---:|---:|---:|---:|")
        for cid in sorted(i for i in recs if recs[i]["cell"]["arm"] == arm):
            r = recs[cid]
            lines.append(
                f"| {cid} | {r['stored_bytes_per_vec']} | {r['out_dim']} | "
                f"{'+'.join(f'{n}@{b}' for n, b in r['schedule'])} | {r['nseg']} | "
                f"{r['expected_distortion']:.4f} | {r['recall10_single']:.4f} | {r['recall10_rr5']:.4f} | "
                f"{r['build_s']} | {r['search_s']} |"
            )
        lines.append("")
    lines.insert(3, "")
    lines.insert(3, "\n".join(f"- **{k}**: {v[0]} ({v[1]})" for k, v in claims.items()))
    lines.insert(3, "## Claim verdicts (primary endpoint: single-pass recall@10)")
    text = "\n".join(lines) + "\n"
    if a.markdown:
        with open(a.markdown, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    print(text)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("gt", "run", "score"):
        p = sub.add_parser(name)
        p.add_argument("--out", required=True)
        p.add_argument("--arms", nargs="+", default=list(UNIFORM))
        if name == "run":
            p.add_argument("--seeds", nargs="+", type=int, default=list(SEEDS))
            p.add_argument("--threads", type=int, default=8)
        if name == "score":
            p.add_argument("--markdown")
    a = ap.parse_args()
    dict(gt=cmd_gt, run=cmd_run, score=cmd_score)[a.cmd](a)


if __name__ == "__main__":
    main()
