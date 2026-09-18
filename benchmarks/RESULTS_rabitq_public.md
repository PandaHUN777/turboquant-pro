# RaBitQ on public data: the preregistered comparison, scored (committed as executed)

The claim under test was the README's *beats RaBitQ on recall, ties OPQ at matched bytes*, registered in `docs/PREREG_rabitq_public.md` before any cell ran and scored by `benchmarks/rabitq_public/score.py` at the registration commit. Six public arms, three seeds, all methods at matched stored bytes with the same 5x oversample and exact rerank (rr5, the primary endpoint). Cells ran on NRP through the campaign harness; the scorer ran inside one pod on the campaign volume (`scoring/2026-09-18T1115/`), and every number below is read from the reports it printed. Registered verdicts first; the two supplementary families of Amendments 2 and 3 are reported beside them and never substituted (section 5 of the preregistration).

**Registered verdicts: C1 beats RaBitQ MIXED, C2 ties OPQ MIXED.** C1: 15 BEATS, 47 TIES, 10 LOSES of 72 scored pairs, 47 byte gaps. C2: 6, 12, 4 of 22, 19 gaps. By the section 5 rule for MIXED, the ledger row `embedding_beats_rabitq_ties_opq` becomes `reproducible` with its text rewritten to where the claim holds, and the unscoped phrase leaves the README and the claim tables.

## What was run

519 of 540 registered cells finished. 21 never ran and are recorded as not run (Amendment 4): eighteen refused by the sizing guard's peak-to-mean rule, three parked under it and not resubmitted. Nothing was imputed. A configuration is scored only with all three seeds, so the configurations below are absent from every family:

- dbpedia-3large-1536-1m dbpedia-3large-1536-1m-pca_rabitq_ivf-d384-b1-n4096: seeds [0] (excluded, seeds short)
- dbpedia-3large-1536-1m dbpedia-3large-1536-1m-pca_rabitq_ivf-d768-b3-n4096: seeds [0] (excluded, seeds short)
- wiki1024-10m wiki1024-10m-pq-m128: seeds [0, 2] (excluded, seeds short)
- wiki1024-10m wiki1024-10m-rabitqlib_ivf-b4-n16384: seeds [0] (excluded, seeds short)
- wiki1024-10m wiki1024-10m-rabitqlib_ivf-b5-n16384: seeds [0] (excluded, seeds short)
- dbpedia-3large-1536-1m-pca_rabitq_ivf-d384-b2-n4096: no seed ran
- dbpedia-3large-1536-1m-pca_rabitq_ivf-d384-b3-n4096: no seed ran
- dbpedia-3large-1536-1m-pca_rabitq_ivf-d768-b1-n4096: no seed ran
- dbpedia-3large-1536-1m-pca_rabitq_ivf-d768-b2-n4096: no seed ran

The 21 cells:

- `dbpedia-3large-1536-1m-pca_rabitq_ivf-d384-b1-n4096-s1`
- `dbpedia-3large-1536-1m-pca_rabitq_ivf-d384-b1-n4096-s2`
- `dbpedia-3large-1536-1m-pca_rabitq_ivf-d384-b2-n4096-s0`
- `dbpedia-3large-1536-1m-pca_rabitq_ivf-d384-b2-n4096-s1`
- `dbpedia-3large-1536-1m-pca_rabitq_ivf-d384-b2-n4096-s2`
- `dbpedia-3large-1536-1m-pca_rabitq_ivf-d384-b3-n4096-s0`
- `dbpedia-3large-1536-1m-pca_rabitq_ivf-d384-b3-n4096-s1`
- `dbpedia-3large-1536-1m-pca_rabitq_ivf-d384-b3-n4096-s2`
- `dbpedia-3large-1536-1m-pca_rabitq_ivf-d768-b1-n4096-s0`
- `dbpedia-3large-1536-1m-pca_rabitq_ivf-d768-b1-n4096-s1`
- `dbpedia-3large-1536-1m-pca_rabitq_ivf-d768-b1-n4096-s2`
- `dbpedia-3large-1536-1m-pca_rabitq_ivf-d768-b2-n4096-s0`
- `dbpedia-3large-1536-1m-pca_rabitq_ivf-d768-b2-n4096-s1`
- `dbpedia-3large-1536-1m-pca_rabitq_ivf-d768-b2-n4096-s2`
- `dbpedia-3large-1536-1m-pca_rabitq_ivf-d768-b3-n4096-s1`
- `dbpedia-3large-1536-1m-pca_rabitq_ivf-d768-b3-n4096-s2`
- `wiki1024-10m-pq-m128-s1`
- `wiki1024-10m-rabitqlib_ivf-b4-n16384-s1`
- `wiki1024-10m-rabitqlib_ivf-b4-n16384-s2`
- `wiki1024-10m-rabitqlib_ivf-b5-n16384-s1`
- `wiki1024-10m-rabitqlib_ivf-b5-n16384-s2`

