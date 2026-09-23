# TurboQuant Pro: Open-source TurboQuant for LLM KV cache compression
# Copyright (c) 2026 Andrew H. Bond. MIT License.
"""The observer-advantage harness on synthetic arms with a planted effect.

This tests the harness, not the hypothesis. It stages synthetic arms in the
consumer-basis layout, runs real jobs through ``observer_advantage.cell``, and
scores them with ``observer_advantage.score``, checking that

* gate G0 is a real reproduction: ``consumer_basis.run`` is run on the same
  staged arrays and the harness's EXACT family must match it;
* a planted observer effect is found: queries read directions the corpus varies
  in weakly, so O must beat P through the TQ codec (H1 HOLDS), a held-out-rows
  arm must not move (H2 HOLDS), and a basis fitted to another arm's queries
  must lose to the right one (H4 HOLDS);
* what cannot be claimed is not: with RaBitQ and OPQ absent and three of seven
  arms run, H3 and the other families are UNSCORED and the platform claim is
  "TQ only";
* a configuration missing a seed is excluded, not imputed;
* a finished job is not recomputed.
"""

from __future__ import annotations

import json
import os
import sys
from importlib.util import find_spec

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "benchmarks"))

from consumer_basis import run as cb_run  # noqa: E402
from observer_advantage import cell, grid, score  # noqa: E402

D = 600  # > 512 so consumer_basis.run can produce its own record for G0
# 1,500 evaluation queries put the bootstrap interval of a null difference
# inside the +-0.01 TIE band; 300 left it just outside (INCONCLUSIVE).
N_CORPUS, N_FIT, N_EVAL = 3000, 2000, 1500
# O whitens by the fitted query moment, so a symmetric control needs enough fit
# rows per dimension for O to reduce to P: 2,000 in 600-d made O lose to P under
# exact search alone. 30,000 matches the real symmetric arms (50,000 in 1024-d).
N_FIT_SYM = 30_000


def _directions(rng):
    """Three disjoint orthonormal blocks: what the corpus varies in most (A),
    what msmarco's queries read (B), what hotpotqa's queries read (C)."""
    q = np.linalg.qr(rng.standard_normal((D, 3 * 128)))[0].T
    return q[:128], q[128:256], q[256:]


def _stage(root):
    rng = np.random.default_rng(0)
    a, b, c = _directions(rng)

    def corpus(n):
        return (
            3.0 * rng.standard_normal((n, 128)) @ a
            + 1.0 * rng.standard_normal((n, 128)) @ b
            + 1.0 * rng.standard_normal((n, 128)) @ c
            + 0.05 * rng.standard_normal((n, D))
        )

    def queries(n, reads):
        return rng.standard_normal((n, 128)) @ reads + 0.1 * rng.standard_normal((n, D))

    x = corpus(N_CORPUS + N_FIT_SYM + N_EVAL)
    arms = {
        "msmarco": (x[:N_CORPUS], queries(N_FIT, b), queries(N_EVAL, b)),
        "hotpotqa": (x[:N_CORPUS], queries(N_FIT, c), queries(N_EVAL, c)),
        "msmarco-sym": (
            x[:N_CORPUS],
            x[N_CORPUS : N_CORPUS + N_FIT_SYM],
            x[N_CORPUS + N_FIT_SYM :],
        ),
    }
    for arm, parts in arms.items():
        os.makedirs(os.path.join(root, arm), exist_ok=True)
        for name, arr in zip(("corpus", "fit", "eval"), parts):
            np.save(os.path.join(root, arm, f"{name}.npy"), arr.astype(np.float32))
        with open(os.path.join(root, arm, "hashes.json"), "w") as f:
            json.dump(dict(synthetic=True), f)
    return list(arms)


@pytest.fixture(scope="module")
def campaign(tmp_path_factory):
    root = str(tmp_path_factory.mktemp("cb"))
    out = str(tmp_path_factory.mktemp("oa"))
    cb_out = str(tmp_path_factory.mktemp("cbres"))
    arms = _stage(root)
    for arm in ("msmarco", "hotpotqa"):
        cb_run.run(arm, root, cb_out)
    for job in grid.jobs():  # Q is reported only and asserted nowhere, so skipped
        if (
            job["arm"] in arms
            and job["family"] in ("EXACT", "TQ")
            and job["transform"] != "Q"
        ):
            cell.run(job, root, out, threads=2)
    return dict(root=root, out=out, cb_out=cb_out)


