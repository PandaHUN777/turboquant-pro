# Design — certificates expire

Issue #177, the fifth of the Observation Theory family (#183). Phase 1 on
`feat/certificate-validity`.

## 0. Thesis

A rank certificate says that a statement was true for an observer `O` under an
environment `E`: these inputs, this read operator, this calibration sample.
When `O` becomes `O'`, or the data drifts out of the calibration's coverage,
the certificate is not false. It is no longer applicable. Monitoring reports
drift; this is different: it is invalidation, a status with a reason and an
action, computed from what the certificate itself recorded at issue.

The certificate already binds its reference operator by hash, so a changed
operator is detectable; but a hash says only that something changed, not how
much or in which direction. readscope's C-11c measured a consumer's read
operator drifting along a sequence, and the certificate's own `reference`
section exists because two defensible operators for one head differ by 0.3 in
overlap. The certificate should therefore carry enough of the operator to
measure that overlap later, and enough of the certified sample to measure
coverage later, and `tqp verify` should read both.

## 1. What the certificate records at issue (additive `validity` section)

Emitted by `tqp certify --validity`, and by default when `--observer` or
`--reference` is given, since both name an observer the certificate depends
on. `schema_version` stays 1.

| field | content | why |
|---|---|---|
| `issued_for` | the observer contract hash (if any), the reference provider and `operator_sha256` (if any) | the identity of `O` |
| `operator_sketch` | the top-`r` eigenvectors and eigenvalues of the reference operator, `r` the ceiling of its effective rank up to a cap, with the fraction of trace they carry | enough of `P_C` to measure how much of a later operator lies in the certified read subspace |
| `coverage_sketch` | per-channel mean and variance of the certified original sample, and the row count | enough of `E` to measure whether later data sits inside the calibration's coverage, without storing a `D×D` covariance |
| `thresholds` | `min_operator_overlap` (0.85), `max_coverage_divergence` (a diagonal Jeffreys divergence per channel, 0.5) | the numbers the status is decided against, recorded so a reader cannot move them after the fact |

## 2. What `tqp verify` checks (`checks.validity`)

`tqp verify CERT --observer C [--data sample.npy --queries q.npy]`:

1. **source artifact unchanged**: the existing input hashes (with `--original`/`--reconstructed`).
2. **observer unchanged**: the contract hash (from #173).
3. **observer read geometry**: with `--data`, the contract's operator is rebuilt (`refinement.observer_operator`) and its overlap with the sketch is `tr(Uᵀ P' U) / tr(P')`, the fraction of the new operator's sensitivity inside the certified read subspace. Below `min_operator_overlap` the certificate is STALE with reason "consumer read geometry changed" and action REPLAN.
4. **data distribution within coverage**: with `--data`, the diagonal Jeffreys divergence between the sketch's moments and the sample's, averaged per channel. Above the threshold: STALE, reason "data outside calibration coverage", action RECERTIFY.
5. **strata coverage**: not checked in phase 1, reported as `not_checked` so its absence is visible.

The result carries `status` (VALID, STALE, or UNCHECKED when neither `--data`
nor a sketch is available), `reason`, `action`, and the measured numbers.
`verified` keeps its meaning (the certificate is what it says it is);
`applicable` is the new field, and the exit code is 1 when either is false.

```
CERTIFICATE STATUS
  source artifact unchanged         ok
  observer contract unchanged       ok
  observer overlap 0.71 < 0.85      FAIL
  data coverage divergence 0.12     ok
  strata coverage                   not checked
STATUS: STALE   reason: consumer read geometry changed   action: REPLAN
```

## 3. What Phase 1 does not do

- No monitor integration: `QualityMonitor` keeps reporting drift; wiring its
  windows to re-run these checks on a schedule is phase 2.
- No strata checks (phase 2, with the STRATA gates reading a contract).
- No codec-identity check: the certificate does not record which codec
  produced the reconstruction; the plan record does (#169), and binding the
  two is the pipeline composition of #182.

## 4. Phases

1. The `validity` section and the `tqp verify` checks above, with tests that
   turn a passing certificate STALE by rotating the operator, and by shifting
   the data, and keep it VALID otherwise.
2. Monitor integration and strata coverage.
3. Capability discovery (#178) reads the status to decide what an index is
   currently certified for.