## Claim verdicts by family

| family | C1 beats RaBitQ | BEATS / TIES / LOSES / INCONCLUSIVE (n, gaps) | C2 ties OPQ | BEATS / TIES / LOSES / INCONCLUSIVE (n, gaps) |
|---|---|---|---|---|
| registered `tq` | **MIXED** | 15 / 47 / 10 / 0 (72, 47) | **MIXED** | 6 / 12 / 4 / 0 (22, 19) |
| `tqfix` (Amendment 2) | **MIXED** | 15 / 54 / 3 / 0 (72, 47) | **HOLDS** | 6 / 14 / 2 / 0 (22, 19) |
| `tq_ivf` (Amendment 3) | **MIXED** | 23 / 64 / 7 / 0 (94, 55) | **HOLDS** | 10 / 27 / 4 / 0 (41, 30) |

## Per-arm counts at rr5 (BEATS / TIES / LOSES / INCONCLUSIVE), description not test

Against the RABITQ family:

| arm | registered `tq` | `tqfix` (Amendment 2) | `tq_ivf` (Amendment 3) |
|---|---|---|---|
| glove-100-angular | 7 / 1 / 0 / 0 | 7 / 1 / 0 / 0 | 9 / 1 / 0 / 0 |
| deep-image-96-angular | 6 / 2 / 0 / 0 | 6 / 2 / 0 / 0 | 9 / 1 / 0 / 0 |
| nytimes-256-angular | 1 / 9 / 0 / 0 | 1 / 9 / 0 / 0 | 3 / 9 / 0 / 0 |
| dbpedia-ada002-1m | 0 / 16 / 0 / 0 | 0 / 16 / 0 / 0 | 0 / 21 / 0 / 0 |
| dbpedia-3large-1536-1m | 0 / 6 / 7 / 0 | 0 / 13 / 0 / 0 | 0 / 15 / 3 / 0 |
| wiki1024-10m | 1 / 13 / 3 / 0 | 1 / 13 / 3 / 0 | 2 / 17 / 4 / 0 |

Against the OPQ family:

| arm | registered `tq` | `tqfix` (Amendment 2) | `tq_ivf` (Amendment 3) |
|---|---|---|---|
| glove-100-angular | 1 / 1 / 1 / 0 | 1 / 1 / 1 / 0 | 2 / 3 / 0 / 0 |
| deep-image-96-angular | 5 / 0 / 0 / 0 | 5 / 0 / 0 / 0 | 8 / 0 / 0 / 0 |
| nytimes-256-angular | 0 / 2 / 0 / 0 | 0 / 2 / 0 / 0 | 0 / 4 / 0 / 0 |
| dbpedia-ada002-1m | 0 / 4 / 0 / 0 | 0 / 4 / 0 / 0 | 0 / 8 / 0 / 0 |
| dbpedia-3large-1536-1m | 0 / 2 / 2 / 0 | 0 / 4 / 0 / 0 | 0 / 6 / 2 / 0 |
| wiki1024-10m | 0 / 3 / 1 / 0 | 0 / 3 / 1 / 0 | 0 / 6 / 2 / 0 |

## Where the registered family wins and loses (rr5, vs RaBitQ)

BEATS:

