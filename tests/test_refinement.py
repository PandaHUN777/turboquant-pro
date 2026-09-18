# TurboQuant Pro: Open-source TurboQuant for LLM KV cache compression
# Copyright (c) 2026 Andrew H. Bond. MIT License.
"""Successive refinement across observers (issue #174, phase 1): the tax is
near zero when two readers share directions, and the planner recommends
separate representations when they do not."""

from __future__ import annotations

import json

import numpy as np
import pytest

from turboquant_pro.cli import main
from turboquant_pro.observer import ObserverContract
from turboquant_pro.refinement import (
    ObserverGeometry,
    layer_bytes,
    observer_operator,
    refinement_report,
)

D = 32


def _corpus(seed=0, n=2000):
    rng = np.random.default_rng(seed)
    scale = np.linspace(3.0, 0.3, D)
    return (rng.standard_normal((n, D)) * scale).astype(np.float32)


def _projector(lo, hi):
    P = np.zeros((D, D))
    P[lo:hi, lo:hi] = np.eye(hi - lo)
    return P


def test_identical_readers_share_a_code_at_no_tax():
    x = _corpus()
    a = ObserverGeometry("search", _projector(0, 8), 12)
    b = ObserverGeometry("analytics", _projector(0, 8), 16)
    r = refinement_report(x, a, b)
    assert r.overlap == pytest.approx(1.0)
    assert r.progressive["feasible"]
    assert r.tax is not None and r.tax <= 0.15
    assert r.verdict.startswith("progressive")
    assert r.progressive["base_bytes"] <= a.budget_bytes
    assert r.progressive["total_bytes"] <= r.separate["bytes"]
    # the refined observer reaches the quality it would have had alone
    assert (
        r.progressive["distortion_total_for_refined"]
        <= r.alone["analytics"]["distortion"] + 1e-12
    )


def test_disjoint_aligned_readers_layer_at_no_tax():
    # two projectors on disjoint coordinate blocks: the null space of one
    # contains the other's directions, so the layer is exactly the second
    # block and the base reader stops early
    x = _corpus()
    a = ObserverGeometry("search", _projector(0, 8), 12)
    b = ObserverGeometry("anomaly", _projector(16, 24), 12)
    r = refinement_report(x, a, b)
    assert r.overlap == pytest.approx(0.0)
    assert r.tax == pytest.approx(0.0)
    assert r.progressive["total_bytes"] < r.separate["bytes"]
    assert r.verdict.startswith("progressive")


def test_rotated_reader_is_told_to_keep_a_separate_code():
    # a projector onto a Haar-random 8-dimensional subspace spreads over every
    # coordinate direction, so refining the coordinate-aligned base costs as
    # much as a second code
    x = _corpus()
    rng = np.random.default_rng(3)
    Q, _ = np.linalg.qr(rng.standard_normal((D, D)))
    rot = Q[:, :8] @ Q[:, :8].T
    a = ObserverGeometry("search", _projector(0, 8), 12)
    b = ObserverGeometry("anomaly", rot, 12)
    r = refinement_report(x, a, b)
    assert 0.0 < r.overlap < 0.6
    assert r.verdict.startswith("separate")
    assert r.progressive["total_bytes"] >= r.separate["bytes"]


def test_tax_is_reported_when_budgets_bind():
    # diagonal readers with opposite emphasis share the coordinate basis, so
    # a flat code exists; the base-first order pays a non-negative tax
    x = _corpus()
    w = np.linspace(1.0, 0.05, D)
    a = ObserverGeometry("front", np.diag(w), 10)
    b = ObserverGeometry("back", np.diag(w[::-1]), 14)
    r = refinement_report(x, a, b)
    assert r.progressive["feasible"] and r.flat["feasible"]
    assert r.tax is not None and r.tax >= -1e-9
    assert r.progressive["total_bytes"] >= r.flat["bytes"]


def test_partial_overlap_lands_between():
    x = _corpus()
    a = ObserverGeometry("search", _projector(0, 8), 12)
    b = ObserverGeometry("mixed", _projector(4, 12), 12)
    r = refinement_report(x, a, b)
    assert 0.0 < r.overlap < 1.0
    assert r.progressive["total_bytes"] >= r.progressive["base_bytes"]
    d = r.as_dict()
    assert d["schema"] == "turboquant-pro/refinement-report"
    json.dumps(d)
    text = r.explain()
    assert "SUCCESSIVE REFINEMENT REPORT" in text and "VERDICT" in text


