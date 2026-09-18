# Design — progressive multi-observer codes (TQE-R)

Issue #174, the second of the Observation Theory family (#183). Phase 1 shipped
on `feat/refinement-report`; the storage phases follow.

## 0. Thesis

An index built for search is reused for analytics, for anomaly detection, for
a reranker's shortlist, and each of those readers weighs the directions of
the vector differently. Today the choice is one code sized for the most
demanding reader, or one index per reader. Observation Theory's two-observer
successive-refinement region (geometric-observation, Paper III) says a third
option exists exactly when the readers' operators share their directions: a
base description for the first reader that a second layer refines for the
second, so the first reads fewer bytes and nobody stores twice. It also says
when the option does not exist: the layered code then costs a tax over one
flat code, and past some tax two representations are cheaper than one.

The software should discover which case it is in, rather than pretend one
representation is good for every use. Phase 1 makes that discovery a number
before anything is built.

## 1. The model (Phase 1)

A code quantizes the source in one orthonormal basis `U` at integer widths
`b_i` per direction from the widths the v3 scan stores, 0 to 4 bits. The
error along `u_i` has variance `sigma_i^2 D(b_i)`, `D` the Lloyd-Max
distortion table of `turboquant_pro.spectrum` (preregistered and measured in
`benchmarks/RESULTS_spectrum_bits.md`), independent across directions. An
observer with read operator `P` therefore sees

    d_P(b; U) = sum_i (u_i^T P u_i) sigma_i^2 D(b_i)

and only the diagonal of `P` in the code's basis enters, exactly, because the
error covariance is diagonal there. `turboquant_pro.refinement` computes four
quantities from a corpus sample and two observers, each an operator and a byte
budget:

| quantity | basis | what it is |
|---|---|---|
| alone | each observer's own eigenbasis | the spectrum allocation at its budget; its distortion `d*` is the quality it would have by itself |
| progressive | the base observer's eigenbasis | the base allocation, then bits added where they cut the second observer's distortion most per bit until it reaches its `d*` |
| flat joint | the average operator's eigenbasis | one code meeting both `d*` at once, the fewest bits a single representation needs |
| separate | each its own | two codes, the sum of the budgets |

The **refinement tax** is progressive total over flat total minus one. The
**overlap** `tr(P_A P_B) / (‖P_A‖ ‖P_B‖)` says why the tax is what it is.

The verdict, in order: the refinement cannot reach the second observer's
`d*`, separate; the layered code saves nothing over two codes, separate; no
flat code reaches both but the layered one does, progressive; tax at or
under the threshold (0.15), progressive; otherwise separate, with the tax and
the overlap named. Three cases the tests pin: identical readers layer at no
tax; readers on disjoint coordinate blocks layer at no tax, because the
second block lies in the first's null space; a reader on a rotated subspace
is told to keep its own code, because refining a basis it does not share
costs as much as a second code.

An observer's operator comes from its contract (#173): a `read_operator`
consumer asks its provider; a top-k retrieval consumer reads along the
queries, `E[q q^T]` over unit queries, since its score is `q · x`, and every
direction equally when no queries are given; consumers are mixed by weight.

```
tqp plan refine --artifact corpus.npy --queries q.npy --observer search.tqo --observer analytics.tqo
SUCCESSIVE REFINEMENT REPORT
Observers: search (base), analytics (refined)   dim 1536
Read-operator overlap: 0.41
  search alone: 100 B/vec, consumer distortion 0.0312 of unstored
  analytics alone: 148 B/vec, consumer distortion 0.0187 of unstored
Progressive: base 100 B + layer 56 B = 156 B/vec
Flat joint code meeting both: 148 B/vec
Separate representations: 248 B/vec (sum)
Refinement tax: +5.4% (threshold 15%)
VERDICT: progressive representation recommended
```

The numbers above are the report's shape, not a measurement.

## 1b. The compatibility matrix (issue #179)

The same mathematics answers a question one step back: not *can these two
share a layered code*, but *is the code I already built for one reader safe
for the others at all*. `compatibility_matrix` allocates, for each observer,
the code that observer would choose at a common byte budget, then reads that
code with every observer's operator. Rows are the observer the code was built
for, columns the reader; cells are the reader's distortion as a fraction of
what it reads and the ratio against its own code at the same bytes.

A pair counts as safe when that ratio stays under **1.25**, a stated
convention: a quarter more error than the reader's own optimum is the band
where it keeps working, and outside it the reader is looking at a different
representation. Three cases the tests pin: the diagonal is each observer's own
optimum by construction; readers on disjoint subspaces are unsafe both ways;
and a code allocated against a reader that reads every direction serves a
narrower reader safely, while the reverse does not hold. That asymmetry is
the useful part, and it is invisible to any single-number "quality" of a code.

`tqp plan compat` exits 1 when any pair is unsafe, so it works as a gate.

## 2. What Phase 1 does not do

- It predicts from the distortion table; it stores nothing and measures no
  reader. The spectrum campaign found the table's allocation beat uniform
  widths at four of six byte levels on 1024-d Wikipedia and lost on
  flat-spectrum GloVe, so the prediction is a planning signal, not a
  certificate.
- Two observers. The region is stated for two; a chain of layers is the same
  computation applied in order and comes with the container.
- The base observer is the smaller budget. Choosing the base by reader
  frequency or by value is the value-of-observation planner (#181).

## 3. Phases

1. **The report.** Shipped: `turboquant_pro.refinement`, `tqp plan refine`,
   `tests/test_refinement.py`.
2. **The container.** A base segment and named refinement segments in the TQE
   container, each with its widths per direction and its bytes per row, so a
   reader opens the layers its contract names and the scan kernel (per-dim
   tables, weighted segments) scores base plus layer as one row. Bit-exact
   with a flat index at the same total widths.
3. **The measurement.** The report's predicted distortions and the campaign's
   rerank protocol against real readers on the public arms, preregistered
   like the spectrum cells: does the base reader keep its recall at base
   bytes, does the layered reader match the flat one, and is the measured
   tax the predicted one.
4. **Adaptive readers** (#175): a reader that opens the next layer only when
   its margin is not decisive.