| arm | tq-pro configuration | B | matched RaBitQ | B | tq | RaBitQ | diff [95% CI] |
|---|---|---:|---|---:|---:|---:|---|
| deep-image-96-angular | `deep-image-96-angular-tq-d96-b3` | 40 | `deep-image-96-angular-rabitq_flat-b2` | 44 | 0.9823 | 0.8614 | +0.1208 [+0.1150, +0.1267] |
| deep-image-96-angular | `deep-image-96-angular-tq-d96-b4` | 52 | `deep-image-96-angular-rabitq_flat-b3` | 56 | 0.9991 | 0.9845 | +0.0146 [+0.0126, +0.0168] |
| deep-image-96-angular | `deep-image-96-angular-tq-d96-b2` | 28 | `deep-image-96-angular-rabitqlib_ivf-b1-n16384` | 32.94 | 0.8634 | 0.8489 | +0.0144 [+0.0086, +0.0202] |
| deep-image-96-angular | `deep-image-96-angular-tq-d96-b4` | 52 | `deep-image-96-angular-rabitqlib_ivf-b2-n16384` | 56.94 | 0.9991 | 0.9919 | +0.0072 [+0.0062, +0.0082] |
| deep-image-96-angular | `deep-image-96-angular-tq-d96-b3` | 40 | `deep-image-96-angular-rabitqlib_ivf-b1-n16384` | 32.94 | 0.9823 | 0.8489 | +0.1334 [+0.1282, +0.1386] |
| deep-image-96-angular | `deep-image-96-angular-tq-d96-b4` | 52 | `deep-image-96-angular-rabitq_ivf-b2-n16384` | 44 | 0.9991 | 0.9785 | +0.0206 [+0.0188, +0.0223] |
| glove-100-angular | `glove-100-angular-tq-d100-b3` | 42 | `glove-100-angular-rabitq_flat-b2` | 46 | 0.9877 | 0.8939 | +0.0939 [+0.0887, +0.0990] |
| glove-100-angular | `glove-100-angular-tq-d100-b4` | 54 | `glove-100-angular-rabitq_flat-b3` | 58 | 1.0000 | 0.9939 | +0.0061 [+0.0050, +0.0072] |
| glove-100-angular | `glove-100-angular-tq-d100-b3` | 42 | `glove-100-angular-rabitq_ivf-b2-n4096` | 46 | 0.9877 | 0.9379 | +0.0499 [+0.0466, +0.0532] |
| glove-100-angular | `glove-100-angular-tq-d100-b2` | 29 | `glove-100-angular-rabitqlib_ivf-b1-n4096` | 33.99 | 0.9058 | 0.7298 | +0.1760 [+0.1694, +0.1827] |
| glove-100-angular | `glove-100-angular-tq-d100-b4` | 54 | `glove-100-angular-rabitqlib_ivf-b2-n4096` | 57.99 | 1.0000 | 0.9659 | +0.0340 [+0.0316, +0.0365] |
| glove-100-angular | `glove-100-angular-tq-d100-b3` | 42 | `glove-100-angular-rabitqlib_ivf-b1-n4096` | 33.99 | 0.9877 | 0.7298 | +0.2580 [+0.2492, +0.2666] |
| glove-100-angular | `glove-100-angular-tq-d100-b4` | 54 | `glove-100-angular-rabitq_ivf-b2-n4096` | 46 | 1.0000 | 0.9379 | +0.0621 [+0.0584, +0.0659] |
| nytimes-256-angular | `nytimes-256-angular-tq-d256-b3` | 100 | `nytimes-256-angular-rabitqlib_ivf-b2-n2048` | 92.9 | 0.9819 | 0.9677 | +0.0142 [+0.0123, +0.0162] |
| wiki1024-10m | `wiki1024-10m-tq-d256-b3` | 100 | `wiki1024-10m-pca_rabitq_ivf-d256-b2-n16384` | 84 | 0.9793 | 0.9663 | +0.0130 [+0.0104, +0.0156] |

LOSES:

