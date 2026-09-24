"""The registered grid of observer-advantage Part II (docs/PREREG_observer_advantage_keys.md).

One source of truth for the runner and the scorer: every arm is an env line for
``tq_paper_lb_shard.py`` / ``wikitext_ppl.py``, every model a (hf id, LongBench key)
pair, every comparison a (arm, reference) pair. Nothing here is fitted.
"""

from __future__ import annotations

# The shipped deployable key recipe (tq_expand.sh / breadth_run.sh), minus the codebook.
SHIPPED = "VAL_BITS=4 GROUP=32 HOT=128 SINK=4 OUTLIER_FRAC=0.02 PREROPE=0"

TIER_A = {  # primary: the attention-keys model card's GQA range
    "llama2-7b-chat-4k": "NousResearch/Llama-2-7b-chat-hf",  # MHA 1:1
    "mistral-7b-instruct": "mistralai/Mistral-7B-Instruct-v0.2",  # GQA 4:1
    "qwen2.5-7b-instruct": "Qwen/Qwen2.5-7B-Instruct",  # GQA 7:1, the fragile case
}
TIER_B = {  # reported: small models, same arms
    "qwen2.5-1.5b-instruct": "Qwen/Qwen2.5-1.5B-Instruct",  # GQA 6:1
    "llama3.2-3b-instruct": "unsloth/Llama-3.2-3B-Instruct",  # GQA 3:1
}
MODELS = {**TIER_A, **TIER_B}
TASKS = ("trec", "triviaqa", "qasper")
G0_TASKS = ("trec",)
PPL = "SEQLEN=2048"  # all chunks of the WikiText-2 test split


def _arm(codebook: str, bits: int, **stages) -> str:
    env = f"NOQUANT=0 CODEBOOK={codebook} KEY_BITS={bits} {SHIPPED}"
    return " ".join([env] + [f"{k}={v}" for k, v in stages.items()])


ARMS: dict[str, str] = {"fp16": "NOQUANT=1"}

# The shipped codebook (4-bit only): every basis, the byte-matched native, a repeat.
ARMS.update(
    {
        "nf4a": _arm("nf4a", 4),
        "nf4a_rep": _arm("nf4a", 4),  # run-to-run floor of the shipped arm
        "nf4a_bm": _arm("nf4a", 4, BYTE_MATCH=1),  # native at a dense basis's bytes
        "nf4a_O": _arm("nf4a", 4, KEY_BASIS="O"),  # REGISTERED O
        "nf4a_Oey": _arm("nf4a", 4, KEY_BASIS="Oey"),
        "nf4a_Ofor": _arm("nf4a", 4, KEY_BASIS="O_foreign"),
        "nf4a_P": _arm("nf4a", 4, KEY_BASIS="P"),
        "nf4a_R": _arm("nf4a", 4, KEY_BASIS="R"),
        "nf4a_H": _arm("nf4a", 4, KEY_BASIS="H"),
        "nf4a_Ocal": _arm("nf4a", 4, KEY_BASIS="O", BASIS_FIT="calib"),
    }
)
# The codebook defined at every width: bases x allocations, at 4, 3 and 2 bits.
for b in (4, 3, 2):
    ARMS.update(
        {
            f"u{b}": _arm("uniform", b),
            f"u{b}_rep": _arm("uniform", b),
            f"u{b}_O": _arm("uniform", b, KEY_BASIS="O"),
            f"u{b}_R": _arm("uniform", b, KEY_BASIS="R"),
            f"u{b}_read": _arm("uniform", b, KEY_ALLOC="read"),  # native channels
            f"u{b}_key": _arm("uniform", b, KEY_ALLOC="key"),
            f"u{b}_O_read": _arm("uniform", b, KEY_BASIS="O", KEY_ALLOC="read"),
        }
    )
# G0: the identity codebook through every basis and the allocation path.
G0_ARMS = {
    f"g0_{b}": _arm("identity", 4, KEY_BASIS=b)
    for b in ("native", "P", "O", "Oey", "O_foreign", "R", "H")
}
G0_ARMS["g0_O_read"] = _arm("identity", 4, KEY_BASIS="O", KEY_ALLOC="read")

# (arm, reference, floor arm): the floor is |mean(floor) - mean(reference)|.
COMPARISONS = {
    "K1": [("nf4a_O", "nf4a_bm", "nf4a_rep")],
    "K1_low": [("u3_O", "u3", "u3_rep")],
    "K2": [("nf4a_O", "nf4a_Ofor", "nf4a_rep")],
    "K3": [("nf4a_O", r, "nf4a_rep") for r in ("nf4a_P", "nf4a_R", "nf4a_H")],
    "K4": [("u3_read", "u3", "u3_rep")],
    "K4b": [("u3_read", "u3_key", "u3_rep")],
}
REPORTED = [
    ("nf4a_O", "nf4a", "nf4a_rep"),
    ("nf4a_Oey", "nf4a_O", "nf4a_rep"),
    ("nf4a_Ocal", "nf4a_O", "nf4a_rep"),
    ("nf4a_bm", "nf4a", "nf4a_rep"),
] + [
    (f"u{b}_{x}", f"u{b}", f"u{b}_rep")
    for b in (4, 3, 2)
    for x in ("O", "R", "read", "key", "O_read")
]