def test_the_grid_is_the_registered_size():
    jobs = grid.jobs()
    codec = [c for j in jobs if j["family"] != grid.EXACT for c in grid.job_cells(j)]
    assert len(codec) == 1512 + 54  # prereg section 7
    exact = [c for j in jobs if j["family"] == grid.EXACT for c in grid.job_cells(j)]
    assert len(exact) == 87
    assert len({c["cell_id"] for j in jobs for c in grid.job_cells(j)}) == sum(
        len(grid.job_cells(j)) for j in jobs
    )


def test_gates_pass_and_g0_is_a_reproduction(campaign):
    res = score.score(campaign["out"], campaign["cb_out"])
    for g in ("G0", "G1", "G3"):
        assert res["gates"][g][0] == "PASS", (g, res["gates"][g])
    notes = res["gates"]["G0"][1]
    assert sum(not n.startswith("split identity") for n in notes) == 12  # 2x2x3
    assert sum(n.startswith("split identity") for n in notes) == 9  # 3 arms x 3 k


def test_the_planted_effect_is_found_and_nothing_more_is_claimed(campaign):
    res = score.score(campaign["out"], campaign["cb_out"], ungated=True)
    tq = res["verdicts"]["TQ"]
    assert tq["H1"][0] == "HOLDS", score._counts(tq["H1"][1])
    assert tq["H2"][0] == "HOLDS", score._counts(tq["H2"][1])
    assert tq["H4"][0] == "HOLDS", score._counts(tq["H4"][1])
    assert tq["H3"][0] == "UNSCORED"  # four of the seven arms never ran
    for fam in ("RBQ", "OPQ"):
        assert {v for v, _ in res["verdicts"][fam].values()} == {"UNSCORED"}
    assert res["claim"] == "HOLDS FOR TQ ONLY"


def test_withheld_without_the_reference_record(campaign):
    res = score.score(campaign["out"], cb_dir=None)
    assert res["gates"]["G0"][0] == "NOT CHECKED"
    assert res["verdicts"] is None and res["claim"] is None


def test_a_missing_seed_excludes_the_configuration(campaign, tmp_path):
    import shutil

    part = str(tmp_path / "part")
    shutil.copytree(campaign["out"], part)
    os.remove(
        os.path.join(part, grid.cell_id("msmarco", "O", "TQ", 64, 2, 1) + ".json")
    )
    configs, excluded = score.load(part)
    assert ("msmarco", "O", "TQ", 64, 2) not in configs
    assert any(e["config"] == ("msmarco", "O", "TQ", 64, 2) for e in excluded)
    res = score.score(part, campaign["cb_out"], ungated=True)
    assert res["verdicts"]["TQ"]["H1"][0] == "UNSCORED"


def test_a_finished_job_is_not_recomputed(campaign):
    job = next(j for j in grid.jobs() if j["job_id"] == "msmarco-P-TQ-s0")
    paths = [
        os.path.join(campaign["out"], c["cell_id"] + ".json")
        for c in grid.job_cells(job)
    ]
    before = [os.path.getmtime(p) for p in paths]
    cell.run(job, campaign["root"], campaign["out"], threads=2)
    assert [os.path.getmtime(p) for p in paths] == before


def test_records_carry_what_the_scorer_needs(campaign):
    p = os.path.join(
        campaign["out"], grid.cell_id("msmarco", "O", "TQ", 128, 4, 0) + ".json"
    )
    with open(p) as f:
        r = json.load(f)
    assert r["extra"]["scan"] in ("kernel", "numpy")
    assert r["stored_bytes_per_vec"] == 128 * 4 // 8 + 4
    assert len(r["hits_single"]) == len(r["hits_rr5"]) == N_EVAL
    assert r["basis_bytes"] == 2 * 128 * D * 4  # O has two maps


@pytest.mark.skipif(find_spec("faiss") is None, reason="faiss not installed")
def test_faiss_families_run():
    """One small cell per faiss family: the calls, the byte accounting and the
    output shape. faiss's OPQ training takes about 40 s even here, so whole jobs
    are left to the campaign."""
    rng = np.random.default_rng(3)
    ck = rng.standard_normal((3000, 64)).astype(np.float32)
    qk = rng.standard_normal((50, 64)).astype(np.float32)
    for fam, want_bytes in (("RBQ", None), ("OPQ", 64 * 2 // 8)):
        ids, stored, shared, extra = cell.FAMILIES[fam](ck, qk, 64, 2, 0, 2)
        assert np.asarray(ids).shape == (50, grid.K_TOP)
        assert (np.asarray(ids) >= 0).all()
        assert stored == want_bytes if want_bytes else stored > 64 * 2 // 8
        assert extra["seeded"] is (fam == "OPQ")
