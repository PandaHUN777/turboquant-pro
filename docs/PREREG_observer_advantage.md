# Pre-registration — does observer conditioning move the frontier of codecs tq-pro did not write?

**Status: REGISTERED 2026-09-23, before any cell of section 3 ran on any real arm.** The harness
(`benchmarks/observer_advantage/{grid,cell,score}.py`) is committed with this file, so the scoring rule
is fixed in code as well as in prose. This file is never edited to fit results. Amendments go in
section 9 with a date and a reason. Results land in `benchmarks/RESULTS_observer_advantage.md`.

This is Phase 0 of the observer-aware platform vision (revision 2, kept outside this repository).
That vision's central claim is that the observer layer is independent of any one codec. This
registration is the test that can refute that claim.

**Run before registration, disclosed.** The harness was executed only on synthetic arms with a
planted effect (`tests/test_observer_advantage_harness.py`), to test the harness, not the hypothesis.
No real arm was loaded by it. That run changed the design in one place, stated in section 2 under
"The split": on a synthetic symmetric arm, consumer_basis's O lost to P through TQ although it tied P
under exact search. The cause is derived there, and the registered O is the construction the
derivation selects, not the one that scored better.

> **The question.** `RESULTS_consumer_basis.md` (registered, scored 2026-09-16) found that keeping the
> subspace the queries read (basis **O**) beats corpus PCA (basis **P**) at fixed dimension on
> asymmetric retrieval, 6 of 6 cells, and ties or beats it on symmetric retrieval. That was measured
> with **exact search in the kept subspace, with no quantizer**. Does the advantage survive when the
> kept subspace is then compressed by three unrelated codec families, at matched stored bytes, and does
> it still vanish where queries and documents are distributed alike?

---

## 0. Prediction, and what is already known

For inner-product top-k retrieval the consumer's read operator is the query second moment
`C = E[q qᵀ]`. Basis O minimises expected squared score error at rank k given `C` and the corpus
second moment `S` (derivation in `PREREG_consumer_basis.md` section 0). A codec applied after the
transform adds its own error on top of the truncation error. The theory predicts the truncation
advantage carries through unless the codec's error dominates the truncation error at the budgets
tested.

**Prediction.** For each of the three codec families, O beats P on the asymmetric primary arms at
matched bytes, ties it on the symmetric primary arm, and the size of the gain follows the
query/corpus mismatch index `m = 1 − ⟨S, C⟩ / (‖S‖ ‖C‖)`.

**Known before registration, disclosed so it can be discounted.**

- The exact-search gains on msmarco were +0.0125 to +0.0147 recall@10. They sit just above the
  materiality bar of ±0.01 used below. Codec noise can push them to TIE. The bar is not lowered for
  that reason.
- On `nq` (mismatch 0.507) P led O at k = 256 under exact search (0.807 vs 0.802). That is evidence
  against H3 before it runs.
- `hotpotqa-sym` carries mismatch 0.095 and showed O ahead. It is therefore not a clean symmetric
  control, and section 4 does not use it as one.
- Reranking the top 100 closed most of the P/O gap at k ≥ 256. The rerank endpoint is expected to show
  smaller differences than the single-pass endpoint.
- **The rank of C is not the control variable.** C is full rank (1024) on every arm, symmetric or
  not. The v1 vision's exit criterion ("absent where read geometry is effectively full-rank") would
  predict no advantage anywhere and is replaced by the mismatch index.

## 1. Data

The arms, staged arrays, fit rows and evaluation queries of `PREREG_consumer_basis.md` section 1,
unchanged: Cohere embed-english-v3 (1024-d) from `CohereLabs/beir-embed-english-v3` at revision
`f018922a46a51388348a307ec2fef28019a33026`. The staged arrays are reused by sha256 from the campaign
volume. They are not re-staged.

| arm | role here | mismatch (measured 2026-09-16) |
|---|---|---:|
| `msmarco` | asymmetric, primary | 0.4395 |
| `hotpotqa` | asymmetric, primary | 0.5178 |
| `msmarco-sym` | symmetric control, primary | 0.0048 |
| `hotpotqa-sym` | intermediate, H3 only | 0.0952 |
| `fiqa`, `nq`, `quora` | H3 only | 0.3109, 0.5074, 0.0140 |
| `msmarco×hotpotqa-C` | foreign observer, H4 only | not a new arm (see section 2) |

## 2. Transforms, codecs and fixed parameters

