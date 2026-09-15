"""The registered arms: which corpus rows, fit queries and evaluation queries each uses.

All files come from the Hugging Face dataset CohereLabs/beir-embed-english-v3 at revision
REVISION (Cohere embed-english-v3, 1024-d; documents and queries embedded with their own
input types). Row ranges are half-open and taken in file order.
"""

REPO = "CohereLabs/beir-embed-english-v3"
REVISION = "f018922a46a51388348a307ec2fef28019a33026"

# arm: (corpus file, corpus rows, fit (file, rows), eval (file, rows), kind)
ARMS = {
    "msmarco": (
        "msmarco/corpus/0000.parquet",
        (0, 1_000_000),
        ("msmarco/queries/train.parquet", (0, 100_000)),
        ("msmarco/queries/dev.parquet", (0, 6_980)),
        "asymmetric",
    ),
    "hotpotqa": (
        "hotpotqa/corpus/0000.parquet",
        (0, 1_000_000),
        ("hotpotqa/queries/train.parquet", (0, 85_000)),
        ("hotpotqa/queries/test.parquet", (0, 7_405)),
        "asymmetric",
    ),
    "fiqa": (
        "fiqa/corpus/0000.parquet",
        (0, 57_638),
        ("fiqa/queries/train.parquet", (0, 5_500)),
        ("fiqa/queries/test.parquet", (0, 648)),
        "asymmetric-secondary",
    ),
    "nq": (
        "nq/corpus/0000.parquet",
        (0, 1_000_000),
        ("nq/queries/test.parquet", (0, 2_000)),
        ("nq/queries/test.parquet", (2_000, 3_452)),
        "asymmetric-secondary",
    ),
    "quora": (
        "quora/corpus/0000.parquet",
        (0, 522_931),
        ("quora/queries/dev.parquet", (0, 5_000)),
        ("quora/queries/test.parquet", (0, 10_000)),
        "symmetric-secondary",  # 5,000 fit queries in 1024-d: C is noisy, see prereg §2
    ),
    "msmarco-sym": (
        "msmarco/corpus/0000.parquet",
        (0, 900_000),
        ("msmarco/corpus/0000.parquet", (900_000, 950_000)),
        ("msmarco/corpus/0000.parquet", (950_000, 957_000)),
        "symmetric",
    ),
    "hotpotqa-sym": (
        "hotpotqa/corpus/0000.parquet",
        (0, 900_000),
        ("hotpotqa/corpus/0000.parquet", (900_000, 950_000)),
        ("hotpotqa/corpus/0000.parquet", (950_000, 957_000)),
        "symmetric",
    ),
}

# Unscored fit-size curve: basis O refit on the first n fit queries.
FIT_SUBSETS = {"msmarco": (2_000, 10_000)}

BASES = ("P", "Q", "S", "O")
DIMS = (32, 64, 128, 256, 512)
PRIMARY_DIMS = (64, 128, 256)
SIGMA_ROWS = 200_000  # corpus rows used for the corpus second moment
EIG_FLOOR = 1e-6  # relative eigenvalue floor for inverse square roots (basis O)
K_EVAL = 10
K_CAND = 100
