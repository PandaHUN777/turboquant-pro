# Design — the value-of-observation planner

Issue #181, in the Observation Theory family (#183). **Not implemented.** This
document exists because the honest version of the feature needs measurements
the library does not yet collect, and writing that down is worth more than
shipping a planner that invents them.

## 0. What the request asks for

Optimise bits, compute, reranking and I/O together against the downstream
value of another observation, rather than choosing a codec under a byte budget
alone. The planner today (#169) takes a byte or bit budget and a quality
floor, measures candidates on the consumer's metric, and picks a winner. It
cannot trade a wider candidate set against a fatter code, or a refinement
layer against a cold-tier fetch, because it prices only one resource.

## 1. Why a naive version would be dishonest

To say "this plan costs less" the tool must convert resource use into one
number. Four resources are in play and only the first is free to measure:

| resource | measurable today | needs |
|---|---|---|
| bytes stored per row | yes, exactly (`stored_bytes_per_row`) | nothing |
| bytes scanned per query | yes, as a count (rows × row bytes × scan fraction from `IVFIndex.stats()`) | nothing for the count |
| bytes fetched per query for rerank | yes, as a count (candidates × original row bytes) | nothing for the count |
| **seconds** for any of the above | **no** | a measured scan rate and a measured fetch latency **on the target hardware** |

The scan rate is not portable: the v3 kernel's measured 16.0 ms per query on
Wikipedia-1024 at 1M rows is an Atlas number at eight threads, and the
campaign's own plan records already carry a hardware fingerprint because costs
are only valid for one. A cold-tier fetch latency is a property of the
deployment's storage, not of this library. A planner that assumed either would
produce a confident total that is wrong by whatever the deployment differs by,
and the error would be invisible because the output is a single number.

The value side is worse. "The downstream value of another observation" is a
business quantity: what one point of recall@10 is worth against one millisecond
of latency. Nothing in a corpus determines it. A default here would not be a
modelling simplification, it would be a fabrication presented as a
recommendation.

## 2. The honest shape

Two inputs the caller supplies, and one the library already has.

1. **Measured operating points**, not predicted ones. A plan record (#169) or
   a campaign scorer report gives (configuration, recall, stored bytes) rows
   that were measured, not modelled. The planner optimises over those points.
   When a point is absent the answer is "not measured", the same way the
   byte-window rule reports a gap rather than interpolating.
2. **Declared resource weights**, from the caller: what a stored byte, a
   scanned byte and a fetched byte cost each other in their deployment. A
   caller who does not know can pass none and receive the three counts
   separately, which is a complete answer to "what would this cost me" for
   someone who knows their own storage.
3. **The three counts**, which the library computes exactly: stored, scanned
   and fetched bytes per query for each operating point, from the index
   structure and the probe and rerank settings.

The planner then reports the frontier over (stored, scanned, fetched) among
the points that clear the contract's floor, and, if weights were declared, the
cheapest point and the marginal value of relaxing each resource. Every row is
traceable to a measurement.

```
tqp plan value --points plan_record.json --observer production.tqo \
    --weight stored=1 --weight scanned=0.1 --weight fetched=8
```

## 3. What has to exist first

- **A measured cost record per configuration.** The campaign harness records
  build and search seconds per cell; the library does not record scanned and
  fetched byte counts per query. Adding those counters to `ADCIndex.search`
  and `IVFIndex.search` (behind `return_stats`, which IVF already has) is the
  prerequisite, and it is cheap and exact.
- **A hardware fingerprint on any second-valued number**, which the plan
  record already carries and which this must refuse to cross.
- **Agreement on what a "point" is**, so a plan record, a scorer report and an
  index's own stats can all be read into the same rows.

## 4. Recommendation

Build the byte counters first (a small, exact change), then this planner over
measured points with declared weights. Do not ship a version that converts
bytes to seconds from constants measured on one machine, and do not ship a
default value for a point of recall. The feature's worth is that it makes a
trade visible; a made-up exchange rate would make it invisible again.
