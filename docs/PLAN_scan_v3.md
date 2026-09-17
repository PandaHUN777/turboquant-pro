# Plan — what the public RaBitQ comparison asks of the library

**Written 2026-09-17, from the interim scoring of `docs/PREREG_rabitq_public.md`
(477 of 540 registered cells).** The campaign is still running and nothing below
changes it: the registered cells run the code at `856c4cb`, the supplementary
cells at `3d96506`, and both are pinned by commit. This plan is the library work
those results point at, done in phases that each leave the tree releasable.

## What the numbers said

| observation | evidence (interim, +rerank x5 unless stated) | phase |
|---|---|---|
| The shipped AVX2 kernel wraps its uint16 sums above 257 dims. | tq-pro d1536 on text-embedding-3-large: 0.785 / 0.862 / 0.964 against 1.000 for every baseline. The fix (`3d96506`) is on `master` and in no wheel. | 1 |
| The kernel repacks every code on every search call, and the index holds one byte per code. | `in_memory_bytes_per_vec` 520 for a 196-byte cell; `repack4` runs inside `search`. | 2 |
| Uniform bits lose at both ends of the byte axis. | Wikipedia 1024-d: d512 x 4 bits beats d1024 x 2 bits at equal bytes (single-pass 0.938 vs 0.886); PCA+RaBitQ at d512 x 2 bits (148 B) beats tq-pro d256 x 4 bits (132 B), 0.997 vs 0.985, the arm's only loss. | 3 |
| tq-pro builds fastest and scans slowest at scale. | Wikipedia 10M, 4 threads: 120 to 420 ms per query against 43 to 77 ms for rabitqlib IVF; build 300 to 850 s against 3,000 to 6,000 s. | 4 |
| Coding residuals to a centroid is worth 4 to 24 points single-pass at 1 bit. | RaBitQ IVF vs flat RaBitQ on every arm (GloVe 0.359 vs 0.275, deep-image 0.411 vs 0.178). tq-pro's IVF partitions but codes around the global mean. | 4 |
| "Clearly above RaBitQ at matched bytes" is not what public data shows. | C1 MIXED (15 wins, 44 ties, 6 losses); C2 HOLDS at the limit. | 5 |

## Rules the work runs under

- **Nothing executes on the laptop.** Tests and benchmarks run on Atlas in a
  fresh clone (`/home/claude/tqp-v3`, its own venv), capped at 8 threads and
  `nice 19` while the sealed BGP campaign occupies the machine (its schedule
  bar is 3 s; contention is a way to void it).
- **The running campaign is not touched.** No ConfigMap edit, no volume write,
  no new pods until the registered pool reports done. New harness code ships
  under a new ConfigMap name.
- **Every phase ends green.** The full test suite passes at the end of each
  phase, on Atlas, and the phase is one commit or a short series with the
  reason in the message.
- **Every measured claim is preregistered before its data exists**, with the
  rules of `benchmarks/rabitq_public/score.py` (paired bootstrap over queries,
  BEATS / TIES / LOSES) reused rather than restated.
- **Results are reported as returns.** A phase whose measurement comes back
  flat is recorded flat; the design does not move because of it.

## Phase 0 — ground

Branch `feat/scan-v3` from `master`. Clone on Atlas, build the kernel, run the
suite once to record the baseline count. Deliverable: the baseline number in
this file's log.

## Phase 1 — release the kernel fix

The v2 kernel (`3d96506`) is a correctness fix that no user has. Work:

- `CHANGELOG.md`: an entry under the unreleased 2.0.0a3 heading that states
  the defect (uint16 wrap above 257 dims, which vectors it hit, the measured
  recall it cost), the fix, and the regression test that pins it
  (`tests/test_adc_kernel.py::test_maximal_sums_do_not_wrap`).
- Wheel build on Atlas as a dry run (`python -m build`), so the owner's
  publish is one command. The owner publishes.

