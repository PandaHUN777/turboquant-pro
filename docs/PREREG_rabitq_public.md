# Pre-registration — turboquant-pro vs RaBitQ, PQ and OPQ at matched bytes on public data

**Status: REGISTERED 2026-09-15, before any registered cell ran.** Results land in
`benchmarks/RESULTS_rabitq_public.md`; this file is never edited to fit them. Changes after
registration go in the amendment log (section 8) with a date and a reason.

> **The question.** The ledger row `embedding_beats_rabitq_ties_opq` says turboquant-pro
> beats RaBitQ on recall and ties OPQ at matched bytes. The only committed RaBitQ numbers
> come from one run on a private 199k LaBSE sample (`embedding_labse_32x_headline`,
> *reported*). Does the claim hold on public data, under a byte accounting that counts
> every per-vector scalar, against RaBitQ in its intended configuration?

---

## 0. Claims under test, and what the analyst already knows

- **C1** — at matched stored bytes, turboquant-pro's recall@10 exceeds RaBitQ's.
- **C2** — at matched stored bytes, turboquant-pro's recall@10 ties or exceeds OPQ's.

Build time (the "builds faster than OPQ" part of the README text) is recorded but not
scored: cells run on shared nodes of different CPU models, so a build-time ratio between
two pods confounds the method with the node.

**Prior knowledge, stated so it can be discounted.**

| arm | known before registration | consequence |
|---|---|---|
| GloVe-100, NYTimes-256, deep-image-96 | tq-pro vs PQ/OPQ at 16x, one run each (`benchmarks/RESULTS_glove.md`); flat faiss RaBitQ on a 200k GloVe subset (pilot 2026-09-14: recall@10 0.46 single-pass at 4 bits, 0.84 +rerank x5); a 20k-row synthetic fixture | C2 on these arms is reported as *consistent with* or *not consistent with*, never *confirmed*. C1 is blind for IVF RaBitQ and rabitqlib on every arm. |
| Cohere Wikipedia 1024-d | tq-pro IVF recall at 15M (`benchmarks/fleet/results/real_pilot_15M_wiki1024.json`); no baseline ever measured | C1 and C2 blind |
| DBpedia ada-002 / text-embedding-3-large 1536-d | never measured with any method in this repo | blind |

The flat-RaBitQ pilot is the reason this design runs RaBitQ in IVF form as well: RaBitQ's
estimator is designed for residuals around a nearby centroid, not for raw vectors around a
single global mean.

## 1. Arms

| arm | corpus | dim | corpus rows | queries | ground truth |
|---|---|---:|---:|---:|---|
| `glove-100-angular` | ann-benchmarks train | 100 | 1,183,514 | first 2,000 of `test` | provided `neighbors` |
| `nytimes-256-angular` | ann-benchmarks train | 256 | 290,000 | first 2,000 of `test` | provided `neighbors` |
| `deep-image-96-angular` | ann-benchmarks train | 96 | 9,990,000 | first 2,000 of `test` | provided `neighbors` |
| `wiki1024-10m` | CohereLabs/wikipedia-2023-11-embed-multilingual-v3 (en), rows 0..9,999,999 | 1024 | 9,999,000 | 1,000 rows drawn from those 10M with seed 20260914 and removed from the corpus | exact, `gt.py` |
| `dbpedia-ada002-1m` | KShivendu/dbpedia-entities-openai-1M | 1536 | 990,000 | the next 1,000 rows (`queries.npy`) | exact, `gt.py` |
| `dbpedia-3large-1536-1m` | Qdrant/dbpedia-entities-openai3-text-embedding-3-large-1536-1M | 1536 | 990,000 | the next 1,000 rows | exact, `gt.py` |

Data identities are the sha256 hashes in `benchmarks/rabitq_public/DATA_MANIFEST.json`,
taken from the Atlas copies before any cell ran. The NRP staging job rebuilds the corpora
from their public sources and recomputes the hashes; a mismatch is an amendment. For the
ann-benchmarks arms, `gt.py --check` recomputes exact top-10 for 200 queries under this
normalization and records agreement with the provided neighbours.

All vectors are L2-normalized; the metric is cosine. Queries on the real arms are held-out
corpus rows, so they are in-distribution. That is a limitation (section 7).

