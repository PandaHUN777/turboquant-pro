# TurboQuant Pro: Open-source TurboQuant for LLM KV cache compression
# Copyright (c) 2026 Andrew H. Bond. MIT License.
"""The inner-product metric of the ADC scan.

Cosine discards two magnitudes, the query's and the row's. That is correct for
a cosine consumer and wrong for two others: a maximum-inner-product consumer,
and a consumer whose queries and rows pass through different linear maps (the
two-map consumer basis of docs/PREREG_consumer_basis.md), which do not preserve
norms. Under ``metric="inner_product"`` the index scores ``q . recon`` with the
query as given and the reconstruction in the input space.

What is pinned here, each against a reference computed another way:

* the scan equals ``q @ decompress(compress(x)).T`` from the pipeline's own
  codec path, for off-centre data with heterogeneous row norms, whitened or
  not, QR or Hadamard rotated;
* it is linear in the query (a metamorphic check that the query is not
  normalized), where cosine is invariant to the query's scale;
* it recovers exact inner-product neighbours that cosine cannot, on data
  constructed so the two orders disagree (the check has something to find);
* exact reranking orders by the index's metric everywhere it is implemented:
  the flat index, IVF, TQEIndex and the cold-tier rerank;
* with the compiled kernel, inner product is the cosine scan with a unit
  denominator, and its scores sit within the kernel's table resolution.
"""

from __future__ import annotations

import numpy as np
import pytest

from turboquant_pro import ADCIndex, IVFIndex, PCAMatryoshka, TQEIndex
from turboquant_pro import adc_index as ai
from turboquant_pro.metrics import METRICS, check_metric, exact_scores
from turboquant_pro.rerank_tier import rerank_candidates

# Agreement with the pipeline's reconstruction, relative to the scale of the
# scores (inner products are not bounded by one). Measured on Atlas at 1.8e-7
# to 3.4e-7 across whiten x rotation, i.e. float32 rounding; 1e-5 leaves a 30x
# margin and still fails on any systematic error, where the cosine reference
# tests' 2e-4 would pass one 600 times larger than the rounding.
REL = 1e-5


def _data(n_train=2000, n_db=1000, n_q=40, d=64, seed=0):
    """Correlated, off-centre rows with lognormal norms, and queries from a
    different distribution (other covariance, other norms)."""
    rng = np.random.default_rng(seed)
    mix = 0.5 * rng.standard_normal((d, d)) + np.eye(d)
    x = rng.standard_normal((n_train + n_db, d)) @ mix + 2.0 * rng.standard_normal(d)
    x *= np.exp(0.8 * rng.standard_normal((len(x), 1)))
    qmix = 0.3 * rng.standard_normal((d, d)) + np.diag(rng.uniform(0.2, 2.0, d))
    q = rng.standard_normal((n_q, d)) @ qmix
    q *= np.exp(0.5 * rng.standard_normal((n_q, 1)))
    x, q = x.astype(np.float32), q.astype(np.float32)
    return x[:n_train], x[n_train:], q


def _fitted(train, d_out, whiten=False):
    pca = PCAMatryoshka(input_dim=train.shape[1], output_dim=d_out, whiten=whiten)
    pca.fit(train)  # fit returns a PCAFitResult, not the fitted object
    return pca


def _full_scores(index: ADCIndex, q: np.ndarray) -> np.ndarray:
    """Every row's numpy-scan score for every query, in row order."""
    q_rot, qbias = index._query_terms(q)
    idx, sc = index._search_numpy(q_rot, qbias, index.size)
    return np.take_along_axis(sc, np.argsort(idx, axis=1), axis=1)


def _recall(found: np.ndarray, truth: np.ndarray) -> float:
    k = truth.shape[1]
    return float(np.mean([len(set(f[:k]) & set(t)) / k for f, t in zip(found, truth)]))


@pytest.fixture
def no_kernel(monkeypatch):
    monkeypatch.setattr(ai._adc, "load", lambda: None)


# --------------------------------------------------------------------------- #
# The metric vocabulary                                                        #
# --------------------------------------------------------------------------- #


