# TurboQuant Pro: Open-source TurboQuant for LLM KV cache compression
# Copyright (c) 2026 Andrew H. Bond
# MIT License

"""Learn the observer from the traffic, instead of asking for it (issue #180).

An observer contract (#173) says who reads the data. Asking a person to write
one invites the answer they believe rather than the one their system performs:
the reranker nobody remembers, the analytics job that runs at midnight, the
``k`` that moved from 10 to 50 a quarter ago. The requests themselves are the
evidence, and a trace of them is usually already being written.

This reads such a trace and writes a contract whose consumers and weights
reflect what actually ran. Three properties make the result usable as
evidence rather than as a guess.

**It abstains on thin evidence.** A consumer seen fewer times than the
threshold is not given a weight; it is listed as abstained with its count, so
a rare reader is visible as a question rather than absent as a fact. The same
holds for a metric the consumer registry does not know: it is reported by
name, never mapped onto a neighbour.

**It states its coverage.** The record says how many lines were read, how many
were unparseable, what fraction of the parsed traffic the retained consumers
carry, and the span of timestamps it saw. A contract learned from an hour of
one weekday is a different claim from one learned from a month, and only the
record can say which this is.

**It writes a contract that validates.** The output goes through
``ObserverContract.validate``, so a learned contract fails the same way a
hand-written one does rather than arriving subtly malformed.

The trace is JSON Lines, one request per line. The reader is liberal about
spelling because traces are written by whatever was already logging:

    {"consumer": "topk_cosine", "config": {"k": 10}, "ts": "...", "stratum": "en"}
    {"metric": "cosine", "k": 50}                     # metric + k, no prefix
    {"consumer": "read_operator", "provider": "attention_analytic"}

A record's configuration is part of its identity: ``topk_cosine`` at ``k=10``
and at ``k=50`` are two readers, weighted separately, because they are.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field

DEFAULT_MIN_COUNT = 20
CONFIG_KEYS = ("k", "provider", "metric", "rerank", "nprobe")

__all__ = [
    "DEFAULT_MIN_COUNT",
    "WorkloadSummary",
    "read_trace",
    "summarize",
    "learn_contract",
]


def _metric_of(rec: dict) -> str | None:
    """The registered consumer metric this record names, or None."""
    for key in ("consumer", "metric_name", "consumer_metric"):
        v = rec.get(key)
        if isinstance(v, str) and v:
            return v
    m = rec.get("metric")
    if isinstance(m, str) and m:
        # a bare distance name is a top-k retrieval consumer by that metric
        return (
            m
            if m.startswith(("topk_", "read_", "attention_", "declared"))
            else f"topk_{m}"
        )
    return None


def _config_of(rec: dict) -> dict:
    cfg = rec.get("config")
    cfg = dict(cfg) if isinstance(cfg, dict) else {}
    for key in CONFIG_KEYS:
        if key not in cfg and key in rec and not isinstance(rec.get(key), (dict, list)):
            cfg[key] = rec[key]
    # a bare 'metric' belongs to the consumer's name, not its configuration
    cfg.pop("metric", None)
    return cfg


def _key(metric: str, cfg: dict) -> str:
    return metric + "|" + json.dumps(cfg, sort_keys=True, separators=(",", ":"))


@dataclass
class WorkloadSummary:
    lines: int
    parsed: int
    unparseable: int
    unnamed: int
    counts: dict
    configs: dict
    strata: dict
    first_ts: str | None
    last_ts: str | None
    min_count: int
    retained: list = field(default_factory=list)
    abstained: list = field(default_factory=list)
    unregistered: list = field(default_factory=list)

    @property
    def retained_share(self) -> float:
        kept = sum(self.counts[k] for k in self.retained)
        return kept / self.parsed if self.parsed else 0.0

    def as_dict(self) -> dict:
        return {
            "schema": "turboquant-pro/workload-summary",
            "schema_version": 1,
            "lines": self.lines,
            "parsed": self.parsed,
            "unparseable": self.unparseable,
            "records_without_a_consumer": self.unnamed,
            "distinct_readers": len(self.counts),
            "min_count": self.min_count,
            "retained": [
                {
                    "metric": self.configs[k][0],
                    "config": self.configs[k][1],
                    "count": self.counts[k],
                    "weight": self.counts[k] / self.parsed if self.parsed else 0.0,
                }
                for k in self.retained
            ],
            "abstained": [
                {
                    "metric": self.configs[k][0],
                    "config": self.configs[k][1],
                    "count": self.counts[k],
                    "reason": f"seen {self.counts[k]} times, under the "
                    f"{self.min_count} needed to weigh it",
                }
                for k in self.abstained
            ],
            "unregistered": list(self.unregistered),
            "retained_share_of_traffic": self.retained_share,
            "strata": dict(self.strata),
            "first_timestamp": self.first_ts,
            "last_timestamp": self.last_ts,
        }

    def explain(self) -> str:
        L = [
            "WORKLOAD",
            f"  {self.parsed} requests parsed of {self.lines} lines"
            + (f", {self.unparseable} unparseable" if self.unparseable else "")
            + (f", {self.unnamed} naming no consumer" if self.unnamed else ""),
        ]
        if self.first_ts or self.last_ts:
            L.append(f"  span {self.first_ts or '?'} to {self.last_ts or '?'}")
        L.append(f"  {len(self.counts)} distinct readers; threshold {self.min_count}")
        L.append("")
        L.append("retained:")
        for k in self.retained:
            metric, cfg = self.configs[k]
            share = self.counts[k] / self.parsed if self.parsed else 0.0
            L.append(
                f"  {metric} {json.dumps(cfg, sort_keys=True)}  "
                f"{self.counts[k]} ({share * 100:.1f}%)"
            )
        if not self.retained:
            L.append("  <none cleared the threshold>")
        if self.abstained:
            L.append("abstained (too rare to weigh, not absent):")
            for k in self.abstained:
                metric, cfg = self.configs[k]
                L.append(
                    f"  {metric} {json.dumps(cfg, sort_keys=True)}  {self.counts[k]}"
                )
        if self.unregistered:
            L.append("not a registered consumer metric (reported, never mapped):")
            for name in self.unregistered:
                L.append(f"  {name}")
        L.append("")
        L.append(
            f"retained readers carry {self.retained_share * 100:.1f}% of parsed traffic"
        )
        return "\n".join(L)


def read_trace(lines) -> list:
    """Parse JSON Lines into records, keeping the unparseable count."""
    records, bad = [], 0
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            bad += 1
            continue
        if isinstance(rec, dict):
            records.append(rec)
        else:
            bad += 1
    return records, bad


def summarize(
    records: list,
    *,
    lines: int | None = None,
    unparseable: int = 0,
    min_count: int = DEFAULT_MIN_COUNT,
) -> WorkloadSummary:
    """Count the readers a trace performed, and decide which to weigh."""
    from turboquant_pro import consumers as consumers_mod

    counts: Counter = Counter()
    configs: dict = {}
    strata: Counter = Counter()
    unnamed = 0
    first_ts = last_ts = None
    for rec in records:
        metric = _metric_of(rec)
        if not metric:
            unnamed += 1
            continue
        cfg = _config_of(rec)
        k = _key(metric, cfg)
        counts[k] += 1
        configs[k] = (metric, cfg)
        st = rec.get("stratum")
        if isinstance(st, str) and st:
            strata[st] += 1
        ts = rec.get("ts") or rec.get("timestamp")
        if isinstance(ts, str) and ts:
            first_ts = ts if first_ts is None or ts < first_ts else first_ts
            last_ts = ts if last_ts is None or ts > last_ts else last_ts

    parsed = sum(counts.values())
    retained, abstained, unregistered = [], [], []
    for k, n in counts.most_common():
        metric = configs[k][0]
        try:
            consumers_mod.get_consumer(metric)
        except KeyError:
            if metric not in unregistered:
                unregistered.append(metric)
            continue
        (retained if n >= min_count else abstained).append(k)
    return WorkloadSummary(
        lines=lines if lines is not None else len(records),
        parsed=parsed,
        unparseable=unparseable,
        unnamed=unnamed,
        counts=dict(counts),
        configs=configs,
        strata=dict(strata),
        first_ts=first_ts,
        last_ts=last_ts,
        min_count=min_count,
        retained=retained,
        abstained=abstained,
        unregistered=unregistered,
    )


def learn_contract(
    summary: WorkloadSummary,
    *,
    observer: str,
    target: str = "embedding",
    source: dict | None = None,
    requirements: dict | None = None,
    budget: dict | None = None,
):
    """An :class:`~turboquant_pro.observer.ObserverContract` from what the
    trace performed, weighted by frequency.

    Raises:
        ValueError: no reader cleared the threshold, so there is nothing to
            declare; the summary says what was seen instead.
    """
    from turboquant_pro.observer import ConsumerClause, ObserverContract

    if not summary.retained:
        raise ValueError(
            "no reader in this trace cleared the threshold "
            f"({summary.min_count}); {len(summary.counts)} distinct readers seen. "
            "Lower --min-count only if a thinner sample is acceptable as evidence"
        )
    clauses = []
    for k in summary.retained:
        metric, cfg = summary.configs[k]
        clauses.append(
            ConsumerClause(
                name=f"{metric}-{summary.counts[k]}",
                metric=metric,
                config=cfg,
                weight=summary.counts[k] / summary.parsed,
            )
        )
    src = dict(source or {})
    src.setdefault("learned_from", "workload trace")
    src.setdefault("requests", summary.parsed)
    if summary.first_ts:
        src.setdefault("first_request", summary.first_ts)
    if summary.last_ts:
        src.setdefault("last_request", summary.last_ts)
    src.setdefault("retained_share_of_traffic", round(summary.retained_share, 4))
    return ObserverContract(
        observer=observer,
        consumers=tuple(clauses),
        target=target,
        source=src,
        requirements=dict(requirements or {}),
        budget=dict(budget or {}),
    )
