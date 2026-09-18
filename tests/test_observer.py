# TurboQuant Pro: Open-source TurboQuant for LLM KV cache compression
# Copyright (c) 2026 Andrew H. Bond. MIT License.
"""Observer contracts (issue #173, phase 1): identity, validation, the planner
adapter, and the CLI paths that record or check the contract's hash."""

from __future__ import annotations

import json

import numpy as np
import pytest

from turboquant_pro.cli import main
from turboquant_pro.observer import (
    PROFILE,
    ConsumerClause,
    ContractError,
    ObserverContract,
    load_contract,
    parse_contract,
    save_contract,
)

CONTRACT = {
    "schema": "turboquant-pro/observer-contract",
    "profile": PROFILE,
    "observer": "retrieval-prod-v3",
    "target": "embedding",
    "source": {"embedding_model": "text-embedding-3-large", "dim": 1536},
    "consumers": [
        {
            "name": "retrieval",
            "metric": "topk_cosine",
            "config": {"k": 10},
            "weight": 0.85,
        },
        {
            "name": "reader",
            "metric": "read_operator",
            "config": {"provider": "identity"},
            "weight": 0.15,
        },
    ],
    "population": {"strata": "language-region-map.tqa"},
    "requirements": {
        "floor": {"metric": "recall@10", "minimum": 0.995, "confidence": 0.95}
    },
    "budget": {"max_bytes_per_vector": 128},
    "fallback": {"action": "exact_rerank"},
}


def _contract() -> ObserverContract:
    return ObserverContract.from_dict(json.loads(json.dumps(CONTRACT)))


# ---- identity --------------------------------------------------------------


def test_round_trip_and_hash_stability_under_key_order_and_format(tmp_path):
    c = _contract()
    assert c.as_dict() == CONTRACT
    shuffled = json.dumps(CONTRACT, sort_keys=True)
    spaced = json.dumps(CONTRACT, indent=4)
    assert parse_contract(shuffled).digest() == c.digest()
    assert parse_contract(spaced).digest() == c.digest()
    p = tmp_path / "c.json"
    assert save_contract(c, str(p)) == "json"
    assert load_contract(str(p)).digest() == c.digest()
    assert len(c.digest()) == 64


def test_any_declared_value_changes_the_hash():
    a = _contract()
    d = json.loads(json.dumps(CONTRACT))
    d["requirements"]["floor"]["minimum"] = 0.99
    assert ObserverContract.from_dict(d).digest() != a.digest()
    d = json.loads(json.dumps(CONTRACT))
    d["consumers"][0]["weight"] = 0.5
    assert ObserverContract.from_dict(d).digest() != a.digest()


def test_yaml_round_trip_when_pyyaml_is_installed(tmp_path):
    yaml = pytest.importorskip("yaml")
    c = _contract()
    p = tmp_path / "c.tqo"
    assert save_contract(c, str(p)) == "yaml"
    text = p.read_text(encoding="utf-8")
    assert yaml.safe_load(text)["observer"] == "retrieval-prod-v3"
    assert load_contract(str(p)).digest() == c.digest()


def test_primary_is_the_largest_weight_first_on_a_tie():
    c = _contract()
    assert c.primary().label == "retrieval"
    tie = ObserverContract(
        observer="t",
        consumers=(
            ConsumerClause(metric="topk_cosine", weight=1.0, name="a"),
            ConsumerClause(metric="topk_l2", weight=1.0, name="b"),
        ),
    )
    assert tie.primary().label == "a"
    w = c.normalized_weights()
    assert w["retrieval"] == pytest.approx(0.85) and w["reader"] == pytest.approx(0.15)


# ---- validation ------------------------------------------------------------


def test_valid_contract_has_no_problems():
    assert _contract().validate() == []


def test_unknown_consumer_is_refused():
    d = json.loads(json.dumps(CONTRACT))
    d["consumers"][0]["metric"] = "topk_manhattan"
    problems = ObserverContract.from_dict(d).validate()
    assert problems and "topk_manhattan" in problems[0]
    with pytest.raises(ContractError):
        ObserverContract.from_dict(d).ensure_valid()