def test_one_vocabulary():
    assert METRICS == ("inner_product", "cosine", "l2")
    for m in METRICS:
        assert check_metric(m) == m
    with pytest.raises(ValueError, match="unknown retrieval metric"):
        check_metric("ip")  # faiss's spelling is not ours
    train, _, _ = _data(n_db=10)
    pca = _fitted(train, 16)
    with pytest.raises(ValueError, match="unknown retrieval metric"):
        ADCIndex(pca.with_quantizer(bits=3), metric="dot")


def test_exact_scores_definitions():
    rng = np.random.default_rng(1)
    q = rng.standard_normal((3, 5))
    x = rng.standard_normal((7, 5)) * 3.0
    np.testing.assert_allclose(exact_scores(q, x, "inner_product"), q @ x.T)
    qn = q / np.linalg.norm(q, axis=1, keepdims=True)
    xn = x / np.linalg.norm(x, axis=1, keepdims=True)
    np.testing.assert_allclose(exact_scores(q, x, "cosine"), qn @ xn.T)
    d2 = ((q[:, None, :] - x[None, :, :]) ** 2).sum(axis=2)
    np.testing.assert_allclose(exact_scores(q, x, "l2"), -d2, rtol=1e-12, atol=1e-12)


def test_score_block_inner_product_is_the_inner_term():
    rng = np.random.default_rng(2)
    adc = rng.standard_normal((4, 9)).astype(np.float32)
    qbias = rng.standard_normal(4).astype(np.float32)
    cnorm = rng.uniform(0.5, 3.0, 9).astype(np.float32)
    vrnorm = rng.uniform(0.2, 1.0, 9).astype(np.float32)
    inner = qbias[:, None] + cnorm[None, :] * adc
    np.testing.assert_array_equal(
        ai.score_block("inner_product", adc, qbias, cnorm, vrnorm), inner
    )
    np.testing.assert_array_equal(
        ai.score_block("cosine", adc, qbias, cnorm, vrnorm), inner * vrnorm[None, :]
    )


# --------------------------------------------------------------------------- #
# The scan against the pipeline's own reconstruction                           #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("whiten", [False, True])
@pytest.mark.parametrize("rotation", ["qr", "hadamard"])
def test_scan_equals_query_dot_reconstruction(whiten, rotation):
    train, db, q = _data()
    pca = _fitted(train, 32, whiten)
    pipe = pca.with_quantizer(bits=3, rotation=rotation)
    index = ADCIndex(pipe, metric="inner_product").add(db)

    recon = pipe.decompress_batch(pipe.compress_batch(db))
    exact = q.astype(np.float64) @ recon.astype(np.float64).T
    got = _full_scores(index, q)

    scale = np.abs(exact).max()
    assert np.abs(got - exact).max() <= REL * scale


def test_linear_in_the_query_where_cosine_is_invariant():
    train, db, q = _data()
    pca = _fitted(train, 32)
    pipe = pca.with_quantizer(bits=4)
    ip = ADCIndex(pipe, metric="inner_product").add(db)
    cos = ADCIndex(pipe, metric="cosine").add(db)

    # A score is qbias + cnorm * adc, two float32 terms that nearly cancel for
    # scores near zero, so the tolerance is relative to the scale of the scores,
    # not to each element (float32 rounding measured at 1.6e-6 of the scale).
    s = 3.7
    base = _full_scores(ip, q)
    tol = 1e-5 * s * np.abs(base).max()
    np.testing.assert_allclose(_full_scores(ip, s * q), s * base, rtol=0, atol=tol)
    np.testing.assert_allclose(_full_scores(ip, -q), -base, rtol=0, atol=tol / s)
    np.testing.assert_allclose(
        _full_scores(cos, s * q), _full_scores(cos, q), rtol=1e-5, atol=1e-6
    )


