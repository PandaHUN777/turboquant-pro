# TurboQuant Pro: Open-source TurboQuant for LLM KV cache compression
# Copyright (c) 2026 Andrew H. Bond. MIT License.
"""Workload-learned observers (issue #180): the weights recover the mixture,
a rare reader is abstained on rather than dropped, and a metric the registry
does not know is reported rather than mapped."""

from __future__ import annotations

import json

import pytest

from turboquant_pro.cli import main
from turboquant_pro.observer import load_contract
from turboquant_pro.workload import (
    learn_contract,
    read_trace,
    summarize,
)


def _trace(mixture, rare=None, ts=True):
    """A trace with a known mixture: {(metric, k): count}."""
    lines = []
    i = 0
    for (metric, k), n in mixture.items():
        for _ in range(n):
            rec = {"consumer": metric, "config": {"k": k}}
            if ts:
                rec["ts"] = (
                    f"2026-09-18T{i // 3600:02d}:{(i // 60) % 60:02d}:{i % 60:02d}Z"
                )
            lines.append(json.dumps(rec))
            i += 1
    lines.extend(rare or [])
    return lines


# ---- parsing ------------------------------------------------------------------


def test_unparseable_lines_are_counted_not_ignored():
    lines = [
        "{}",
        "not json",
        "[1,2]",
        "",
        "# a comment",
        '{"consumer": "topk_cosine"}',
    ]
    records, bad = read_trace(lines)
    assert bad == 2
    assert len(records) == 2


def test_spellings_a_trace_might_use_all_resolve():
    lines = [
        json.dumps({"consumer": "topk_cosine", "config": {"k": 10}}),
        json.dumps({"metric": "cosine", "k": 10}),
        json.dumps({"consumer": "read_operator", "provider": "identity"}),
    ]
    records, _ = read_trace(lines)
    s = summarize(records, min_count=1)
    metrics = {s.configs[k][0] for k in s.retained}
    assert metrics == {"topk_cosine", "read_operator"}
    # the first two spellings are the same reader and are counted together
    topk = next(k for k in s.retained if s.configs[k][0] == "topk_cosine")
    assert s.counts[topk] == 2
    assert s.configs[topk][1] == {"k": 10}


def test_records_naming_no_consumer_are_counted():
    records, _ = read_trace([json.dumps({"latency_ms": 3}), json.dumps({"k": 10})])
    s = summarize(records, min_count=1)
    assert s.unnamed == 2 and s.parsed == 0


# ---- the mixture --------------------------------------------------------------


def test_the_weights_recover_a_known_mixture():
    records, _ = read_trace(_trace({("topk_cosine", 10): 750, ("topk_l2", 10): 250}))
    s = summarize(records, min_count=20)
    c = learn_contract(s, observer="svc")
    w = c.normalized_weights()
    assert len(c.consumers) == 2
    by_metric = {x.metric: w[x.label] for x in c.consumers}
    assert by_metric["topk_cosine"] == pytest.approx(0.75, abs=0.01)
    assert by_metric["topk_l2"] == pytest.approx(0.25, abs=0.01)
    assert c.primary().metric == "topk_cosine"
    assert c.validate() == []


def test_the_same_metric_at_two_configurations_is_two_readers():
    records, _ = read_trace(
        _trace({("topk_cosine", 10): 500, ("topk_cosine", 50): 300})
    )
    s = summarize(records, min_count=20)
    c = learn_contract(s, observer="svc")
    assert len(c.consumers) == 2
    assert {x.config["k"] for x in c.consumers} == {10, 50}


def test_a_rare_reader_is_abstained_on_and_stays_visible():
    rare = [json.dumps({"consumer": "topk_l2", "config": {"k": 10}}) for _ in range(3)]
    records, _ = read_trace(_trace({("topk_cosine", 10): 500}, rare=rare))
    s = summarize(records, min_count=20)
    assert len(s.retained) == 1 and len(s.abstained) == 1
    d = s.as_dict()
    assert d["abstained"][0]["metric"] == "topk_l2"
    assert d["abstained"][0]["count"] == 3
    assert "under the 20 needed" in d["abstained"][0]["reason"]
    assert "not absent" in s.explain()
    c = learn_contract(s, observer="svc")
    assert [x.metric for x in c.consumers] == ["topk_cosine"]


