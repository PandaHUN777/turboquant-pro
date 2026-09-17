"""IVF coarse-partition layer: sublinear probing that reproduces the brute-force
ADC ranking. Validates the admissible early stop (probe-all == exact), high recall
at a small scan fraction, and the A*-style adaptive stop.
"""

from __future__ import annotations

import numpy as np

from turboquant_pro import ADCIndex, IVFIndex, PCAMatryoshka


def _corpus(n=4000, dim=64, seed=0):
    rng = np.random.default_rng(seed)
    rank = dim // 2
    basis = rng.standard_normal((rank, dim))
    coeffs = rng.standard_normal((n, rank)) * np.linspace(1.0, 0.3, rank)
    return (coeffs @ basis + 0.05 * rng.standard_normal((n, dim))).astype(np.float32)


def _brute_adc_topk(corpus, queries, k, out_dim=32, bits=4):
    pca = PCAMatryoshka(input_dim=corpus.shape[1], output_dim=out_dim)
    pca.fit(corpus)
    adc = ADCIndex(pca.with_quantizer(bits=bits)).add(corpus)
    idx, _ = adc.search(queries, k=k)
    return idx


def _recall(got, ref, k):
    return float(np.mean([len(set(a) & set(b)) / k for a, b in zip(got[:, :k], ref)]))


def test_probe_all_equals_bruteforce():
    # Probing every cell + scoring all candidates is exactly the brute ADC scan
    # (with the plain codes; residual coding changes the codes, and its probe-all
    # is compared against exact ground truth below instead).
    corpus = _corpus()
    q = corpus[:60]
    ref = _brute_adc_topk(corpus, q, 10)
    ivf = IVFIndex.create(corpus, output_dim=32, bits=4, residual=False)
    ids, _, stats = ivf.search(q, k=10, nprobe=ivf.stats()["nlist"], return_stats=True)
    assert _recall(ids, ref, 10) == 1.0  # identical ranking, no approximation
    assert all(s.scan_fraction == 1.0 for s in stats)


