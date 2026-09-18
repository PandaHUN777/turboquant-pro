# Design — feasibility, before the sweep

Issue #176, in the Observation Theory family (#183). Phase 1 on
`feat/feasibility`. Reads an observer contract (#173).

## 0. Thesis

The planner answers *which codec*. It answers it by measuring every candidate,
which costs a sweep. Two questions come before it and cost a single pass over a
sample:

1. **Is the requested guarantee attainable at all** by the widths this library
   stores? If not, the answer is not a better codec, it is a different target
   or exact reranking.
2. **Is what the consumer needs already missing** from this representation?
   Observation Theory's omission floor (Paper III, `thm:omission`) says that
   information the observation has already discarded is not recoverable
   downstream. No encoder repairs it. If the consumer's read directions carry
   no variation in these vectors, compression is the wrong lever.

A tool that answers *should I even compress this* is worth more than one more
point on a rate–distortion curve, and both answers come from quantities the
library already computes.

## 1. What it measures

With `Σ` the corpus covariance and `P` the observer's read operator, read in
the eigenbasis of `Σ` so "a direction the data has" and "a direction the
consumer reads" are stated in one frame:

| quantity | definition | what it tells you |
|---|---|---|
| observable signal | `tr(P Σ)` | what the consumer can tell rows apart by at all |
| observable rank | participation ratio of `P^½ Σ P^½` | how many directions carry it |
| unread source dimensions | the weakest directions whose contributions together stay under a thousandth of the observable signal | how much dimension reduction is free before any quantizer runs |
| omitted sensitivity | `tr(P)` in the null space of `Σ`, as a fraction | the omission floor, measured |
| distortion floor | `Σ_i w_i D(4)` over `w_i = (u_iᵀ P u_i) σ_i²` | the best the widest width can do |
| minimum payload | fewest bytes whose best allocation meets a declared distortion | what to budget, before the sweep |

`D` is the Lloyd-Max table of `turboquant_pro.spectrum`, the same one the
spectrum allocation was preregistered and measured on. The allocation is
greedy-optimal for consecutive widths and its distortion falls with the
budget, so a bisection over total bits finds the smallest payload.

## 2. The verdicts, and the two thresholds that are conventions

- **INFEASIBLE, omission.** More than **half** of the consumer's sensitivity
  sits where the corpus does not vary. The rule is a majority, stated rather
  than tuned: past it, most of what the consumer nominally reads carries no
  row-to-row information here. The reason names both readings, because the
  measurement cannot separate them: either the consumer is declared over
  directions this representation does not carry, or the encoder dropped them.
  Compression repairs neither. Below the majority the same number is a
  **warning**, not a verdict, because constant directions are free for a
  reconstruction consumer and useless only to one that must tell rows apart.
- **INFEASIBLE, width floor.** The widest width leaves more distortion than
  the declared target. No allocation of these widths reaches it; raise the
  target or keep exact originals for rerank.
- **INFEASIBLE, rank.** A Kendall-tau floor is answered by the rank
  certificate's own inversion, `max_certifiable_kappa`, which needs no
  conversion from recall or distortion. When it returns a ratio under
  **1.01**, only a code preserving every pairwise distance to within one
  percent certifies the floor, which no allocation of these widths does. That
  1.01 is a stated convention, not a derived constant.
- **ABSTAIN, identification.** When the operator is an estimate rather than a
  closed form, the report measures how much source variance lies outside the
  subspace the estimate could identify. readscope's recovery cliff at `k = d`
  is a theorem: below full dimension a confined transcript cannot identify
  hidden components. Sensitivity reported as zero there may be unread or
  merely unidentified, and the two are indistinguishable, so the verdict is
  ABSTAIN rather than a guess. A retrieval consumer read through a query
  sample is an estimate; one with no queries at all is the identity stand-in
  and identifies nothing.
- **PASS** otherwise, with the observable rank and the minimum payload.

## 3. Two things it deliberately will not do

- **It will not accept a recall target.** `recall@10 ≥ 0.999` is not
  convertible to a distortion by any distribution-free relation. The tool
  takes a distortion as a fraction of the observable signal, and answers a
  rank floor through the certificate. Translating recall is what the planner's
  measured sweep is for.
- **It will not report a measured recall.** Every number here is a prediction
  from the distortion table over the corpus spectrum. The spectrum campaign
  measured that allocation beating uniform widths at four of six byte levels
  on 1024-d Wikipedia and losing at every level on flat-spectrum GloVe
  (`benchmarks/RESULTS_spectrum_bits.md`), so the prediction is a planning
  signal with a known error bar, not a certificate.

## 4. Interface

```
tqp feasibility --artifact corpus.npy --observer production.tqo \
    --max-distortion 0.01 --min-tau 0.9 [--queries q.npy]
```

Exit 0 on PASS, 1 on INFEASIBLE or ABSTAIN, 2 on a usage or provider error.
`--reference PROVIDER` stands in for a contract when there is not one yet.

## 5. Phases

1. **The report.** Shipped: `turboquant_pro.feasibility`, `tqp feasibility`,
   `tests/test_feasibility.py`.
2. **Against the planner.** Run feasibility before every `tqp plan run` and
   record it in the plan record, so an abstention or an infeasible target
   stops the sweep instead of being discovered by it.
3. **Calibrated.** Compare the predicted minimum payload against the bytes the
   planner actually selects on the six public arms, and publish the error.
   Until that runs, the payload is a prediction and the docs say so.