def test_an_unregistered_metric_is_reported_never_mapped():
    rare = [json.dumps({"consumer": "topk_manhattan"}) for _ in range(50)]
    records, _ = read_trace(_trace({("topk_cosine", 10): 100}, rare=rare))
    s = summarize(records, min_count=20)
    assert s.unregistered == ["topk_manhattan"]
    assert all(s.configs[k][0] != "topk_manhattan" for k in s.retained + s.abstained)
    assert "never mapped" in s.explain()
    c = learn_contract(s, observer="svc")
    assert [x.metric for x in c.consumers] == ["topk_cosine"]


def test_nothing_clearing_the_threshold_raises_rather_than_inventing():
    records, _ = read_trace(_trace({("topk_cosine", 10): 3}))
    s = summarize(records, min_count=20)
    with pytest.raises(ValueError, match="cleared the threshold"):
        learn_contract(s, observer="svc")


def test_the_contract_records_the_sample_it_was_learned_from():
    records, _ = read_trace(_trace({("topk_cosine", 10): 100}))
    s = summarize(records, min_count=20)
    c = learn_contract(s, observer="svc")
    assert c.source["requests"] == 100
    assert c.source["learned_from"] == "workload trace"
    assert c.source["first_request"] < c.source["last_request"]
    assert c.source["retained_share_of_traffic"] == 1.0


def test_the_retained_share_reports_what_was_left_out():
    rare = [json.dumps({"consumer": "topk_l2", "config": {"k": i}}) for i in range(40)]
    records, _ = read_trace(_trace({("topk_cosine", 10): 60}, rare=rare))
    s = summarize(records, min_count=20)
    # 40 singleton readers, none weighable
    assert s.retained_share == pytest.approx(0.6)
    assert len(s.abstained) == 40


def test_strata_and_span_are_recorded():
    lines = [
        json.dumps(
            {"consumer": "topk_cosine", "stratum": "en", "ts": "2026-09-18T01:00:00Z"}
        ),
        json.dumps(
            {"consumer": "topk_cosine", "stratum": "fr", "ts": "2026-09-18T02:00:00Z"}
        ),
    ]
    records, _ = read_trace(lines)
    s = summarize(records, min_count=1)
    assert s.strata == {"en": 1, "fr": 1}
    assert s.first_ts.endswith("01:00:00Z") and s.last_ts.endswith("02:00:00Z")


# ---- CLI -----------------------------------------------------------------------


def test_cli_learn_writes_a_valid_contract(tmp_path, capsys):
    trace = tmp_path / "w.jsonl"
    trace.write_text(
        "\n".join(_trace({("topk_cosine", 10): 200, ("topk_l2", 10): 100})),
        encoding="utf-8",
    )
    out = tmp_path / "learned.json"
    summary = tmp_path / "summary.json"
    rc = main(
        [
            "observer",
            "learn",
            str(trace),
            "--name",
            "prod",
            "--out",
            str(out),
            "--summary",
            str(summary),
            "--floor",
            "0.99",
            "--max-bytes-per-vector",
            "128",
        ]
    )
    assert rc == 0
    c = load_contract(str(out))
    assert c.validate() == []
    assert c.observer == "prod"
    assert c.requirements["floor"]["minimum"] == 0.99
    assert c.budget["max_bytes_per_vector"] == 128
    d = json.loads(summary.read_text(encoding="utf-8"))
    assert d["schema"] == "turboquant-pro/workload-summary"
    assert d["parsed"] == 300
    err = capsys.readouterr().err
    assert "WORKLOAD" in err and "retained" in err
    # the contract exists now, so a second run must not clobber it silently
    assert (
        main(["observer", "learn", str(trace), "--name", "prod", "--out", str(out)])
        == 2
    )
    assert "--force" in capsys.readouterr().err


def test_cli_learn_exits_one_when_nothing_clears_the_threshold(tmp_path, capsys):
    trace = tmp_path / "w.jsonl"
    trace.write_text("\n".join(_trace({("topk_cosine", 10): 2})), encoding="utf-8")
    out = tmp_path / "learned.json"
    assert (
        main(["observer", "learn", str(trace), "--name", "p", "--out", str(out)]) == 1
    )
    assert "cleared the threshold" in capsys.readouterr().err
    assert not out.exists()


def test_cli_learn_refuses_a_missing_trace(tmp_path, capsys):
    assert (
        main(
            [
                "observer",
                "learn",
                str(tmp_path / "nope.jsonl"),
                "--name",
                "p",
                "--out",
                str(tmp_path / "o.json"),
            ]
        )
        == 2
    )
    assert "cannot read" in capsys.readouterr().err