def test_recovers_inner_product_neighbours_cosine_cannot(no_kernel):
    train, db, q = _data()
    truth = np.argsort(-(q @ db.T), axis=1)[:, :10]
    # The check has something to find: the exact cosine order is not the exact
    # inner-product order on this data.
    cos_truth = np.argsort(-exact_scores(q, db, "cosine"), axis=1)[:, :10]
    assert _recall(cos_truth, truth) < 0.5

    pca = _fitted(train, 64)
    pipe = pca.with_quantizer(bits=4)
    ip_ids, _ = ADCIndex(pipe, metric="inner_product").add(db).search(q, k=10)
    cos_ids, _ = ADCIndex(pipe, metric="cosine").add(db).search(q, k=10)
    r_ip, r_cos = _recall(ip_ids, truth), _recall(cos_ids, truth)
    assert r_ip >= 0.8
    assert r_ip - r_cos >= 0.3


def test_two_map_consumer_basis_scores_the_mapped_pair(no_kernel):
    """Queries and rows through different maps A and B: the index over B x,
    searched with A q, scores (A q) . recon(B x). Norms change under both maps,
    so this is the case cosine cannot express."""
    train, db, q = _data()
    rng = np.random.default_rng(5)
    a = (rng.standard_normal((32, 64)) / 8.0).astype(np.float32)
    stretch = np.diag(rng.uniform(0.3, 3.0, 32))
    b = (stretch @ rng.standard_normal((32, 64)) / 8.0).astype(np.float32)
    pca = _fitted(train @ b.T, 32)
    pipe = pca.with_quantizer(bits=4)
    index = ADCIndex(pipe, metric="inner_product").add(db @ b.T)

    recon = pipe.decompress_batch(pipe.compress_batch(db @ b.T))
    exact = (q @ a.T).astype(np.float64) @ recon.astype(np.float64).T
    got = _full_scores(index, q @ a.T)
    assert np.abs(got - exact).max() <= REL * np.abs(exact).max()


# --------------------------------------------------------------------------- #
# Reranking orders by the metric, everywhere                                   #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("metric", METRICS)
def test_flat_rerank_is_exact_in_the_metric(metric):
    train, db, q = _data(n_db=600)
    pca = _fitted(train, 16)
    index = ADCIndex(pca.with_quantizer(bits=2), metric=metric).add(db)
    # rerank depth covers the whole corpus, so the result is exact search
    got = index.search(q, k=10, rerank=len(db), originals=db)
    want = np.argsort(-exact_scores(q, db, metric), axis=1, kind="stable")[:, :10]
    np.testing.assert_array_equal(got, want)


def test_the_rerank_metrics_disagree_on_this_data():
    """Without this, the rerank tests above could pass with any one metric."""
    _, db, q = _data(n_db=600)
    tops = {m: np.argsort(-exact_scores(q, db, m), axis=1)[:, :10] for m in METRICS}
    for a in METRICS:
        for b in METRICS:
            if a < b:
                assert not np.array_equal(tops[a], tops[b]), (a, b)


def test_ivf_rerank_is_the_flat_rerank():
    train, db, q = _data(n_db=1200)
    ivf = IVFIndex.create(
        np.concatenate([train, db]), output_dim=16, bits=2, nlist=8, seed=0
    )
    corpus = np.concatenate([train, db])
    ids, _ = ivf.search(q, k=10, nprobe=8, rerank=len(corpus))
    want = np.argsort(-exact_scores(q, corpus, "cosine"), axis=1, kind="stable")
    np.testing.assert_array_equal(ids, want[:, :10])


def test_ivf_adaptive_stop_refuses_a_non_cosine_score():
    train, db, q = _data(n_db=400)
    ivf = IVFIndex.create(db, output_dim=16, bits=2, nlist=4, seed=0)
    ivf._adc._metric = "inner_product"  # IVF's builders make cosine indexes only
    with pytest.raises(ValueError, match="adaptive probing"):
        ivf.search(q, k=5)
    ids, _ = ivf.search(q, k=5, nprobe=4)
    assert ids.shape == (len(q), 5)


