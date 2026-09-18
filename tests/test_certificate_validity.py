# TurboQuant Pro: Open-source TurboQuant for LLM KV cache compression
# Copyright (c) 2026 Andrew H. Bond. MIT License.
"""Certificates expire (issue #177, phase 1): the validity section a
certificate records at issue, and the checks that turn it STALE when the
observer's read geometry changes or the data leaves the calibration's
coverage, and keep it VALID otherwise."""

from __future__ import annotations

import json

import numpy as np
import pytest

from turboquant_pro.cli import main
from turboquant_pro.observer import ObserverContract
from turboquant_pro.validity import (
    STALE,
    UNCHECKED,
    VALID,
    check_validity,
    coverage_divergence,
    coverage_sketch,
    operator_overlap,
    operator_sketch,
    validity_section,
    validity_summary,
)

D = 24


def _projector(lo, hi):
    P = np.zeros((D, D))
    P[lo:hi, lo:hi] = np.eye(hi - lo)
    return P


def _sample(seed=0, n=400, shift=0.0, scale=1.0):
    rng = np.random.default_rng(seed)
    return (shift + scale * rng.standard_normal((n, D))).astype(np.float32)


# ---- sketches ----------------------------------------------------------------


def test_operator_sketch_keeps_the_read_subspace():
    sk = operator_sketch(_projector(0, 4))
    assert sk["rank"] == 4 and sk["trace_fraction"] == pytest.approx(1.0)
    assert operator_overlap(sk, _projector(0, 4)) == pytest.approx(1.0)
    assert operator_overlap(sk, _projector(4, 8)) == pytest.approx(0.0)
    assert operator_overlap(sk, _projector(2, 6)) == pytest.approx(0.5)


def test_flat_operator_sketch_carries_little_trace():
    sk = operator_sketch(np.eye(D), cap=8)
    assert sk["rank"] == 8
    assert sk["trace_fraction"] == pytest.approx(8 / D)


def test_coverage_divergence_is_zero_on_the_same_moments_and_grows_with_shift():
    x = _sample()
    sk = coverage_sketch(x)
    assert coverage_divergence(sk, x) == pytest.approx(0.0, abs=1e-9)
    assert coverage_divergence(sk, _sample(seed=1)) < 0.1
    assert coverage_divergence(sk, _sample(seed=1, shift=2.0)) > 1.0
    assert coverage_divergence(sk, _sample(seed=1, scale=3.0)) > 1.0


def test_validity_section_records_identity_and_thresholds():
    v = validity_section(
        observer_sha256="a" * 64,
        reference={"provider": "declared", "operator_sha256": "b" * 64},
        operator=_projector(0, 4),
        sample=_sample(),
    )
    assert v["issued_for"]["observer_sha256"] == "a" * 64
    assert v["issued_for"]["reference_provider"] == "declared"
    assert v["thresholds"]["min_operator_overlap"] == 0.85
    assert v["operator_sketch"]["rank"] == 4
    assert v["coverage_sketch"]["rows"] == 400
    json.dumps(v)


# ---- the decision -------------------------------------------------------------


def _contract(provider_matrix=None):
    consumers = (
        [{"metric": "read_operator", "config": {"provider": "identity"}}]
        if provider_matrix is None
        else [{"metric": "declared_op", "config": {}}]
    )
    return ObserverContract.from_dict(
        {
            "schema": "turboquant-pro/observer-contract",
            "profile": "tqp-observer/1",
            "observer": "svc",
            "target": "embedding",
            "consumers": consumers,
        }
    )


def _doc(operator, sample, contract=None, reference=None):
    return {
        "schema": "turboquant-pro/rank-certificate",
        "observer": {"sha256": contract.digest()} if contract else None,
        "reference": reference,
        "validity": validity_section(
            observer_sha256=contract.digest() if contract else None,
            reference=reference,
            operator=operator,
            sample=sample,
        ),
    }


def test_unchecked_without_data_or_contract():
    r = check_validity(_doc(_projector(0, 4), _sample()))
    assert r["status"] == UNCHECKED and r["applicable"]
    assert "not_checked" in validity_summary(r)


def test_geometry_change_makes_it_stale_with_replan(monkeypatch):
    # the certified operator reads the first four channels; the reference
    # provider later reads channels 8 to 12
    from turboquant_pro import read_operators as ro

    class Rotated:
        def operator(self, activations, **_):
            return _projector(8, 12)

    monkeypatch.setitem(
        ro._REGISTRY,
        "rotated_test",
        ro.ReadOperatorSpec(name="rotated_test", factory=lambda **k: Rotated()),
    )
    x = _sample()
    ref = {"provider": "rotated_test", "operator_sha256": "c" * 64, "config": {}}
    doc = _doc(_projector(0, 4), x, reference=ref)
    r = check_validity(doc, data=_sample(seed=2))
    assert r["status"] == STALE and not r["applicable"]
    assert r["checks"]["operator_overlap"]["status"] == "FAIL"
    assert r["checks"]["operator_overlap"]["overlap"] == pytest.approx(0.0)
    assert r["action"] == "REPLAN"
    assert "consumer read geometry changed" in r["reason"]
    assert r["checks"]["data_coverage"]["status"] == "ok"
    assert "STALE" in validity_summary(r)