## 2. Methods and fixed parameters

The cell grid is `benchmarks/rabitq_public/grid.py` at the registration commit: 540 cells,
3 seeds (0, 1, 2) of each configuration.

| method | what runs | configurations |
|---|---|---|
| `tq` | turboquant-pro `PCAMatryoshka` fit on 100k training rows, `with_quantizer(bits, seed)`, `ADCIndex` with the compiled AVX2 kernel | full dimension at 2, 3, 4 bits; on the 1024/1536-d arms also PCA to d/4 and d/2 at 3 and 4 bits |
| `rabitq_flat` | faiss `RaBitQ{b}`, inner product, trained on 200k rows | 1-5 bits |
| `rabitq_ivf` | faiss `IVF{nlist},RaBitQ{b}`, L2, k-means seed = cell seed, trained on 40 x nlist rows, **nprobe = nlist** | 1-5 bits |
| `rabitqlib_ivf` | official `rabitqlib.IvfIndex`, L2, centroids from seeded faiss k-means on 40 x nlist rows, **nprobe = nlist**, `high_accuracy=True` | 1-5 bits |
| `pca_rabitq_ivf` | the tq PCA front end (d/4, d/2) followed by faiss IVF RaBitQ as above | 1024/1536-d arms only; 1-3 bits |
| `pq`, `opq` | faiss `PQ{m}x8` / `OPQ{m},PQ{m}x8`, inner product, trained on 200k rows | m per arm in `grid.PQ_M` |

Fixed everywhere: faiss RaBitQ query bits `qb = 0` (unquantized queries, the most accurate
setting); `nlist = 2^round(log2(4 sqrt(N)))`; every search returns 50 candidates; training
rows are nested prefixes of one seeded random order per (arm, seed). IVF search is
exhaustive so that recall measures the quantizer's estimator rather than partition
routing; turboquant-pro's search is a flat scan, so routed IVF would compare different
things. `pca_rabitq_ivf` is included so that a C1 win cannot come from the PCA front end
alone.

Software: turboquant-pro at commit `856c4cb` (package unchanged since), faiss-cpu 1.15.0,
rabitqlib 0.3.4, image `python:3.12`; `pip freeze` of the run environment is saved with
the results.

## 3. Measurement

For every cell, from the 50 candidates the compressed search returns:

- **single** — recall@10 of the first 10 candidates;
- **rr2** — recall@10 after exact cosine re-scoring of the first 20;
- **rr5** — recall@10 after exact cosine re-scoring of all 50.

Recall is scored per query against the top-10 of the ground truth.

**Stored bytes per vector** (the matching axis) counts every per-vector scalar and excludes
structures shared across the corpus:

| method | counted | excluded |
|---|---|---|
| `tq` | bit-packed codes `ceil(d' * bits / 8)` + one fp32 norm | PCA basis, codebook |
| faiss RaBitQ (flat, IVF, PCA+IVF) | faiss `code_size` (codes plus per-vector correction factors) | IVF centroids, the 8-byte id per vector in IVF lists |
| `rabitqlib_ivf` | (saved index file size - centroid table) / N | nothing else |
| `pq`, `opq` | m | codebooks, OPQ rotation |

Leaving out the IVF id bytes favours RaBitQ. In-memory size is recorded separately: the
tq `ADCIndex` holds unpacked uint8 codes and two fp32 per vector, more than it stores.

## 4. Statistics and verdict rules

Implemented in `benchmarks/rabitq_public/score.py` at the registration commit.

1. A configuration is scored only when all three seeds finished. Per-query recall is
   averaged over seeds.
2. **Families:** RABITQ = `rabitq_flat` ∪ `rabitq_ivf` ∪ `rabitqlib_ivf` ∪ `pca_rabitq_ivf`;
   OPQ; PQ (reported, no claim).
3. **Matching is two-sided and byte-windowed.** Anchored at each tq configuration with
   stored bytes B, the matched baseline is the family configuration with the highest mean
   rr5 among those storing between 0.80 B and 1.05 B. Anchored at each baseline
   configuration with bytes B', the matched tq configuration is the best one between
   0.80 B' and 1.05 B'. A pair found from both sides counts once. An anchor with nothing
   in its window is a byte gap (`NO-CONFIG`): reported, not scored. Choosing the best
   configuration inside a window on the same queries favours the side being chosen, so
   the two-sided rule gives that advantage to each family in turn.
