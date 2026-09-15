# Pre-registration — which directions should a truncated embedding keep? Consumer-read bases vs corpus PCA

**Status: REGISTERED 2026-09-15, before any real embedding was staged or searched.** Results land in
`benchmarks/RESULTS_consumer_basis.md`; this file is never edited to fit them. Amendments go in
section 8 with a date and a reason.

> **The question.** tq-pro truncates embeddings with PCA of the corpus: it keeps the directions the
> documents vary in most, which is the reconstruction corner (P_C = I) of Observation Theory. The
> theory says the directions to keep are the ones the consumer reads. For top-k inner-product
> retrieval the consumer's read operator is the query second moment C = E[q qᵀ]. Does truncating
> in a consumer-read basis retrieve better than corpus PCA at the same number of dimensions — and
> only when queries and documents are distributed differently?

Search time of tq-pro's scan is linear in the kept dimension (measured 2026-09-15, v1 vs v2 kernel
benchmark), so a basis that holds recall at fewer dimensions is a direct speedup. The work is useful
to borrow even where it is not new; section 6 records the prior art it has to be positioned against.

---

## 0. Prediction from the theory

The expected squared score error of a rank-k inner-product approximation `qᵀMx` is
`E[(qᵀx − qᵀMx)²] = ‖C^½ (I − M) S^½‖²_F`, with `S = E[x xᵀ]` the corpus second moment. Its minimum
over rank-k `M` is given by Eckart–Young on `C^½ S^½` (basis O below). When queries are distributed
like documents, `C ∝ S`, basis O reduces to corpus PCA and nothing changes. When they differ, O keeps
what the queries read.

**Prediction:** O beats corpus PCA (P) on asymmetric retrieval (real queries against passages) and
ties it on symmetric retrieval (held-out documents as queries). The gain should grow with the
mismatch between C and S.

**Prior knowledge.** None of these bases has been measured on real embeddings in this project. A
synthetic check of the pipeline (600-d Gaussians, 20k corpus, 3k fit queries) showed large gains for
O, S and Q on an asymmetric construction, and a small loss for O on a symmetric one, traced to fitting
C from 3,000 samples in 600 dimensions. That observation shaped section 2 (fit sizes, which arms are
primary); it is disclosed so it can be discounted.

## 1. Data

All embeddings are Cohere embed-english-v3 (1024-d) from the Hugging Face dataset
`CohereLabs/beir-embed-english-v3` at revision `f018922a46a51388348a307ec2fef28019a33026`; documents
and queries were embedded by Cohere with their own input types. Row ranges below are half-open, in
file order (`benchmarks/consumer_basis/arms.py`). The staging job records the sha256 of every staged
array.

| arm | kind | corpus | fit rows (for C) | evaluation queries |
|---|---|---|---|---|
| `msmarco` | asymmetric, primary | msmarco/corpus/0000.parquet [0, 1,000,000) | msmarco train queries [0, 100,000) | msmarco dev queries, 6,980 |
| `hotpotqa` | asymmetric, primary | hotpotqa/corpus/0000.parquet [0, 1,000,000) | hotpotqa train queries, 85,000 | hotpotqa test queries, 7,405 |
| `msmarco-sym` | symmetric, primary | msmarco corpus [0, 900,000) | msmarco corpus rows [900,000, 950,000) | msmarco corpus rows [950,000, 957,000) |
| `hotpotqa-sym` | symmetric, primary | hotpotqa corpus [0, 900,000) | hotpotqa corpus rows [900,000, 950,000) | hotpotqa corpus rows [950,000, 957,000) |
| `fiqa` | asymmetric, secondary | fiqa corpus, 57,638 | fiqa train queries, 5,500 | fiqa test queries, 648 |
| `nq` | asymmetric, secondary | nq/corpus/0000.parquet [0, 1,000,000) | nq test queries [0, 2,000) | nq test queries [2,000, 3,452) |
| `quora` | symmetric, secondary | quora corpus, 522,931 | quora dev queries, 5,000 | quora test queries, 10,000 |

Secondary arms are reported and not scored: their fit sets are small for a 1024×1024 second moment
(FiQA 5,500, NQ 2,000, Quora 5,000), or their evaluation set is small (FiQA 648).

## 2. Bases and fixed parameters

All vectors are L2-normalized; scores are inner products. `S` is estimated on the first 200,000 corpus
rows, `C` on the arm's fit rows; evaluation queries are never used to fit anything.