| arm | tq-pro configuration | B | matched RaBitQ | B | tq | RaBitQ | diff [95% CI] |
|---|---|---:|---|---:|---:|---:|---|
| dbpedia-3large-1536-1m | `dbpedia-3large-1536-1m-tq-d1536-b3` | 580 | `dbpedia-3large-1536-1m-rabitq_flat-b3` | 596 | 0.8625 | 1.0000 | -0.1375 [-0.1501, -0.1254] |
| dbpedia-3large-1536-1m | `dbpedia-3large-1536-1m-tq-d1536-b4` | 772 | `dbpedia-3large-1536-1m-rabitq_flat-b4` | 788 | 0.9642 | 1.0000 | -0.0358 [-0.0418, -0.0300] |
| dbpedia-3large-1536-1m | `dbpedia-3large-1536-1m-tq-d1536-b3` | 580 | `dbpedia-3large-1536-1m-rabitq_ivf-b3-n4096` | 596 | 0.8625 | 1.0000 | -0.1375 [-0.1501, -0.1254] |
| dbpedia-3large-1536-1m | `dbpedia-3large-1536-1m-tq-d1536-b4` | 772 | `dbpedia-3large-1536-1m-rabitq_ivf-b4-n4096` | 788 | 0.9642 | 1.0000 | -0.0358 [-0.0418, -0.0300] |
| dbpedia-3large-1536-1m | `dbpedia-3large-1536-1m-tq-d1536-b3` | 580 | `dbpedia-3large-1536-1m-rabitqlib_ivf-b3-n4096` | 613.24 | 0.8625 | 1.0000 | -0.1375 [-0.1501, -0.1254] |
| dbpedia-3large-1536-1m | `dbpedia-3large-1536-1m-tq-d1536-b4` | 772 | `dbpedia-3large-1536-1m-rabitqlib_ivf-b4-n4096` | 805.24 | 0.9642 | 1.0000 | -0.0358 [-0.0418, -0.0300] |
| dbpedia-3large-1536-1m | `dbpedia-3large-1536-1m-tq-d1536-b2` | 388 | `dbpedia-3large-1536-1m-rabitq_ivf-b2-n4096` | 404 | 0.7850 | 1.0000 | -0.2150 [-0.2304, -0.2003] |
| wiki1024-10m | `wiki1024-10m-tq-d256-b4` | 132 | `wiki1024-10m-pca_rabitq_ivf-d512-b2-n16384` | 148 | 0.9851 | 0.9974 | -0.0123 [-0.0152, -0.0097] |
| wiki1024-10m | `wiki1024-10m-tq-d256-b4` | 132 | `wiki1024-10m-rabitq_ivf-b1-n16384` | 136 | 0.9851 | 0.9952 | -0.0101 [-0.0130, -0.0074] |
| wiki1024-10m | `wiki1024-10m-tq-d256-b4` | 132 | `wiki1024-10m-rabitqlib_ivf-b1-n16384` | 147.57 | 0.9851 | 0.9975 | -0.0124 [-0.0152, -0.0097] |

## Reading

- At the low-byte end on the two low-dimensional arms (GloVe-100 at 29 to 54 bytes, deep-image-96 at 28 to 52 bytes) tq-pro beats every RaBitQ variant at matched bytes, by 0.006 to 0.26 in recall@10 after rerank. NYTimes-256, ada-002 and most of Wikipedia-1024 tie: both sides sit at or near recall 1.0 after a 5x rerank, which the preregistration said to expect.
- The registered family loses in two places. On text-embedding-3-large at full dimension (1536-d, 388 to 772 bytes) it loses by 0.036 to 0.215: those cells ran the kernel that wrapped its sums past 257 dims (fixed in `3d96506`; Amendment 2), and the `tqfix` family, same pipeline on the fixed kernel, ties every one of them. That is a defect finding, not a method finding, and it is scored as registered. On Wikipedia at 132 bytes (PCA-256, 4 bits) it loses to three 1-bit-per-dimension RaBitQ IVF configurations by 0.010 to 0.012, on the fixed kernel too.
- Against OPQ the registered family ties or wins everywhere except the wrapped full-dimension cells, that same 132-byte Wikipedia point, and one GloVe point at 42 bytes (0.9877 against 0.9992). `tqfix` and `tq_ivf` reach HOLDS on C2.
- `tq_ivf`, tq-pro's own IVF with residual coding, adds 22 scored pairs and wins more of them (23 of 94), with its seven losses in the same two places; C1 stays MIXED because ties dominate, by rule.
- The honest public sentence is therefore: tq-pro wins at the low-byte end on low-dimensional data, ties once the rerank saturates, and loses only where its own kernel wrapped or at one 132-byte Wikipedia point. "Beats RaBitQ" without those qualifiers is not supported by this campaign and is no longer claimed.

## Provenance

- Preregistration `docs/PREREG_rabitq_public.md` (registered `856c4cb`; Amendments 1 to 4 dated in its log). Harness `benchmarks/rabitq_public/` at the ops branch `feat/quantization-control-plane`; results on the campaign volume `tqp-rbq-data` and mirrored at `/archive/ahb-sjsu/tqp_rabitq_public/` on Atlas.
- Scorer reports, verbatim: `benchmarks/rabitq_public/scoring/2026-09-18T1115/` (`registered.md`, `tqfix.md`, `tq_ivf.md`, the pod log). This file is generated from them by `python -m rabitq_public.write_results`.