4. **Paired comparison.** Per-query difference tq minus baseline; percentile bootstrap over
   queries, 10,000 resamples, seed 0; 95% interval [lo, hi] and mean m:
   - BEATS if lo > 0 and m ≥ 0.005
   - LOSES if hi < 0 and m ≤ -0.005
   - TIES if lo ≥ -0.01 and hi ≤ 0.01
   - otherwise INCONCLUSIVE
5. **Primary endpoint: rr5.** It is the protocol of the claim under test. Single and rr2 are
   reported under the same rules and do not enter the claim verdicts.
6. **Claim verdicts,** over all scored pairs of the family on all six arms (INCONCLUSIVE
   stays in the denominator):
   - C1 HOLDS if BEATS ≥ 2/3 of pairs and LOSES = 0; REFUTED if LOSES ≥ 1/3 or BEATS = 0;
     otherwise MIXED.
   - C2 HOLDS if BEATS + TIES ≥ 2/3 and LOSES ≤ 1/6; REFUTED if LOSES ≥ 1/3; otherwise MIXED.
   Verdicts are also reported per arm, as description, not as separate tests.

**Pre-stated expectation, so a saturated result is not mistaken for a strong one.** At rr5
many configurations on easy arms will sit near recall 1.0 and TIE. A C1 verdict carried by
ties would fall short of HOLDS by rule 6, and that is intended: "beats" must be shown where
the methods differ.

## 5. Consequences for the ledger (decided now)

| outcome | `embedding_beats_rabitq_ties_opq` | README / docs |
|---|---|---|
| C1 and C2 HOLD | status `reproducible`; description cites the results file and the per-arm table | headline text may keep "beats RaBitQ, ties OPQ", scoped to the arms and the rr5 protocol |
| either MIXED | status `reproducible`; claim text rewritten to the arms and budgets where it holds | the unscoped phrase is removed from README, CLAIMS.md, docs/claims.md and the notebook |
| either REFUTED | claim text replaced by the measured statement; the old wording kept visible with a pointer, as the long-generation erratum was | unscoped phrase removed everywhere; `embedding_labse_32x_headline` gains a note that public data does not support its RaBitQ clause |

## 6. Execution rules

- Cells run on NRP (`ssu-atlas-ai`) through nats-bursting and openvector-bench's
  `PoolRunner` (`benchmarks/rabitq_public/submit_pool.py`), CPU only, pinned to zone
  `ucsd-suncave` next to the Ceph volume. Order: environment, staging (hashes checked
  against `DATA_MANIFEST.json`), ground truth, then a **calibration wave** of one
  registered cell per (arm, method), its largest configuration at seed 0, sized by the
  memory model in `footprints.py`. Every remaining cell is sized from its class's measured
  peak anonymous memory. Calibration cells are ordinary registered cells; their results
  count like any other.
- Sizing and scheduling choices cannot change a result: they decide where a cell runs and
  how much memory it may use, never what it computes. `rabitqlib` receives the corpus
  through a memory-mapped scratch file instead of an in-RAM array, for the same reason.
- A cell that fails for an operational reason (OOM, preemption, node fault) is rerun,
  unchanged. A cell is never rerun because of its result.
- No cell, configuration or arm is added or dropped after launch without an amendment.
  An arm that cannot be staged is reported as missing and its claims are scored without it.
- Timing is recorded per cell and reported as descriptive only.

## 7. Known limitations

- Queries on the real arms are held-out corpus rows, not user queries; openvector-bench
  found real queries to be out-of-distribution for corpus-region models, so recall on real
  query logs may be lower for every method.
- One CPU architecture family per pod, not controlled; no GPU paths; no graph indexes
  (HNSW, SymQG); no routed-IVF speed/recall trade-off.
- rabitqlib's bytes come from its saved file and may include format overhead the paper's
  accounting would not count.
- The largest arm is 10M rows. Nothing here says how the comparison scales beyond it.

## 8. Amendment log

(none)
