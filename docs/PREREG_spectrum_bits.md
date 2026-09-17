# Pre-registration — bits that follow the spectrum, at matched bytes

**Status: REGISTERED 2026-09-17, before any registered cell ran.** Results land in
`benchmarks/RESULTS_spectrum_bits.md`; this file is never edited to fit them. Changes
after registration go in the amendment log (section 7) with a date and a reason.

> **The question.** The interim scoring of the public RaBitQ comparison
> (`docs/PREREG_rabitq_public.md`, 2026-09-17) showed uniform bit widths losing at both
> ends of the byte axis on 1024-d and 1536-d embeddings: at equal bytes, half the dims
> at 4 bits beat all of them at 2, and more dims at 2 bits beat fewer at 4 when bytes
> are scarce. `turboquant_pro.spectrum` allocates widths along the PCA spectrum instead
> (`docs/PLAN_scan_v3.md`, Phase 3). Does that raise single-pass recall@10 at the same
> stored bytes, on the same data?

---

## 0. Claims under test

- **S1** — on the 1024-d arm, at matched stored bytes, the spectrum allocation's
  single-pass recall@10 beats the uniform configuration at that byte level.
- **S2** — on the 100-d arm, whose spectrum is nearly flat, the spectrum allocation does
  not lose to the uniform configuration at matched bytes.

**Prior knowledge, stated so it can be discounted.** The direction of S1 is what the
interim public numbers suggest and what `sum_j lambda_j D(b_j)` predicts; no spectrum
cell has been run on either arm. `tests/test_spectrum.py` checks the allocation and the
scan on synthetic data (3,000 to 6,000 rows); its recall assertion is a sanity floor
(`>= uniform - 0.05`), not a measurement. Two registered uniform configurations on
`wiki1024-10m` exist in the public campaign at 10M rows with a different query set;
they are not reused here.

One exploration ran before registration, on synthetic Gaussian corpora of 20,000 rows
with a geometric spectrum (Atlas, 2026-09-17 23:09 UTC, kernel path, single-pass
recall@10 over 500 queries, one seed). Against the *best* uniform configuration at
each byte level, which is the comparison this design makes: on steep spectra (decay
0.94 at 128-d, 0.985 at 512-d) the allocation won at the low and middle levels by
0.10 to 0.25 (for example 0.667 to 0.819 at 100 bytes on the 512-d corpus) and was
within 0.01 either way at the level where the uniform 4-bit full-dimension index
already sits; on a nearly flat spectrum (decay 0.99) it won where the best uniform
configuration was 3 or 4 bits on few dims and lost by 0.01 to 0.04 where the best
uniform configuration was 2 bits on many dims. Two things follow for this design and
are fixed before any registered cell: the comparison is against the best uniform
configuration at a level, and S2 (the flat 100-d arm) is registered as a claim that
can fail. The exploration used two bytes and then one byte per segment; one byte is
what ships.

## 1. Arms

| arm | corpus | dim | rows | queries | ground truth |
|---|---|---:|---:|---:|---|
| `wiki1024-1m` | `/archive/tqp_real/wiki1024/part_000.npy` rows 0 to 999,999 (Cohere Wikipedia 1024-d, as staged for the public campaign) | 1024 | 1,000,000 | first 1,000 rows of `part_001.npy` (disjoint from the corpus) | exact cosine top-10 over the corpus, computed once and stored |
| `glove-100-angular` | ann-benchmarks `train` (`/archive/cache/glove-100-angular.hdf5`) | 100 | 1,183,514 | first 1,000 of `test` | provided `neighbors` |

Both run on Atlas (2 x Xeon E5-2690 v3), 8 threads, the v3 kernel compiled, in the
clone `/home/claude/tqp-v3` at the commit recorded in the results.

## 2. Cells

A cell is `(arm, byte level, method, seed)`. Byte levels are the stored bytes of the
uniform tq-pro configurations of the public grid on these dims (`out_dim * bits / 8`
rounded up, plus 4 for the norm):

| arm | uniform configurations (out_dim, bits) -> bytes |
|---|---|
| `wiki1024-1m` | (256, 3) 100; (256, 4) 132; (512, 3) 196; (512, 4) 260 and (1024, 2) 260; (1024, 3) 388; (1024, 4) 516 |
| `glove-100-angular` | (100, 2) 29; (100, 3) 42; (100, 4) 54 |