| basis | map for queries | map for documents |
|---|---|---|
| **P** corpus PCA | top-k eigenvectors of S | same |
| **Q** query PCA | top-k eigenvectors of C | same |
| **S** symmetric consumer basis | top-k eigenvectors of (CS + SC)/2 | same |
| **O** asymmetric optimum | `(C^-½ U_k)ᵀ` | `Λ_k V_kᵀ S^-½`, where `C^½ S^½ = U Λ Vᵀ` |

Inverse square roots floor eigenvalues at 1e-6 of the largest. `k ∈ {32, 64, 128, 256, 512}`; each
basis is computed once at k = 512 and smaller k are prefixes. **S** is included because a basis applied
identically to queries and documents is what drops into tq-pro's existing pipeline; **O** needs two
maps. Unscored fit-size curve: O refit on the first 2,000 and 10,000 msmarco fit queries.

Code: `benchmarks/consumer_basis/{arms,stage,run,score}.py` at the registration commit.

## 3. Measurement

Ground truth: exact full-dimension inner-product top-10 over the arm's corpus. For each basis and k,
per evaluation query:

- **single** — recall@10 of exact top-10 search in the k-dim space (primary endpoint);
- **rerank** — recall@10 after exact full-dimension rescoring of the k-dim top-100 (secondary).

## 4. Statistics and verdicts

Implemented in `benchmarks/consumer_basis/score.py`. Paired per-query difference in recall@10
(basis − P), percentile bootstrap over the evaluation queries, 10,000 resamples, seed 0, 95% interval
[lo, hi], mean m:

- BETTER if lo > 0 and m ≥ 0.01; WORSE if hi < 0 and m ≤ −0.01;
- TIE if lo ≥ −0.01 and hi ≤ 0.01; otherwise INCONCLUSIVE.

Cells: primary arm × k ∈ {64, 128, 256}.

- **H1** — O vs P on `msmarco`, `hotpotqa` (6 cells): HOLDS if BETTER in ≥ 5 and WORSE in none;
  REFUTED if BETTER in ≤ 1 or WORSE in any; otherwise MIXED.
- **H2** — O vs P on `msmarco-sym`, `hotpotqa-sym` (6 cells): HOLDS if TIE or BETTER in ≥ 5 and
  WORSE in none; REFUTED if WORSE in ≥ 2; otherwise MIXED.
- **H3** — S vs P on `msmarco`, `hotpotqa`: the rule of H1.

The theory's claim is supported only if H1 and H2 both HOLD. H1 without H2 would say O helps for
reasons the theory does not give (for example a better conditioned estimate), and is reported that
way. Everything else — Q, k = 32 and 512, the rerank endpoint, the fit-size curve, the secondary arms,
and the relation between the mismatch index `1 − ⟨S, C⟩ / (‖S‖‖C‖)` and the gain — is reported and
not scored.

## 5. What each outcome licenses

| outcome | tq-pro | Paper II / ledger |
|---|---|---|
| H1 and H3 HOLD, H2 HOLDS | add an opt-in consumer basis (S, or O with two maps) fit from a query sample; document the fit-size curve | a registered consumer-relative result for retrieval truncation, positioned against the prior art in section 6 |
| H1 HOLDS, H2 not | the gain is not the theory's; engineering use only after understanding why | reported as a negative for the theory's mechanism |
| H1 REFUTED | corpus PCA stays the default | reported as a miss at equal prominence |

## 6. Prior art to position against (checked 2026-09-15)

Consumer-aware or score-aware compression for retrieval is not new: ScaNN's anisotropic quantization
weights the error that changes inner products; ADSampling (SIGMOD 2023) and DADE / DDCpca use
variance-ordered or sampled dimensions to terminate distance computations early; query-aware subspace
methods exist (e.g. TaCo, 2026). What this registration tests is narrower: whether choosing the kept
subspace from the query distribution, per the read-operator construction, changes exact-search recall
at fixed dimension, with a symmetric control that the construction predicts will not move. Any
novelty claim needs its own search before it is written.

## 7. Execution and limitations

- Staging (exempt pods, streamed parquet) and one compute job per arm on NRP, submitted through
  nats-bursting; arrays are hashed at staging and the hashes are carried into each result.
- One embedding model; no quantization (tq-pro's bit allocation is not part of this test); ground truth
  is exact search, not human relevance labels; 1M-row corpora are the first parquet file, not the full
  collections.
- A run is never repeated because of its result; an operational failure is rerun unchanged.

## 8. Amendment log

(none)