def test_high_recall_at_small_scan_fraction():
    corpus = _corpus()
    q = corpus[:80]
    ref = _brute_adc_topk(corpus, q, 10)
    ivf = IVFIndex.create(corpus, output_dim=32, bits=4)
    nlist = ivf.stats()["nlist"]
    # Probing a quarter of the cells (best-first) recovers most neighbours.
    ids, _, stats = ivf.search(q, k=10, nprobe=max(8, nlist // 4), return_stats=True)
    frac = float(np.mean([s.scan_fraction for s in stats]))
    assert _recall(ids, ref, 10) > 0.8
    assert frac < 0.4  # sublinear: touches well under half the corpus


def test_adaptive_weighted_stop_is_sublinear():
    corpus = _corpus()
    q = corpus[:80]
    ref = _brute_adc_topk(corpus, q, 10)
    ivf = IVFIndex.create(corpus, output_dim=32, bits=4)
    # weighted A*: shrinking the radius prunes more. beta<1 scans less than exact.
    ids, _, stats = ivf.search(
        q, k=10, nprobe=None, bound="weighted", radius_scale=0.5, return_stats=True
    )
    exact_frac = np.mean(
        [
            s.scan_fraction
            for s in ivf.search(
                q, k=10, nprobe=None, bound="admissible", return_stats=True
            )[2]
        ]
    )
    frac = float(np.mean([s.scan_fraction for s in stats]))
    assert _recall(ids, ref, 10) > 0.6  # keeps useful recall
    assert frac < exact_frac  # prunes strictly more than the admissible bound
    assert all(s.cells_probed >= 1 for s in stats)


def test_admissible_stop_is_exact():
    # The admissible bound never prunes a cell that could contain a better point,
    # so its result matches probing everything (coarse-exact), even if it scans a lot.
    corpus = _corpus(2500)
    q = corpus[:50]
    ivf = IVFIndex.create(corpus, output_dim=32, bits=4)
    exact, _ = ivf.search(q, k=10, nprobe=ivf.stats()["nlist"])
    adm, _ = ivf.search(q, k=10, nprobe=None, bound="admissible")
    assert _recall(adm, exact, 10) > 0.99  # admissible stop == full probe


def test_rerank_finds_self():
    corpus = _corpus(3000)
    ivf = IVFIndex.create(corpus, output_dim=32, bits=4, keep_originals=True)
    q = corpus[:40]
    ids, _ = ivf.search(q, k=10, nprobe=None, bound="admissible", rerank=10)
    assert all(i in ids[i] for i in range(len(q)))  # each row retrieves itself


def test_stats_and_partition_sane():
    corpus = _corpus(2000)
    ivf = IVFIndex.create(corpus, output_dim=32, bits=4, nlist=40)
    st = ivf.stats()
    assert st["nlist"] == 40
    assert st["n_rows"] == 2000
    assert st["cell_min"] >= 0 and st["cell_max"] <= 2000
    assert 0.0 <= st["radius_mean_deg"] <= 180.0


# --------------------------------------------------------------------------- #
# v3: cells are chunks; residual coding                                        #
# --------------------------------------------------------------------------- #


def _clustered(n=6000, dim=64, centers=40, seed=0, spread=0.25):
    """A mixture of tight clusters: where a centroid explains most of a row."""
    rng = np.random.default_rng(seed)
    c = rng.standard_normal((centers, dim))
    which = rng.integers(0, centers, size=n)
    x = c[which] + spread * rng.standard_normal((n, dim))
    return (x / np.linalg.norm(x, axis=1, keepdims=True)).astype(np.float32)


def test_cells_are_chunks_and_partition_covers_every_row():
    corpus = _corpus(2000)
    ivf = IVFIndex.create(corpus, output_dim=32, bits=4, nlist=40)
    assert len(ivf._adc._chunks) == 40  # one chunk per cell, empty cells included
    assert ivf._adc.size == 2000
    assert sorted(ivf._members.tolist()) == list(range(2000))
    counts = np.diff(ivf._offsets)
    assert counts.sum() == 2000 and (counts == [c.n for c in ivf._adc._chunks]).all()


def test_probe_all_without_residuals_equals_the_flat_index_exactly():
    corpus = _corpus()
    q = corpus[:60]
    ref = _brute_adc_topk(corpus, q, 10)
    ivf = IVFIndex.create(corpus, output_dim=32, bits=4, residual=False)
    ids, _, stats = ivf.search(q, k=10, nprobe=ivf.stats()["nlist"], return_stats=True)
    # the same pipeline, the same kernel, every row scanned: the same ranking
    assert _recall(ids, ref, 10) == 1.0
    assert all(s.scan_fraction == 1.0 for s in stats)


def test_residual_coding_scores_match_a_direct_reconstruction():
    corpus = _corpus(1500)
    q = corpus[:9]
    ivf = IVFIndex.create(corpus, output_dim=24, bits=4, nlist=12, residual=True)
    adc = ivf._adc
    q_rot, qbias = adc._query_terms(q)
    biases, ip = ivf._cell_terms(q_rot, qbias)
    probes = np.broadcast_to(np.arange(12, dtype=np.int32), (9, 12))
    pos, sc = adc._search_chunks_numpy(q_rot, probes, biases, 10)
    # direct: recon = c + rho * unrotate(cent[codes]) per row, cosine against q
    codes = np.asarray(adc._codes)
    rho, vr = adc._cnorm, adc._vrnorm
    cell_of = np.repeat(np.arange(12), np.diff(ivf._offsets))
    xp_hat = ivf._c[cell_of] + rho[:, None] * adc._coder.unrotate(adc._cent[codes])
    q_proj = adc._coder.unrotate(q_rot)
    direct = (qbias[:, None] + q_proj @ xp_hat.T) * vr[None, :]
    for i in range(9):
        np.testing.assert_allclose(
            sc[i], np.sort(direct[i])[::-1][:10], rtol=1e-4, atol=1e-5
        )
    # the residual norm is shorter than the row's norm
    xp = adc.project(corpus)
    assert rho.mean() < np.linalg.norm(xp, axis=1).mean()


def test_residual_coding_raises_single_pass_recall_on_clustered_data():
    corpus = _clustered()
    q = corpus[:200]
    gt = np.argsort(-(q @ corpus.T), axis=1)[:, :10]
    plain = IVFIndex.create(corpus, output_dim=32, bits=2, nlist=40, residual=False)
    resid = IVFIndex.create(corpus, output_dim=32, bits=2, nlist=40, residual=True)
    r_plain = _recall(plain.search(q, k=10, nprobe=40)[0], gt, 10)
    r_resid = _recall(resid.search(q, k=10, nprobe=40)[0], gt, 10)
    assert r_resid > r_plain + 0.05, (r_plain, r_resid)


def test_kernel_and_numpy_paths_agree_on_probed_cells():
    corpus = _corpus(3000)
    q = corpus[:20]
    ivf = IVFIndex.create(corpus, output_dim=32, bits=4, nlist=30)
    adc = ivf._adc
    if not adc.uses_kernel:
        return
    q_rot, qbias = adc._query_terms(q)
    biases, _ = ivf._cell_terms(q_rot, qbias)
    probes = np.tile(np.asarray([3, 7, 11, 29, -1], np.int32), (20, 1))
    b = np.take_along_axis(biases, np.maximum(probes, 0), axis=1)
    k_ids, k_sc = adc.search_chunks(q_rot, probes, b, 10)
    n_ids, n_sc = adc._search_chunks_numpy(q_rot, probes, b, 10)
    overlap = np.mean([len(set(a) & set(c)) / 10 for a, c in zip(k_ids, n_ids)])
    assert overlap >= 0.9  # the uint8 tables round each lookup
    np.testing.assert_allclose(k_sc[:, 0], n_sc[:, 0], rtol=3e-2)


def test_segmented_pipeline_inside_ivf():
    corpus = _corpus(2500)
    q = corpus[:30]
    ivf = IVFIndex.create(
        corpus, output_dim=32, bit_schedule=[(12, 4), (12, 2), (8, 1)], nlist=25
    )
    assert ivf._adc._coder.nseg == 3 and ivf._adc._segw.shape == (2500, 3)
    ids, _ = ivf.search(q, k=10, nprobe=25, rerank=5)
    assert all(i in ids[i] for i in range(len(q)))
    st = ivf.stats()
    assert st["stored_bytes_per_row"] == 6 + 3 + 1 + 4 + 3


def test_from_blocks_equals_create():
    corpus = _corpus(2600)
    q = corpus[:25]
    whole = IVFIndex.create(corpus, output_dim=32, bits=4, nlist=30, seed=3)
    pca = whole._adc._pca
    streamed = IVFIndex.from_blocks(
        pca,
        lambda: (corpus[s : s + 700] for s in range(0, 2600, 700)),
        n=2600,
        train=corpus,
        bits=4,
        nlist=30,
        seed=3,
    )
    np.testing.assert_array_equal(whole._members, streamed._members)
    np.testing.assert_array_equal(whole._offsets, streamed._offsets)
    np.testing.assert_array_equal(
        np.asarray(whole._adc._codes), np.asarray(streamed._adc._codes)
    )
    np.testing.assert_allclose(whole._adc._cnorm, streamed._adc._cnorm, rtol=1e-5)
    a, _ = whole.search(q, k=10, nprobe=30)
    b, _ = streamed.search(q, k=10, nprobe=30)
    np.testing.assert_array_equal(a, b)
