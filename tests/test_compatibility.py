# TurboQuant Pro: Open-source TurboQuant for LLM KV cache compression
# Copyright (c) 2026 Andrew H. Bond. MIT License.
"""Cross-observer compatibility (issue #179): a code is not good on its own,
only good for a reader. The matrix says which readers can share one."""

from __future__ import annotations

import json

import numpy as np
import pytest

from turboquant_pro.cli import main
from turboquant_pro.observer import ObserverContract
from turboquant_pro.refinement import (
    ObserverGeometry,
    compatibility_matrix,
)

D = 32


def _projector(lo, hi):
    P = np.zeros((D, D))
    P[lo:hi, lo:hi] = np.eye(hi - lo)
    return P


def _corpus(seed=0, n=2000):
    rng = np.random.default_rng(seed)
    return (rng.standard_normal((n, D)) * np.linspace(3.0, 0.5, D)).astype(np.float32)


def test_the_diagonal_is_each_observers_own_optimum():
    obs = [
        ObserverGeometry("search", _projector(0, 8), 16),
        ObserverGeometry("anomaly", _projector(16, 24), 16),
    ]
    m = compatibility_matrix(_corpus(), obs)
    for label in m.labels:
        assert m.ratio[label][label] == pytest.approx(1.0)
        assert m.safe[label][label] is True
        assert m.distortion[label][label] == pytest.approx(
            m.own[label]["distortion_fraction"]
        )


def test_disjoint_readers_cannot_share_a_code():
    obs = [
        ObserverGeometry("search", _projector(0, 8), 16),
        ObserverGeometry("anomaly", _projector(16, 24), 16),
    ]
    m = compatibility_matrix(_corpus(), obs)
    assert m.overlap["search"]["anomaly"] == pytest.approx(0.0)
    assert m.safe["search"]["anomaly"] is False
    assert m.safe["anomaly"]["search"] is False
    assert m.ratio["search"]["anomaly"] > 10
    pairs = m.unsafe_pairs()
    assert ("search", "anomaly") in pairs and ("anomaly", "search") in pairs


def test_identical_readers_share_a_code_safely():
    obs = [
        ObserverGeometry("a", _projector(0, 8), 16),
        ObserverGeometry("b", _projector(0, 8), 16),
    ]
    m = compatibility_matrix(_corpus(), obs)
    assert m.unsafe_pairs() == []
    assert m.overlap["a"]["b"] == pytest.approx(1.0)
    assert "within" in m.explain()


def test_a_code_for_a_reader_that_reads_everything_serves_a_narrower_one():
    # allocating against the identity spends bits on every direction, so a
    # reader of a subspace finds what it needs; the reverse does not hold
    obs = [
        ObserverGeometry("narrow", _projector(0, 8), 16),
        ObserverGeometry("everything", np.eye(D), 16),
    ]
    m = compatibility_matrix(_corpus(), obs)
    assert m.safe["everything"]["narrow"] is True
    assert m.safe["narrow"]["everything"] is False


def test_the_report_serialises_and_reads():
    obs = [
        ObserverGeometry("search", _projector(0, 8), 16),
        ObserverGeometry("anomaly", _projector(16, 24), 16),
    ]
    m = compatibility_matrix(_corpus(), obs)
    d = m.as_dict()
    assert d["schema"] == "turboquant-pro/compatibility-matrix"
    json.dumps(d)
    text = m.explain()
    assert "CROSS-OBSERVER COMPATIBILITY" in text and "UNSAFE" in text


def test_budget_defaults_to_the_smallest_and_is_overridable():
    obs = [
        ObserverGeometry("a", _projector(0, 8), 12),
        ObserverGeometry("b", _projector(0, 8), 40),
    ]
    assert compatibility_matrix(_corpus(), obs).budget_bytes == 12
    assert compatibility_matrix(_corpus(), obs, budget_bytes=24).budget_bytes == 24
    # more bytes cannot leave a reader worse off
    tight = compatibility_matrix(_corpus(), obs, budget_bytes=12)
    loose = compatibility_matrix(_corpus(), obs, budget_bytes=24)
    assert (
        loose.own["a"]["distortion_fraction"] <= tight.own["a"]["distortion_fraction"]
    )


def test_bad_inputs_are_refused():
    with pytest.raises(ValueError):
        compatibility_matrix(_corpus(), [ObserverGeometry("a", np.eye(D), 16)])
    with pytest.raises(ValueError):
        compatibility_matrix(
            _corpus(),
            [
                ObserverGeometry("a", np.eye(D), 16),
                ObserverGeometry("b", np.eye(D - 1), 16),
            ],
        )


# ---- CLI ----------------------------------------------------------------------


def _contract(name, consumers, budget):
    return ObserverContract.from_dict(
        {
            "schema": "turboquant-pro/observer-contract",
            "profile": "tqp-observer/1",
            "observer": name,
            "target": "embedding",
            "consumers": consumers,
            "budget": {"max_bytes_per_vector": budget},
        }
    )


def _write(tmp_path, contract, name):
    p = tmp_path / name
    p.write_text(json.dumps(contract.as_dict()), encoding="utf-8")
    return str(p)


def test_cli_matrix_from_contracts(tmp_path, capsys):
    art = tmp_path / "x.npy"
    np.save(art, _corpus())
    rng = np.random.default_rng(4)
    q = np.zeros((300, D))
    q[:, :6] = rng.standard_normal((300, 6))
    qp = tmp_path / "q.npy"
    np.save(qp, q)
    a = _write(
        tmp_path,
        _contract("search", [{"metric": "topk_cosine", "config": {"k": 10}}], 16),
        "a.json",
    )
    b = _write(
        tmp_path,
        _contract(
            "reader",
            [{"metric": "read_operator", "config": {"provider": "identity"}}],
            16,
        ),
        "b.json",
    )
    out = tmp_path / "m.json"
    rc = main(
        [
            "plan",
            "compat",
            "--artifact",
            str(art),
            "--queries",
            str(qp),
            "--observer",
            a,
            "--observer",
            b,
            "--out",
            str(out),
            "--format",
            "json",
        ]
    )
    assert rc in (0, 1)
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["labels"] == ["search", "reader"]
    assert doc["ratio"]["search"]["search"] == pytest.approx(1.0)
    assert len(doc["observers"]) == 2 and doc["observers"][0]["sha256"]
    assert isinstance(doc["unsafe_pairs"], list)
    capsys.readouterr()
    assert main(["plan", "compat", "--artifact", str(art), "--observer", a]) == 2
    assert "two or more" in capsys.readouterr().err


def test_cli_needs_a_budget_somewhere(tmp_path, capsys):
    art = tmp_path / "x.npy"
    np.save(art, _corpus())
    c = _contract("a", [{"metric": "topk_cosine"}], 16).as_dict()
    c["budget"] = {}
    p = tmp_path / "a.json"
    p.write_text(json.dumps(c), encoding="utf-8")
    b = _write(tmp_path, _contract("b", [{"metric": "topk_l2"}], 16), "b.json")
    assert (
        main(
            [
                "plan",
                "compat",
                "--artifact",
                str(art),
                "--observer",
                str(p),
                "--observer",
                b,
            ]
        )
        == 2
    )
    assert "max_bytes_per_vector" in capsys.readouterr().err
    assert main(
        [
            "plan",
            "compat",
            "--artifact",
            str(art),
            "--observer",
            str(p),
            "--observer",
            b,
            "--budget-bytes",
            "16",
            "--format",
            "json",
        ]
    ) in (0, 1)