At 260 bytes the 1024-d arm has two uniform configurations; the comparison there is
against whichever has the higher mean single-pass recall (the same "best in window" rule
the public scorer uses).

- **`uniform`** — `PCAMatryoshka(output_dim).fit(train)`, `with_quantizer(bits, seed)`,
  `ADCIndex`, exactly the public campaign's `m_tq`.
- **`spectrum`** — `PCAMatryoshka(dim).fit(train)` for the full spectrum;
  `spectrum.plan_for_bytes(eigenvalues, B, choices=(0, 1, 2, 3, 4))` gives
  `out_dim` (the dims with a non-zero width) and the segment schedule;
  `PCAMatryoshka(out_dim).fit(train)`, `with_weighted_quantizer(schedule, seed)`,
  `ADCIndex`. Stored bytes = codes packed at each segment's width + 4 (norm) + 1 per
  segment (the energy fraction, one byte), `ADCIndex.stored_bytes_per_row`, and must
  not exceed `B` (section 5).

Training sample: 100,000 corpus rows drawn without replacement with `seed`, the same
draw for both methods at a seed. Seeds 0, 1, 2. Search: 1,000 queries, `k = 10` single
pass; `+rerank x5` = the top 50 rescored by exact cosine on the originals.

Cells: 1024-d arm 7 uniform + 6 spectrum, 100-d arm 3 + 3, three seeds: **57 cells**.

## 3. Endpoints

- **Primary:** single-pass recall@10, the ADC ranking itself, where the widths act.
- **Reported:** +rerank x5 recall@10; each cell's stored bytes, `out_dim`, segment
  schedule and segment count; build and search seconds; the kernel's per-query time.

## 4. Verdict rules (from `benchmarks/rabitq_public/score.py`, unchanged)

Per byte level: the three seeds' per-query hits are averaged; paired per-query
difference (spectrum minus uniform), percentile bootstrap over the 1,000 queries,
10,000 resamples, seed 0, 95 percent interval `[lo, hi]`, mean `m`:
BEATS if `lo > 0` and `m >= 0.005`; LOSES if `hi < 0` and `m <= -0.005`;
TIES if `lo >= -0.01` and `hi <= 0.01`; otherwise INCONCLUSIVE.

- **S1** (1024-d, 6 byte levels): HOLDS if BEATS at >= 4 levels and LOSES at none;
  REFUTED if LOSES at >= 2 levels or BEATS at none; otherwise MIXED.
- **S2** (100-d, 3 byte levels): HOLDS if LOSES at none; REFUTED otherwise.

Both directions are pre-committed. A flat curve on the 1024-d arm means the per-row
fractions and the coarser tail cost what the leading dims gain, and the plan's Phase 3
records that. A loss on GloVe means a byte per segment is not free on a flat spectrum,
and the default stays uniform there.

## 5. Manipulation checks

- **MC1 (void).** A spectrum cell whose `stored_bytes_per_row` exceeds its byte level
  is void, and the level is scored as NO-CONFIG.
- **MC2 (void).** A cell whose ground truth or query set differs from the stored one
  (hash recorded in the results) is void.
- **MC3 (reported).** Segment count per spectrum cell; the allocation's expected
  distortion `sum lambda_j D(b_j) / sum lambda_j` beside the uniform configuration's.

## 6. Declared confounds

1. The uniform arm pays 4 bytes per row for the norm; the spectrum arm pays 4 plus 1
   per segment (at most 4 segments). Both are charged; a level where the overhead
   forces a narrower tail than the uniform width is the design paying its own cost.
2. The kernel's uint8 lookup tables round every lookup for both methods; a segmented
   scan adds per-segment biases in float32. The integer replay test pins the
   arithmetic; the endpoint is measured through it.
3. `wiki1024-1m` is the first million rows of a 10M staged corpus, not a random sample;
   both methods see the same rows.
4. Ground truth for `wiki1024-1m` is exact cosine computed here, so the +rerank x5
   endpoint on that arm can reach 1.0 by construction of the rerank; that is why the
   primary endpoint is single-pass.

## 7. Amendment log

(none)