def test_read_operator_consumer_needs_a_registered_provider():
    d = json.loads(json.dumps(CONTRACT))
    d["consumers"][1]["config"] = {"provider": "no_such_provider"}
    problems = ObserverContract.from_dict(d).validate()
    assert any("no_such_provider" in p for p in problems)
    d["consumers"][1]["config"] = {}
    problems = ObserverContract.from_dict(d).validate()
    assert any("config.provider" in p for p in problems)


def test_consumer_registered_for_another_target_is_refused():
    d = json.loads(json.dumps(CONTRACT))
    d["target"] = "kv_key"
    problems = ObserverContract.from_dict(d).validate()
    assert any("not for target 'kv_key'" in p for p in problems)


@pytest.mark.parametrize(
    "path, value, fragment",
    [
        (("requirements", "floor", "minimum"), 1.5, "minimum"),
        (("requirements", "floor", "confidence"), 1.0, "confidence"),
        (("budget", "max_bits"), -1, "max_bits"),
        (("fallback", "action"), "panic", "action"),
        (("consumers", 0, "weight"), 0, "weight"),
    ],
)
def test_structural_problems_are_named(path, value, fragment):
    d = json.loads(json.dumps(CONTRACT))
    node = d
    for k in path[:-1]:
        node = node[k]
    node[path[-1]] = value
    problems = ObserverContract.from_dict(d).validate()
    assert problems and any(fragment in p for p in problems)


def test_manual_rules_agree_with_the_schema_when_jsonschema_is_absent(monkeypatch):
    import builtins

    from turboquant_pro import observer as mod

    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "jsonschema":
            raise ImportError
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    d = json.loads(json.dumps(CONTRACT))
    d["fallback"]["action"] = "panic"
    problems = mod._schema_problems(d)
    assert problems and "action" in problems[0]
    assert mod._schema_problems(CONTRACT) == []


def test_malformed_documents_raise_contract_error():
    with pytest.raises(ContractError):
        parse_contract("[]")
    with pytest.raises(ContractError):
        parse_contract(
            json.dumps(
                {
                    "schema": "something-else",
                    "observer": "x",
                    "consumers": [{"metric": "m"}],
                }
            )
        )
    with pytest.raises(ContractError):
        parse_contract(json.dumps({"observer": "x", "consumers": []}))
    with pytest.raises(ContractError):
        load_contract("/no/such/contract.tqo")


# ---- the planner adapter ---------------------------------------------------


def test_workload_spec_matches_the_hand_built_one():
    from turboquant_pro.planner import Budget, QualityFloor, WorkloadSpec

    c = _contract()
    spec = c.to_workload_spec(seed=3, n_boot=64)
    expected = WorkloadSpec(
        target="embedding",
        consumer="topk_cosine",
        consumer_config={"k": 10},
        budget=Budget(max_bytes_per_vector=128),
        floor=QualityFloor(minimum=0.995, confidence=0.95),
        seed=3,
        n_boot=64,
    )
    assert spec.as_dict() == expected.as_dict()
    ref = c.reference()
    assert ref["sha256"] == c.digest()
    assert ref["primary_consumer"]["metric"] == "topk_cosine"
    assert ref["consumers"] == ["retrieval", "reader"]


# ---- CLI -------------------------------------------------------------------


def _write(tmp_path, doc, name="c.json"):
    p = tmp_path / name
    p.write_text(json.dumps(doc), encoding="utf-8")
    return str(p)


def test_cli_validate_show_hash(tmp_path, capsys):
    p = _write(tmp_path, CONTRACT)
    assert main(["observer", "validate", p]) == 0
    assert "VALID" in capsys.readouterr().out
    assert main(["observer", "hash", p]) == 0
    assert capsys.readouterr().out.strip() == _contract().digest()
    assert main(["observer", "show", p]) == 0
    out = capsys.readouterr().out
    assert "retrieval" in out and "primary" in out and "valid" in out
    assert main(["observer", "show", p, "--format", "json"]) == 0
    doc = json.loads(capsys.readouterr().out)
    assert doc["sha256"] == _contract().digest()
    bad = json.loads(json.dumps(CONTRACT))
    bad["consumers"][0]["metric"] = "nope"
    pb = _write(tmp_path, bad, "bad.json")
    assert main(["observer", "validate", pb]) == 1
    assert "INVALID" in capsys.readouterr().out
    assert main(["observer", "validate", str(tmp_path / "missing.tqo")]) == 2


