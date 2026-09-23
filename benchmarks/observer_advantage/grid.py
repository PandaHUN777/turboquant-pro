"""The registered grid (docs/PREREG_observer_advantage.md sections 1, 2 and 4).

A **job** is (arm, transform, family, seed): it loads the arm once, projects it
once, and writes one record per (k, b). A **cell** is one (arm, transform,
family, k, b, seed) record. The EXACT family is exact search in the kept
subspace, one seed, no b: it is gate G0's reproduction and G2's ceiling.
"""

from __future__ import annotations

ARMS_ASYM = ("msmarco", "hotpotqa")  # H1
ARM_SYM = "msmarco-sym"  # H2 control (mismatch 0.0048)
ARMS_H3 = (
    "msmarco",
    "hotpotqa",
    "msmarco-sym",
    "hotpotqa-sym",
    "fiqa",
    "nq",
    "quora",
)
ARMS = ARMS_H3  # every arm that runs

# O is the consumer basis with its singular values split evenly between the query
# and document maps (see cell.balanced_o); Oey is consumer_basis's Eckart-Young
# split, all of them on the document side. Their exact-search scores are
# identical; only a codec can tell them apart. O is scored, Oey is reported.
TRANSFORMS = ("P", "O", "Q", "Oey")
FOREIGN = "Of"  # balanced O from msmarco S and hotpotqa C, run on msmarco only (H4)
FOREIGN_ARM, FOREIGN_C_FROM = "msmarco", "hotpotqa"

FAMILIES = ("TQ", "RBQ", "OPQ")
EXACT = "EXACT"

KS = (64, 128, 256)
BITS = (2, 4)
SEEDS = (0, 1, 2)
KMAX = max(KS)

TRAIN_ROWS = 200_000  # codec training: the first rows of the transformed corpus
K_TOP = 50  # candidates kept per query; single-pass uses the first 10
K_EVAL = 10

H3_CELL = (128, 4)  # (k, b) at which H3 correlates gain with mismatch
SPEARMAN_CRIT = 0.714  # one-sided 5% critical value at n = 7
QUALITY_LEVELS = (0.80, 0.90, 0.95)  # Observer Advantage table, descriptive


def transforms_for(arm: str) -> tuple[str, ...]:
    return TRANSFORMS + ((FOREIGN,) if arm == FOREIGN_ARM else ())


def jobs() -> list[dict]:
    out = []
    for arm in ARMS:
        for t in transforms_for(arm):
            out.append(dict(arm=arm, transform=t, family=EXACT, seed=0))
            for fam in FAMILIES:
                for seed in SEEDS:
                    out.append(dict(arm=arm, transform=t, family=fam, seed=seed))
    for j in out:
        j["job_id"] = f"{j['arm']}-{j['transform']}-{j['family']}-s{j['seed']}"
    return out


def cell_id(arm, transform, family, k, b, seed) -> str:
    bb = "" if b is None else f"-b{b}"
    return f"{arm}-{transform}-{family}-k{k}{bb}-s{seed}"


def job_cells(job: dict) -> list[dict]:
    bits = (None,) if job["family"] == EXACT else BITS
    return [
        dict(
            job,
            k=k,
            b=b,
            cell_id=cell_id(
                job["arm"], job["transform"], job["family"], k, b, job["seed"]
            ),
        )
        for k in KS
        for b in bits
    ]