**Transforms.** P and Q exactly as defined in `PREREG_consumer_basis.md` section 2, by the same
function (`consumer_basis.run.bases`), imported, not copied. They are computed at k = 256 and taken as
prefixes. The leading k components of each construction do not depend on how many are computed, so
these prefixes are the ones the k = 512 computation of that registration produced.

**The split.** With `C^½ S^½ = U Λ Vᵀ`, consumer_basis's O maps queries by `(C^-½ U_k)ᵀ` and
documents by `Λ_k V_kᵀ S^-½`. Moving any diagonal D from one map to the other leaves every score
`(A q)·(B x)` unchanged, so exact search cannot see the split, and `RESULTS_consumer_basis.md` does not
depend on it. A codec quantizes `B x` alone, so it can. For a codec that rotates and spends its bits
evenly across coordinates (TQ, RaBitQ), the score error grows with `E‖Bx‖² · E‖Aq‖²`. That product is
`k·Σλᵢ²` for the Eckart–Young split and `(Σλᵢ)²` for `Λ^½` on each side, and Cauchy–Schwarz makes the
second the minimum over diagonal splits, equal to the first only for a flat spectrum. The balanced
maps also reduce to corpus PCA *as maps*, up to a scalar, when `C ∝ S`, which is the premise of the
symmetric control. The Eckart–Young split reduces to PCA only in its scores.

- **O** (registered): `A = Λ_k^½ U_kᵀ C^-½`, `B = Λ_k^½ V_kᵀ S^-½` (`observer_advantage.cell.balanced_o`).
- **Oey** (reported, not scored): consumer_basis's Eckart–Young split, unchanged. **Stated
  prediction:** Oey's recall equals O's under exact search (checked by G0) and is at or below O's
  through TQ and RaBitQ, the more so the steeper the spectrum. For OPQ, which adapts its codebooks to
  the variance it is given, the prediction is not made.
- **O_foreign** (H4 only): the balanced O with `S` from the msmarco corpus and `C` from the hotpotqa
  train queries. It is applied to the msmarco corpus and scored on msmarco dev queries. It is the O
  basis of the wrong observer.

**Codec families.** Each consumes the transformed document vectors in k dimensions. Queries go
through the query map. Scores are **inner products in the transformed space** for every codec, because
O's two maps do not preserve norms.

| family | implementation | parameter giving b bits per kept dimension | stored bytes per vector |
|---|---|---|---|
| **TQ** | tq-pro `PCAMatryoshka(input_dim=k, output_dim=k)` (a full-dimension rotation plus centering, no truncation) + Lloyd-Max scalar codes, `ADCIndex(metric="inner_product")` scan (the v3 kernel where built, else numpy; see "Scan path") | `bits = b` | `ceil(k·b/8) + 4` |
| **RBQ** | faiss `RaBitQ{b}` flat index, `METRIC_INNER_PRODUCT`, `qb = 0` | `bits = b` | `code_size` as reported by faiss |
| **OPQ** | faiss `OPQ{m},PQ{m}x8`, `METRIC_INNER_PRODUCT` | `m = k·b/8` | `m` |

`k ∈ {64, 128, 256}`, `b ∈ {2, 4}`, three seeds (0, 1, 2). Codec training uses the first 200,000
transformed corpus rows, so a seed reaches only a codec's own randomness: TQ's rotation and OPQ's
k-means. faiss's flat RaBitQ takes no seed, so its three seeds repeat one computation, and its seed
spread is zero by construction, not by measurement. Evaluation queries fit nothing.

**Scan path.** The TQ family scans with tq-pro's compiled kernel where it is built and in numpy
otherwise. The two agree only to within the kernel's table-rounding bound, so every record carries its
scan path and gate G3 requires the two sides of every comparison to share one.

**Why matched bytes holds by construction.** Within a family, a P cell and an O cell at the same
(k, b) store identical per-vector bytes. The transform is a shared table and does not appear per
vector. Shared-table bytes (basis matrices, codebooks) are reported per arm, as in
`PREREG_rabitq_public.md` requirement R6. The registered contrast is within a family, so no
cross-family byte matching is needed.

**Engineering prerequisite, met.** tq-pro's `ADCIndex` scored cosine only, dividing by the
reconstruction norm. The TQ family needs inner-product scoring on non-unit vectors.
`ADCIndex(metric="inner_product")` merged in #199 (`5175cd6`). It is tested to equal
`q @ decompress(compress(x)).T` to 1e-5 of the score scale (measured 3.4e-7), including a two-map
basis test that scores `(A q) · recon(B x)`.