def test_base_is_the_smaller_budget_whatever_the_order():
    x = _corpus()
    a = ObserverGeometry("big", _projector(0, 8), 20)
    b = ObserverGeometry("small", _projector(0, 8), 10)
    r = refinement_report(x, a, b)
    assert r.base == "small" and r.refined == "big"


def test_layer_bytes_counts_packed_bits_and_the_norm():
    assert layer_bytes(np.array([4, 4])) == 1 + 4
    assert layer_bytes(np.array([3, 3, 3])) == 2 + 4
    assert layer_bytes(np.zeros(5), norm=False) == 0


def test_operator_shape_is_checked():
    x = _corpus()
    with pytest.raises(ValueError):
        refinement_report(
            x,
            ObserverGeometry("a", np.eye(D - 1), 8),
            ObserverGeometry("b", np.eye(D), 8),
        )


# ---- from contracts ---------------------------------------------------------


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


def test_observer_operator_reads_along_queries_for_retrieval():
    x = _corpus()
    rng = np.random.default_rng(5)
    q = np.zeros((200, D))
    q[:, :4] = rng.standard_normal((200, 4))
    c = _contract("search", [{"metric": "topk_cosine", "config": {"k": 10}}], 16)
    P = observer_operator(c, x, queries=q)
    assert P.shape == (D, D)
    assert np.trace(P[:4, :4]) == pytest.approx(1.0, abs=1e-9)
    assert np.abs(P[4:, 4:]).max() < 1e-12
    # without queries a retrieval consumer reads every direction equally
    assert np.allclose(observer_operator(c, x), np.eye(D))


def test_observer_operator_mixes_consumers_by_weight():
    x = _corpus()
    c = _contract(
        "mix",
        [
            {
                "name": "r",
                "metric": "read_operator",
                "config": {"provider": "identity"},
                "weight": 3,
            },
            {"name": "s", "metric": "topk_cosine", "config": {"k": 10}, "weight": 1},
        ],
        16,
    )
    assert np.allclose(observer_operator(c, x), np.eye(D))


def test_cli_plan_refine_from_two_contracts(tmp_path, capsys):
    x = _corpus()
    art = tmp_path / "x.npy"
    np.save(art, x)
    rng = np.random.default_rng(9)
    q = np.zeros((300, D))
    q[:, :6] = rng.standard_normal((300, 6))
    qp = tmp_path / "q.npy"
    np.save(qp, q)
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text(
        json.dumps(
            _contract(
                "search", [{"metric": "topk_cosine", "config": {"k": 10}}], 12
            ).as_dict()
        )
    )
    b.write_text(
        json.dumps(
            _contract(
                "reader",
                [{"metric": "read_operator", "config": {"provider": "identity"}}],
                20,
            ).as_dict()
        )
    )
    out = tmp_path / "refine.json"
    rc = main(
        [
            "plan",
            "refine",
            "--artifact",
            str(art),
            "--queries",
            str(qp),
            "--observer",
            str(a),
            "--observer",
            str(b),
            "--out",
            str(out),
            "--format",
            "json",
        ]
    )
    assert rc == 0
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["base"] == "search" and doc["refined"] == "reader"
    assert doc["observers"][0]["sha256"] and doc["observers"][1]["sha256"]
    assert doc["verdict"] in (
        "progressive representation recommended",
        "separate representations recommended",
    )
    capsys.readouterr()
    assert main(["plan", "refine", "--artifact", str(art), "--observer", str(a)]) == 2


def test_cli_plan_refine_needs_budgets(tmp_path, capsys):
    x = _corpus()
    art = tmp_path / "x.npy"
    np.save(art, x)
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text(
        json.dumps(_contract("search", [{"metric": "topk_cosine"}], 12).as_dict())
    )
    nb = _contract("reader", [{"metric": "topk_l2"}], 12).as_dict()
    nb["budget"] = {}
    b.write_text(json.dumps(nb))
    assert (
        main(
            [
                "plan",
                "refine",
                "--artifact",
                str(art),
                "--observer",
                str(a),
                "--observer",
                str(b),
            ]
        )
        == 2
    )
    assert "max_bytes_per_vector" in capsys.readouterr().err