def test_cli_init_writes_a_valid_contract(tmp_path, capsys):
    out = tmp_path / "new.json"
    assert (
        main(["observer", "init", "--name", "svc", "--out", str(out), "--k", "5"]) == 0
    )
    c = load_contract(str(out))
    assert c.validate() == []
    assert c.primary().config == {"k": 5}
    assert main(["observer", "init", "--name", "svc", "--out", str(out)]) == 2


def _pair(tmp_path, n=64, d=16, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal((n, d)).astype(np.float32)
    y = (x + 0.01 * rng.standard_normal((n, d))).astype(np.float32)
    po, pr = tmp_path / "o.npy", tmp_path / "r.npy"
    np.save(po, x)
    np.save(pr, y)
    return str(po), str(pr)


def test_certify_records_the_observer_and_verify_checks_it(tmp_path, capsys):
    p = _write(tmp_path, CONTRACT)
    po, pr = _pair(tmp_path)
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
            "--observer",
            p,
            "--out",
            str(cert),
        ]
    )
    assert rc in (0, 1)
    doc = json.loads(cert.read_text(encoding="utf-8"))
    assert doc["observer"]["sha256"] == _contract().digest()
    assert doc["observer"]["observer"] == "retrieval-prod-v3"
    capsys.readouterr()
    assert main(["verify", str(cert), "--observer", p, "--format", "json"]) == 0
    rep = json.loads(capsys.readouterr().out)
    assert rep["checks"]["observer"]["match"] is True
    other = json.loads(json.dumps(CONTRACT))
    other["observer"] = "someone-else"
    p2 = _write(tmp_path, other, "other.json")
    assert main(["verify", str(cert), "--observer", p2, "--format", "json"]) == 1
    rep = json.loads(capsys.readouterr().out)
    assert rep["checks"]["observer"]["match"] is False
    assert "different observer" in rep["checks"]["observer"]["reason"]


def test_certify_refuses_an_invalid_contract_without_writing(tmp_path, capsys):
    bad = json.loads(json.dumps(CONTRACT))
    bad["consumers"][0]["metric"] = "nope"
    p = _write(tmp_path, bad, "bad.json")
    po, pr = _pair(tmp_path)
    cert = tmp_path / "cert.json"
    assert (
        main(
            [
                "certify",
                "--original",
                po,
                "--reconstructed",
                pr,
                "--observer",
                p,
                "--out",
                str(cert),
            ]
        )
        == 2
    )
    assert not cert.exists()


def test_verify_fails_when_the_certificate_names_no_observer(tmp_path, capsys):
    p = _write(tmp_path, CONTRACT)
    po, pr = _pair(tmp_path)
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
    capsys.readouterr()
    assert main(["verify", str(cert), "--observer", p, "--format", "json"]) == 1
    rep = json.loads(capsys.readouterr().out)
    assert rep["checks"]["observer"]["reason"] == "certificate names no observer"


def test_plan_run_reads_the_contract_and_names_it(tmp_path, capsys):
    contract = json.loads(json.dumps(CONTRACT))
    contract["requirements"] = {}
    contract["budget"] = {}
    p = _write(tmp_path, contract)
    rng = np.random.default_rng(1)
    art = tmp_path / "a.npy"
    np.save(art, rng.standard_normal((300, 24)).astype(np.float32))
    out = tmp_path / "plan.json"
    rc = main(
        [
            "plan",
            "run",
            "--artifact",
            str(art),
            "--observer",
            p,
            "--n-boot",
            "16",
            "--out",
            str(out),
            "--format",
            "json",
        ]
    )
    assert rc in (0, 1)
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["observer"]["sha256"] == ObserverContract.from_dict(contract).digest()
    assert doc["workload"]["consumer"] == "topk_cosine"
    assert doc["workload"]["consumer_config"] == {"k": 10}


def test_artifact_schemas_accept_the_observer_section():
    jsonschema = pytest.importorskip("jsonschema")
    from turboquant_pro.schemas import load_schema

    ref = _contract().reference()
    for name in ("rank_certificate.schema.json", "compression_plan.schema.json"):
        schema = load_schema(name)
        prop = schema["properties"]["observer"]
        jsonschema.Draft202012Validator(prop).validate(ref)
    obs = load_schema("observer_contract.schema.json")
    jsonschema.Draft202012Validator(obs).validate(CONTRACT)