Acceptance: `tests/test_version_consistency.py` green; wheel builds and
installs into a scratch venv with the kernel compiling from the sdist.

## Phase 2 — kernel v3: one representation, scanned in place

The kernel's nibble-blocked layout becomes the index's only in-RAM
representation, packed once at `add`, never repacked at search. Chunks are the
unit of storage and of scanning, so a flat index is one chunk per `add` batch
and an IVF cell is a chunk with a centroid; the same entry point serves both.

Design:

- `turboquant_pro/_adc/adc_scan.cpp`
  - `pack(codes uint8 (n, d)) -> bytes` in the `[nblk][d][16]` layout.
  - `search_chunks(chunks, q_rot, tables, nsym, segs, probes, biases, k)`:
    `chunks` is a list of `(blocked bytes, n, vnorm, vrnorm, segw)`;
    `tables` is `(d, 16)` float32, one symbol table per dim; `nsym (d,)`
    says how many entries each dim uses; `segs (nseg + 1,)` are dim offsets;
    `probes (Q, P)` name the chunks each query scans (`-1` pads) and
    `biases (Q, P)` carry that query's constant for that chunk. One streaming
    top-k per query across every probed chunk. The score is
    `(bias + vnorm * sum_seg segw[n, seg] * (scale_seg * acc_seg + lutbias_seg)) * vrnorm`;
    a uniform index has one segment and `segw` absent.
  - `search_pruned` keeps its contract on the blocked layout (uniform only).
- `turboquant_pro/adc_index.py`
  - `BlockedCodes`: the duck array `PackedCodes` already defines (`shape`,
    `dtype`, `__len__`, `__getitem__`, `__array__`) over the blocked bytes, so
    `index.py`, `sharded_index.py` and `ivf.py` keep working through `_codes`.
  - `ADCIndex` holds chunks; `_codes` stays as the concatenated view, and its
    setter accepts what `index.py` assigns today (an ndarray or a
    `PackedCodes`) and blocks it.
  - The numpy fallback scans the same chunks by unpacking blocks.

Tests (all in `tests/test_adc_kernel.py` and `tests/test_adc_index.py`):
the integer replay reference generalised to per-dim tables and segments;
`N` not a multiple of 32 across several chunks and an empty chunk; a probe
subset equal to the masked flat scan; `_codes` view equality with the uint8
codes; in-RAM bytes per row within 5 percent of `d / 2 + 8`.

Acceptance: the suite green; a 1M-row wiki1024 index at d512 reports the
expected RSS on Atlas; search time per query does not regress against v2.

## Phase 3 — bits that follow the spectrum

`ADCIndex` accepts an `EigenweightedPipeline`. Its segments map onto the
kernel's: each segment has its own rotation, its own Lloyd-Max table, and a
per-vector energy fraction stored as float16 (accounted at 2 bytes).

The allocation rule replaces `_auto_bit_schedule`'s fixed variance cut points:
given eigenvalues `lambda_j` and a bit budget, choose `b_j` in {0, 1, 2, 3, 4}
to minimise `sum_j lambda_j D(b_j)` with `D` the Gaussian Lloyd-Max
distortion (1, 0.3634, 0.1175, 0.03454, 0.009497). The marginal gains are
decreasing, so the greedy allocation is optimal, and since `lambda_j` is
sorted the result is monotone in `j`: the segments are contiguous by
construction, and `b_j = 0` is the truncation the pipeline already does with
`output_dim`. A 1-bit codebook (+-0.7979) is added to `_CODEBOOKS`.

Measured claim, preregistered in `docs/PREREG_spectrum_bits.md` before any
cell runs: at matched stored bytes (the 0.80 to 1.05 window of the public
comparison), the spectrum-allocated index's single-pass recall@10 beats or
ties the best uniform configuration on a 1024-d arm (wiki1024, 1M rows, on
Atlas) and does not lose on GloVe-100, where the spectrum is nearly flat.
Three seeds, the score.py rules.