def test_same_geometry_and_data_stay_valid(monkeypatch):
    from turboquant_pro import read_operators as ro

    class Same:
        def operator(self, activations, **_):
            return _projector(0, 4)

    monkeypatch.setitem(
        ro._REGISTRY,
        "same_test",
        ro.ReadOperatorSpec(name="same_test", factory=lambda **k: Same()),
    )
    ref = {"provider": "same_test", "operator_sha256": "c" * 64, "config": {}}
    doc = _doc(_projector(0, 4), _sample(), reference=ref)
    r = check_validity(doc, data=_sample(seed=3))
    assert r["status"] == VALID and r["applicable"]
    assert r["checks"]["operator_overlap"]["overlap"] == pytest.approx(1.0)
    assert r["action"] is None


def test_data_drift_makes_it_stale_with_recertify():
    doc = _doc(_projector(0, 4), _sample())
    r = check_validity(doc, data=_sample(seed=4, shift=3.0))
    assert r["status"] == STALE
    assert r["checks"]["data_coverage"]["status"] == "FAIL"
    assert r["action"] == "RECERTIFY"
    # the operator check could not run (no contract, no reference) and says so
    assert r["checks"]["operator_overlap"]["status"] == "not_checked"


def test_flat_operator_does_not_pretend_to_test_overlap():
    c = _contract()
    doc = _doc(np.eye(D), _sample(), contract=c)
    r = check_validity(doc, contract=c, data=_sample(seed=5))
    assert r["checks"]["operator_overlap"]["status"] == "not_checked"
    assert "not low-rank" in r["checks"]["operator_overlap"]["reason"]
    assert r["status"] == VALID


def test_changed_contract_is_stale():
    c = _contract()
    doc = _doc(_projector(0, 4), _sample(), contract=c)
    other = ObserverContract.from_dict({**c.as_dict(), "observer": "other"})
    r = check_validity(doc, contract=other)
    assert r["status"] == STALE and r["action"] == "REPLAN"
    assert "observer contract changed" in r["reason"]


def test_changed_inputs_are_stale():
    r = check_validity(_doc(_projector(0, 4), _sample()), inputs_ok=False)
    assert r["status"] == STALE and r["action"] == "RECERTIFY"


# ---- CLI ---------------------------------------------------------------------


def _pair(tmp_path, n=64, d=16, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal((n, d)).astype(np.float32)
    y = (x + 0.01 * rng.standard_normal((n, d))).astype(np.float32)
    po, pr = tmp_path / "o.npy", tmp_path / "r.npy"
    np.save(po, x)
    np.save(pr, y)
    return str(po), str(pr), x


def test_certify_records_validity_with_a_reference_and_verify_reads_it(
    tmp_path, capsys
):
    po, pr, x = _pair(tmp_path)
    cert = tmp_path / "cert.json"
    rc = main(
        [
            "certify",
            "--original",
            po,
            "--reconstructed",
            pr,
            "--anchors",
            "16",
            "--reference",
            "identity",
            "--out",
            str(cert),
        ]
    )
    assert rc in (0, 1)
    doc = json.loads(cert.read_text(encoding="utf-8"))
    assert doc["validity"]["issued_for"]["reference_provider"] == "identity"
    assert doc["validity"]["coverage_sketch"]["rows"] == 64
    capsys.readouterr()
    # same data: coverage ok; the identity operator is flat, so overlap is not tested
    data = tmp_path / "d.npy"
    np.save(data, x)
    assert main(["verify", str(cert), "--data", str(data), "--format", "json"]) == 0
    rep = json.loads(capsys.readouterr().out)
    assert rep["validity"]["status"] == "VALID" and rep["applicable"] is True
    assert rep["validity"]["checks"]["operator_overlap"]["status"] == "not_checked"
    # shifted data: STALE, exit 1, verified stays true
    np.save(data, x + 4.0)
    assert main(["verify", str(cert), "--data", str(data), "--format", "json"]) == 1
    rep = json.loads(capsys.readouterr().out)
    assert rep["verified"] is True and rep["applicable"] is False
    assert rep["validity"]["status"] == "STALE"
    assert rep["validity"]["action"] == "RECERTIFY"


def test_certify_without_validity_verifies_unchecked(tmp_path, capsys):
    po, pr, x = _pair(tmp_path)
    cert = tmp_path / "cert.json"
    main(
        [
            "certify",
            "--original",
            po,
            "--reconstructed",
            pr,
            "--anchors",
            "16",
            "--out",
            str(cert),
        ]
    )
    doc = json.loads(cert.read_text(encoding="utf-8"))
    assert "validity" not in doc
    capsys.readouterr()
    data = tmp_path / "d.npy"
    np.save(data, x)
    assert main(["verify", str(cert), "--data", str(data), "--format", "json"]) == 0
    rep = json.loads(capsys.readouterr().out)
    assert rep["validity"]["status"] == "UNCHECKED"


def test_certify_validity_flag_alone(tmp_path):
    po, pr, _ = _pair(tmp_path)
    cert = tmp_path / "cert.json"
    main(
        [
            "certify",
            "--original",
            po,
            "--reconstructed",
            pr,
            "--anchors",
            "16",
            "--validity",
            "--out",
            str(cert),
        ]
    )
    doc = json.loads(cert.read_text(encoding="utf-8"))
    assert doc["validity"]["operator_sketch"] is None
    assert doc["validity"]["coverage_sketch"]["dim"] == 16


def test_certificate_schema_accepts_validity(tmp_path):
    jsonschema = pytest.importorskip("jsonschema")
    from turboquant_pro.schemas import load_schema

    po, pr, _ = _pair(tmp_path)
    cert = tmp_path / "cert.json"
    main(
        [
            "certify",
            "--original",
            po,
            "--reconstructed",
            pr,
            "--anchors",
            "16",
            "--reference",
            "identity",
            "--out",
            str(cert),
        ]
    )
    doc = json.loads(cert.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(
        load_schema("rank_certificate.schema.json")
    ).validate(doc)