def test_tqe_index_inner_product_round_trip(tmp_path):
    train, db, q = _data(n_db=500)
    idx = TQEIndex.create(db, output_dim=32, bits=4, metric="inner_product", seed=3)
    path = str(tmp_path / "ip.tqe")
    idx.save(path)
    back = TQEIndex.open(path)
    a_ids, a_sc = idx.search(q, k=10)
    b_ids, b_sc = back.search(q, k=10)
    np.testing.assert_array_equal(a_ids, b_ids)
    np.testing.assert_array_equal(a_sc, b_sc)
    rr, _ = back.search(q, k=10, rerank=len(db))
    want = np.argsort(-(q @ db.T), axis=1, kind="stable")[:, :10]
    np.testing.assert_array_equal(rr, want)


def test_cold_tier_rerank_in_inner_product():
    _, db, q = _data(n_db=300)
    cand = np.tile(np.arange(len(db)), (len(q), 1))
    ids, sc = rerank_candidates(q, cand, 10, lambda i: db[i], metric="inner_product")
    want = np.argsort(-(q @ db.T), axis=1, kind="stable")[:, :10]
    np.testing.assert_array_equal(ids, want)
    np.testing.assert_allclose(
        sc, np.take_along_axis(q @ db.T, want, axis=1), rtol=1e-5
    )


# --------------------------------------------------------------------------- #
# The compiled kernel                                                          #
# --------------------------------------------------------------------------- #

needs_kernel = pytest.mark.skipif(
    ai._adc.load() is None, reason="the ADC kernel is not compiled"
)


@needs_kernel
def test_kernel_scans_inner_product_with_a_unit_denominator():
    train, db, q = _data()
    pca = _fitted(train, 32)
    index = ADCIndex(pca.with_quantizer(bits=4), metric="inner_product").add(db)
    assert index._kernel_scan()
    scale = index._row_scale()
    np.testing.assert_array_equal(scale, np.ones(index.size, np.float32))
    assert index._row_scale() is scale  # cached
    index.add(db[:7])
    assert len(index._row_scale()) == index.size  # resized after add


@needs_kernel
def test_kernel_inner_product_within_its_rounding_bound():
    """The kernel rounds each table entry ``q_rot[j] * cent[s]`` to a uint8 step
    of ``scale = max_j range_j / 255``, so each entry is off by at most
    ``scale / 2`` and a row's lookup sum by at most ``d * scale / 2``. The score
    multiplies that sum by ``cnorm`` (and by one, under inner product), so

        |kernel - exact| <= cnorm[n] * d * scale / 2.

    This is derived from the kernel's arithmetic, so it holds on any data.
    The 5%-of-top-k-spread rule of tests/test_kernel_contract.py was measured
    on cosine scores and does not transfer: under inner product the error
    scales with each row's own norm, and these rows have lognormal norms."""
    train, db, q = _data()
    pca = _fitted(train, 32)
    index = ADCIndex(pca.with_quantizer(bits=4), metric="inner_product").add(db)
    ids, sc = index.search(q, k=10)
    ref = np.take_along_axis(_full_scores(index, q), ids, axis=1)

    q_rot, _ = index._query_terms(q)
    cent = index._cent
    scale = np.abs(q_rot).max(axis=1) * (cent.max() - cent.min()) / 255.0
    bound = index._cnorm[ids] * index.dim * scale[:, None] / 2.0
    fp32 = 1e-5 * np.abs(ref)  # float32 arithmetic after the exact integer sum
    err = np.abs(sc - ref)
    assert (err <= bound + fp32).all()
    # the bound is attained in order of magnitude, not vacuous
    assert (err / bound).max() > 0.01


@needs_kernel
def test_kernel_pruned_inner_product_returns_kernel_scores():
    train, db, q = _data()
    pca = _fitted(train, 32)
    index = ADCIndex(pca.with_quantizer(bits=4), metric="inner_product").add(db)
    full_ids, full_sc = index.search(q, k=10)
    p_ids, p_sc = index.search(q, k=10, prune=(0.5, 6.0))
    # a returned score is the unpruned kernel score of that row
    all_ids, all_sc = index.search(q, k=index.size)
    lookup = np.take_along_axis(all_sc, np.argsort(all_ids, axis=1), axis=1)
    np.testing.assert_allclose(
        p_sc, np.take_along_axis(lookup, p_ids, axis=1), rtol=1e-6, atol=1e-6
    )
    assert _recall(p_ids, full_ids) >= 0.95
