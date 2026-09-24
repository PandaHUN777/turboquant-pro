# The 1T index is built: 500 of 500 servers, 2026-09-24

Read after `HANDOFF_2026-08-04.md`, which this closes for the build phase.

## What is true now

- **500 servers x 400 shards x 5M rows = 10^12 rows are built and cell-assigned**, one
  Linstor volume each (`tqp-fleet-1t-0..499`, `linstor-unl`, 56Gi), plus the shared CephFS volume
  `tqp-fleet-shared` with the bootstrap, global coarse quantizer and staged dependencies.
- Every server reports the same shape in its `BUILD_DONE` line: **2,000,000,000 rows,
  48,009,656,624 index bytes, 24.0 bytes per row** (4-bit codes 12 + cnorm/vrnorm 8 + IVF
  member sidecar 4). Across 500 servers that is **24.0 TB** of hot-tier index.
- Servers 0 to 15 were built by `driver1t.sh` in waves (2026-08-04); 16 to 499 by
  `driver1t_pool.py` from a single pool with no wave barrier, submissions through the
  `burst.submit` NATS flow. The pool driver's state file records `done=484`, `parked=[]`
  (`benchmarks/fleet/record/1t/pool_state.json`).
- **The last six servers (444 to 448 and 476)** sat parked from 2026-08-12 because their
  single-replica volumes were hostage to an offline node. On 2026-09-24 they were rebuilt from
  seed per the doctrine in `pvc_1t_tmpl.yaml`: delete the claim, recreate it under the same name,
  let the driver re-issue. The six new volumes took about ten minutes to bind (not the 31 s seen in
  August); all six builds then finished on their **first attempt**, with no enforcement kill and no
  recycle, in 2 h 32 m to 3 h 49 m each (pod start to exit 0), at 742 to 805 MiB peak memory inside the 1 CPU / 2 GiB
  enforcement-exempt envelope. Pod logs are in `benchmarks/fleet/record/1t/`.
- Every build ran in the exempt envelope by construction (`write_shard_streaming` over
  `gen_block_bands`, commit `8f42543` and the four memory fixes that followed), which is what
  made a 10^12-row build survivable on a cluster that deletes over-requesting pods.

## What is not done, deliberately

No post-build phase has run: no query cache, no exact full-scan reference, no routed-IVF pass and
no merge/score. **There is no 1T recall measurement**, and nothing here should be read as one. At
100B the exact reference phase alone took seven waves of eight pods at 6 to 11 hours a wave; at 1T
that is about 12,500 CPU-hours (the figure in `RESEARCH_ROADMAP.md`), three to four weeks at
eight pods wide or about four days at forty-eight. It is a run to announce on the NRP channel
first, not to start quietly, and the owner chose on 2026-09-24 to record the build as the
milestone and defer the measurement.

## What this is evidence of

A scaling-mechanics result and nothing more: that the content-addressed, seed-regenerated,
per-shard-resumable build reaches 10^12 rows at 24.0 bytes per row on a shared cluster, inside
its enforcement-exempt pod class, with a lost volume recoverable from its seed in under four
hours. The corpus is `gen_block`, a rank-16 Gaussian at dim 32 (see `FLEET_CORPUS_GEOMETRY.md`),
so it says nothing about recall on realistic embeddings; the realistic-data point remains
`real_pilot_15M_wiki1024.json`.

## The 27.3 TiB

All 500 volumes remain Bound and accrue on the shared cluster. They hold the built index and are
worth keeping only if the measurement will be run. Releasing them is the owner's call; the index
is rebuildable from seed in about 3.5 hours per server at the pool's width.

## Record

| file | what |
|---|---|
| `benchmarks/fleet/record/1t/pool_state.json` | the pool driver's final state, `done=484`, `parked=[]` |
| `benchmarks/fleet/record/1t/driver1t_pool_finish.log` | the 2026-09-24 driver session that finished the six |
| `benchmarks/fleet/record/1t/tqp-fleet-1t-build-{444..448,476}.log` | the six pods' logs, each ending `BUILD_DONE` |
