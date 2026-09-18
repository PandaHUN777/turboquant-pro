# Scoring of 2026-09-18 11:01 to 11:04 UTC (in-pod, 666 result files)

Three runs of `score.py` inside one exempt pod on the campaign volume, each
report as the scorer printed it. Not the final record of
`docs/PREREG_rabitq_public.md`: 18 registered cells were still vetoed by the
sizing guard's peak-to-mean rule (16 PCA+RaBitQ IVF on text-embedding-3-large,
one Wikipedia PQ, one Wikipedia rabitqlib IVF) and their fate is the owner's
decision; the configurations they belong to are listed as incomplete in
`registered.md`.

| family | file | C1 beats RaBitQ | C2 ties OPQ |
|---|---|---|---|
| registered `tq` (kernel at `856c4cb`) | `registered.md` | MIXED: 15 wins, 47 ties, 10 losses of 72 | MIXED: 6, 12, 4 of 22 |
| Amendment 2, `tqfix` (kernel v2) | `tqfix.md` | MIXED: 15, 54, 3 of 72 | HOLDS: 6, 14, 2 of 22 |
| Amendment 3, `tq_ivf` (residual IVF, `5d06ae8`) | `tq_ivf.md` | MIXED: 23, 64, 7 of 94 | HOLDS: 10, 27, 4 of 41 |

The supplementary families replace each `tq` configuration by its twin where
one exists and are reported beside the registered verdicts, never substituted
for them (Amendments 2 and 3).