## 3. Measurement

Ground truth: exact full-dimension (1024-d, untransformed) inner-product top-10 over the arm's corpus,
the same ground truth as `RESULTS_consumer_basis.md`. For each (arm, transform, family, k, b, seed),
per evaluation query:

- **single**: recall@10 of the codec's top-10 in the transformed space (primary endpoint);
- **rr5**: recall@10 after exact full-dimension rescoring of the codec's top-50 (secondary).

Per-query hits are averaged over the three seeds before any statistic is computed. A configuration
missing any seed is excluded and listed, as in `RESULTS_rabitq_public.md`. Nothing is imputed.

## 4. Gates, statistics and verdicts

**Harness gates, checked before any hypothesis is scored.** A failed gate voids the run. It is
reported, fixed and rerun unchanged, never scored around. A gate that cannot be checked (a missing
record) withholds every verdict, the same as a failed one. The EXACT family, exact search in each
kept subspace for every (arm, transform, k), is part of the run and supplies G0 and G2.

- **G0 (wiring).** With the codec replaced by exact search in the transformed space, P and O
  reproduce the `RESULTS_consumer_basis.md` single-pass recall at k ∈ {64, 128, 256} on msmarco and
  hotpotqa to within ±0.002. O and Oey agree under exact search to within ±0.002 on every arm and k,
  because they differ only by the split.
- **G1 (the effect exists to be tested).** Under G0's exact search, O − P on the asymmetric primary
  arms is BETTER in at least 5 of 6 cells. This is already known to hold. It is re-measured here
  because a claim that "X survives quantization" means nothing if X is absent in this harness (the
  standing rule after readscope C-7b and C-8: require a prior bar that Y varies).
- **G2 (codec sanity).** Every codec configuration's single-pass recall is at or below the EXACT
  recall at the same (arm, transform, k) plus 0.005, and above 0.01. A configuration that beats exact
  search in its own subspace is a scoring bug.
- **G3 (paired means paired).** Both sides of every scored comparison, and all seeds of one
  configuration, used the same scan path.

**Cell statistic.** Paired per-query difference in recall@10, percentile bootstrap over evaluation
queries, 10,000 resamples, seed 0, 95% interval [lo, hi], mean d. BETTER if lo > 0 and d ≥ 0.01;
WORSE if hi < 0 and d ≤ −0.01; TIE if lo ≥ −0.01 and hi ≤ 0.01; otherwise INCONCLUSIVE. Same rule as
`PREREG_consumer_basis.md`, deliberately.

**Hypotheses.** Each is scored per family f ∈ {TQ, RBQ, OPQ}, on the single-pass endpoint.

- **H1(f), survives the codec.** O vs P on `msmarco` and `hotpotqa`, k ∈ {64, 128, 256}, b ∈ {2, 4}:
  12 cells. HOLDS if BETTER in ≥ 9 and WORSE in none. REFUTED if BETTER in ≤ 3 or WORSE in ≥ 2.
  Otherwise MIXED.
- **H2(f), control.** O vs P on `msmarco-sym`, 6 cells. HOLDS if TIE or BETTER in ≥ 5 and WORSE in
  none. REFUTED if WORSE in ≥ 2. Otherwise MIXED.
- **H3(f), the mismatch orders the gain.** Across all seven arms, Spearman correlation between the
  mismatch index and the mean single-pass O − P difference at k = 128, b = 4. HOLDS if ρ ≥ 0.714 (the
  one-sided 5% critical value at n = 7). REFUTED if ρ ≤ 0. Otherwise MIXED. Seven points order a
  quantity. They do not fit a law, and no result here is reported as one.
- **H4(f), it is the observer, not the procedure.** O vs O_foreign on msmarco, 6 cells. HOLDS if
  BETTER in ≥ 5 and WORSE in none. REFUTED if O_foreign is BETTER than O in any cell. Otherwise
  MIXED.

**The platform claim.** The vision's statement "the observer layer is codec-independent" is licensed
only if H1 and H2 HOLD in **all three** families and H4 HOLDS in at least two. It is reported as
"holds for f only" if they HOLD in one or two families. It is withdrawn if H1 is REFUTED in two or
more families.

**Reported, not scored.** Q against P and against O; Oey against O, against its stated prediction;
the rr5 endpoint for every hypothesis; the seed spread; build and search seconds with the hardware
fingerprint; the Observer Advantage table below.