Acceptance: allocation tests (budget respected, monotone, degenerate spectra);
ADC equality against a numpy reference for a segmented pipeline; the prereg
verdict recorded whichever way it comes.

## Phase 4 — IVF on the v3 kernel, with residual coding

`IVFIndex` is rebuilt on chunks: the coarse quantizer is fitted in PCA space,
rows are sorted by cell so each cell is one chunk, and a search is one
`search_chunks` call with the probed cells as `probes` and
`qbias + q_proj . c_cell` as `biases`. With `residual=True` the codes are of
`(x_p - c) / ||x_p - c||`, `cnorm` is the residual norm, and `vrnorm` is
computed on `c + cnorm * unrotate(cent[codes])`; the lookup table is shared
across cells because the rotation is global, so residual coding costs nothing
at scan time.

Harness: methods `tq_ivf` (uniform bits, residual coding) and, if Phase 3
passes its bar, `tq_spec_ivf`, added to `benchmarks/rabitq_public/cell.py`
and `grid.py` as supplementary cells under Amendment 3 of the public prereg:
the registered `nlist(dataset)`, the same `nprobe` the RaBitQ IVF cells use,
every arm, three seeds, reported beside the registered arm and never
substituted. They run after the registered pool drains, from a new ConfigMap.

Acceptance: `nprobe = nlist` without residuals equals the flat index exactly;
with residuals it matches a numpy reference; recall on a synthetic
mixture-of-clusters corpus is higher with residuals than without at the same
bits; the harness method passes the cell smoke test.

## Phase 5 — say what the public data says

Gated on the campaign's final scoring. `benchmarks/RESULTS_rabitq_public.md`
is generated by `score.py`; the ledger row `embedding_beats_rabitq_ties_opq`
and the README benchmark paragraph are rewritten from it: where tq-pro wins
(the low-byte end on low-dimensional data), where it ties (once rerank
saturates), where it lost (its own kernel, one 132-byte point), and the build
and scan times as measured. The private-LaBSE table stays, labelled as what it
is.

## Log

- 2026-09-17: plan written; branch `feat/scan-v3` cut from `master` at
  `31ba3bf`.
- 2026-09-17: Phase 0. Clone `/home/claude/tqp-v3` on Atlas at `master`
  `de6729a` (the planner merge), venv with the kernel compiled. Baseline:
  1866 passed, 5 failed, 71 skipped. The five failures predate this work and
  share one cause: they expect the kernel, whose lookup table is uint8, to rank
  identically to the exact numpy path (`test_index.py` x3,
  `test_ivf.py::test_probe_all_equals_bruteforce`,
  `test_claims_glove.py::test_replay_small_reproduces_and_gates`). Left as
  found; the table quantization is a separate question this plan does not open.
- 2026-09-17: Phase 2 measured on Atlas, wiki1024 rows 0 to 1M at d512 / 3
  bits, 1,000 held-out queries, 8 threads, both trees on the same venv:

  | | v2 (`de6729a`) | v3 |
  |---|---:|---:|
  | build, ten add() batches | 34.0 s | 28.1 s |
  | search per query, second pass | 18.9 ms | 16.0 ms |
  | index bytes per row | 520 | 264 |
  | RSS added by the index | 0.36 GiB | 0.08 GiB |

  Top-10 neighbours identical on all 1,000 queries. Targeted tests green with
  the three pre-existing `test_index.py` failures unchanged.
- 2026-09-17: Phase 3 code in place (`spectrum.py`, segmented coder, 1-bit
  table for the embedding quantizer, one byte per segment for the energy
  fraction after a first form at two bytes lost 0.12 recall at a 28-byte
  budget on synthetic data). 194 targeted tests green. A synthetic exploration
  before registration is recorded in `docs/PREREG_spectrum_bits.md`.