**The Observer Advantage table (descriptive).** For each family, arm and quality level
`Q ∈ {0.80, 0.90, 0.95}` on each endpoint: `bytes_P(Q)` is the smallest stored byte level among
measured P configurations whose seed-averaged recall has a bootstrap lower bound ≥ Q. `bytes_O(Q)` is
the same for O. The table reports `bytes_P(Q) / bytes_O(Q)`, or "not measured" when either side has
no configuration that clears Q. There is no interpolation between byte levels. The measured byte
levels are coarse (16 to 128 bytes of codes per family), and the table says so beside every ratio.

## 5. What each outcome licenses

| outcome | tq-pro | platform vision |
|---|---|---|
| H1, H2 HOLD in all three families; H4 HOLDS in ≥ 2 | consumer basis O becomes a planner transform stage for every registered codec, opt-in, fitted from a query sample | the codec-independence claim may be made, scoped to asymmetric text retrieval on one embedding family |
| H1 HOLDS for TQ only | O stays a TQ option | the observer layer is described as a TQ feature. The neutral-planner story rests on selection among providers, not on conditioning them |
| H1 HOLDS, H2 not | the gain is not the theory's mechanism | reported as a negative for the mechanism. No platform claim |
| H1 HOLDS, H4 not | the gain is a better-conditioned fit, not observer relativity | reported as such. "Observer-aware" is not claimed |
| H1 REFUTED in ≥ 2 families | O does not survive quantization at these budgets | Phase 0 fails as registered. The vision is revised before any design-partner conversation |

## 6. Prior art to position against

Score-aware and query-aware compression is not new. ScaNN's anisotropic quantization weights the
error that changes inner products. ADSampling and DADE/DDCpca order or sample dimensions for early
termination. Query-aware subspace methods exist (TaCo, 2026). Asymmetric distance computation in PQ
treats queries and documents differently by design. What this tests is narrower: whether one
transform fitted to the observer improves three unrelated codecs at matched bytes, with a symmetric
control and a wrong-observer control. Any novelty claim needs its own literature search first.

## 7. Execution and limitations

- The harness is `benchmarks/observer_advantage/`. It imports `consumer_basis` for the arms, staged
  arrays, bases and exact search, `consumer_basis.score` for the cell statistic, and `rabitq_public`'s
  faiss conventions. It adds no new estimator. A job is (arm, transform, family, seed) and writes one
  record per (k, b); the grid is `grid.py`.
- Compute on NRP through the existing `burst.submit` flow, sized by `benchmarks/nrp/sizing.py`, with
  `utilization_guard.py` running, and checked against the cluster's resource policy before the first
  submission. The submitter is added after this registration and changes no scored quantity.
- Cell count: 7 arms × 4 transforms (P, O, Q, Oey) × 3 families × 3 k × 2 b × 3 seeds = 1,512,
  plus 54 for O_foreign, plus 87 EXACT reference cells. It is sized before submission. If the
  budget forces a cut, the cut is made here, by amendment, before any cell runs.
- One embedding model. Ground truth is exact search, not human relevance labels. Evaluation queries
  come from each arm's own query split, the distribution O is fitted to. That is the favourable case
  for any observer-fitted method, and H4 is the only check against it.
- A run is never repeated because of its result. An operational failure is rerun unchanged.

## 8. Part II, a second observer (not registered here)

The vision requires observer diversity. The candidate second observer is attention keys, where
readscope measured that a head's read subspace is spanned by its queries (C-3b, resolution 1.000 on
48 cells) and `tr(P̂ Σ_δ)` picked the worse quantizer in 16 of 16 cells where reconstruction error
picked it in 2. The Part II registration would compare `read_allocation` water-filling against
`attention_analytic` with uniform widths, across at least two key quantizer families, on attention
output error on held-out tokens. It is written and registered separately, and it must be committed
before any Part I hypothesis is scored, so Part I verdicts cannot shape Part II bars. Its bars are
not drafted here.

## 9. Amendment log

- **Amendment 1, 2026-09-23, before any cell ran on a real arm. Operational; no scored quantity
  changes.** The OPQ family now adds rows to its index in chunks (`cell.opq_add_rows`). faiss
  encodes a call's rows through a `rows × m × 256` float distance table in blocks of 262,144
  rows, which is 34 GiB at m = 128 and would kill any compliant pod. Codes are computed per
  vector, so chunking bounds the table at 512 MiB and leaves every code bit-identical,
  checked on the codes themselves (`test_chunked_opq_add_is_bit_identical`). Found while
  checking the harness against the cluster's resource policy, before the submitter was
  first run.
