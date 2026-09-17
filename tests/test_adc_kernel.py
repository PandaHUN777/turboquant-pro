"""The compiled ADC kernel against an exact integer reference of its own arithmetic.

The kernel quantizes each query's lookup table to uint8 and sums the lookups. The
reference below recomputes that uint8 LUT exactly (same float32 operations) and sums in
int64, so the kernel must return the same top-k scores: any accumulator wraparound, or
a packing or top-k bug, shows up as a mismatch. v1 of the kernel summed in uint16 and
wrapped for d' > 257, which only this kind of test catches. v3 scans chunks of codes
packed once in the blocked layout, with a symbol table per dim and dims grouped into
weighted segments; the reference covers those too. Skipped when the kernel is not
compiled (``python -m turboquant_pro._adc``).
"""

import numpy as np
import pytest

from turboquant_pro import ADCIndex, PCAMatryoshka, _adc
from turboquant_pro.packed_codes import (
    BlockedCodes,
    blocked_nbytes,
    pack_blocks,
    unpack_blocks,
)

kernel = _adc.load()
pytestmark = pytest.mark.skipif(kernel is None, reason="ADC kernel not compiled")


def _index(n, dim, out_dim, bits, seed=0, batches=1):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal((n, dim)).astype(np.float32)
    x /= np.linalg.norm(x, axis=1, keepdims=True)
    pca = PCAMatryoshka(input_dim=dim, output_dim=out_dim)
    pca.fit(x[: min(n, 4000)])
    ix = ADCIndex(pca.with_quantizer(bits=bits, seed=seed))
    for part in np.array_split(x, batches):
        ix.add(part)
    q = x[:17] + 0.05 * rng.standard_normal((17, dim)).astype(np.float32)
    return ix, q


def _replay(codes, tables, nsym, segs, segw, q_rot, vnorm, vrnorm, biases, k):
    """Exact integer replay of the kernel's SIMD score; top-k scores per query.

    ``tables`` (d, 16), ``nsym`` (d,), ``segs`` (nseg + 1,), ``segw`` (N, nseg) or
    None, ``biases`` (Q,) the per-query constant of the single chunk scanned.
    """
    codes = np.asarray(codes)
    d = codes.shape[1]
    nseg = len(segs) - 1
    out = []
    for qi in range(len(q_rot)):
        lut = (q_rot[qi][:, None].astype(np.float32) * tables).astype(np.float32)
        used = np.arange(16)[None, :] < nsym[:, None]
        dmin = np.where(used, lut, np.inf).min(axis=1).astype(np.float32)
        dmax = np.where(used, lut, -np.inf).max(axis=1).astype(np.float32)
        rmax = np.float32(max(np.float32((dmax - dmin).max()), np.float32(1e-20)))
        scale = np.float32(rmax / np.float32(255.0))
        segbias = []
        for g in range(nseg):
            b = np.float32(0.0)
            for j in range(
                segs[g], segs[g + 1]
            ):  # float32 accumulation in kernel order
                b = np.float32(b + dmin[j])
            segbias.append(b)
        u = ((lut - dmin[:, None]) / scale + np.float32(0.5)).astype(np.int64)
        u = np.where(used, np.clip(u, 0, 255), 0)
        looked = u[np.arange(d)[None, :], codes]  # (N, d)
        inner = np.zeros(len(codes), np.float32)
        for g in range(nseg):
            acc = looked[:, segs[g] : segs[g + 1]].sum(axis=1)
            term = (scale * acc.astype(np.float32) + segbias[g]).astype(np.float32)
            if segw is not None:
                term = (segw[:, g].astype(np.float32) * term).astype(np.float32)
            inner = (inner + term).astype(np.float32)
        s = ((np.float32(biases[qi]) + vnorm * inner) * vrnorm).astype(np.float32)
        out.append(np.sort(s)[::-1][:k])
    return np.array(out)


def _uniform_reference(ix, q_rot, qbias, k):
    return _replay(
        np.asarray(ix._codes),
        ix._coder.tables,
        ix._coder.nsym,
        ix._coder.segs,
        None,
        q_rot,
        ix._cnorm,
        ix._vrnorm,
        qbias,
        k,
    )


# --------------------------------------------------------------------------- #
# The legacy entry point (plain codes, one table)                             #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("out_dim", [16, 255, 256, 257, 512, 1024])
@pytest.mark.parametrize("bits", [2, 3, 4])
def test_simd_matches_uint8_reference(out_dim, bits):
    dim = max(out_dim, 64)
    ix, q = _index(3000 + 7, dim, out_dim, bits)  # N not a multiple of 32
    q_rot, qbias = ix._query_terms(q)
    k = 25
    _, sk = kernel.search(
        np.asarray(ix._codes), q_rot, ix._cent, ix._cnorm, ix._vrnorm, qbias, k, True
    )
    ref = _uniform_reference(ix, q_rot, qbias, k)
    np.testing.assert_allclose(sk, ref, rtol=2e-5, atol=2e-6)


@pytest.mark.parametrize("out_dim,bits", [(64, 4), (600, 2), (1536, 3)])
def test_scalar_path_matches_numpy(out_dim, bits):
    ix, q = _index(2000, max(out_dim, 64), out_dim, bits, seed=1)
    q_rot, qbias = ix._query_terms(q)
    k = 30
    ik, sk = kernel.search(
        np.asarray(ix._codes), q_rot, ix._cent, ix._cnorm, ix._vrnorm, qbias, k, False
    )
    inp, snp = ix._search_numpy(q_rot, qbias, k)
    np.testing.assert_allclose(sk, snp.astype(np.float32), rtol=2e-4, atol=2e-5)


def test_k_larger_than_corpus_pads():
    ix, q = _index(40, 32, 16, 4)
    q_rot, qbias = ix._query_terms(q)
    ik, sk = kernel.search(
        np.asarray(ix._codes), q_rot, ix._cent, ix._cnorm, ix._vrnorm, qbias, 50, True
    )
    assert (ik[:, :40] >= 0).all() and (ik[:, 40:] == -1).all()
    assert np.all(np.diff(sk[:, :40], axis=1) <= 0)  # descending
    assert sorted(ik[0, :40].tolist()) == list(range(40))


@pytest.mark.parametrize("d", [256, 257, 1024, 1536])
def test_maximal_sums_do_not_wrap(d):
    """Vectors whose every lookup is 255 must rank first (v1 wrapped at d > 257).

    Random data rarely reaches the wrap (on real 1536-d embeddings it hit only a few
    top-scoring vectors), so the regression is pinned with a constructed worst case.
    """
    S, n = 16, 1000
    cent = np.linspace(-1.0, 1.0, S).astype(np.float32)  # code 15 has the largest entry
    rng = np.random.default_rng(5)
    # ordinary vectors: low codes
    codes = rng.integers(0, 8, size=(n, d), dtype=np.uint8)
    best = rng.choice(n, 5, replace=False)
    codes[best] = 15  # every dim at the table maximum: uint8 lookup sum = 255 * d
    q_rot = np.ones((1, d), np.float32)
    ones = np.ones(n, np.float32)
    idx, sc = kernel.search(
        codes, q_rot, cent, ones, ones, np.zeros(1, np.float32), 5, True
    )
    assert sorted(idx[0].tolist()) == sorted(best.tolist())
    # score = scale * 255d + bias = (2/255) * 255d - d = d; a wrapped sum changes it
    np.testing.assert_allclose(sc[0], d, rtol=1e-4)


# --------------------------------------------------------------------------- #
# v3: the blocked layout, chunks, per-dim tables, segments                    #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("n,d", [(1, 3), (32, 8), (33, 8), (1000, 257)])
def test_pack_blocks_matches_kernel_pack_and_round_trips(n, d):
    rng = np.random.default_rng(n * 31 + d)
    codes = rng.integers(0, 16, size=(n, d), dtype=np.uint8)
    blocked = pack_blocks(codes)
    assert blocked.dtype == np.uint8 and blocked.size == blocked_nbytes(n, d)
    np.testing.assert_array_equal(blocked, kernel.pack(codes))
    np.testing.assert_array_equal(unpack_blocks(blocked, n, d), codes)
    rows = rng.integers(0, n, size=min(n, 50))
    np.testing.assert_array_equal(unpack_blocks(blocked, n, d, rows), codes[rows])


def test_blocked_codes_reads_like_an_array():
    rng = np.random.default_rng(9)
    codes = rng.integers(0, 16, size=(100, 12), dtype=np.uint8)
    bc = BlockedCodes.from_codes(codes, kernel)
    assert bc.shape == (100, 12) and len(bc) == 100 and bc.nbytes == 4 * 12 * 16
    np.testing.assert_array_equal(np.asarray(bc), codes)
    np.testing.assert_array_equal(bc[7], codes[7])
    np.testing.assert_array_equal(bc[-1], codes[-1])
    np.testing.assert_array_equal(bc[10:45], codes[10:45])
    rows = np.asarray([99, 0, 33, 33])
    np.testing.assert_array_equal(bc[rows], codes[rows])
    mask = codes[:, 0] > 7
    np.testing.assert_array_equal(bc[mask], codes[mask])
    with pytest.raises(ValueError):
        BlockedCodes.from_codes(np.full((4, 4), 16, np.uint8))


@pytest.mark.parametrize(
    "out_dim,bits,batches", [(64, 4, 3), (300, 3, 5), (1024, 2, 2)]
)
def test_chunked_index_scans_like_one_chunk(out_dim, bits, batches):
    """add() in batches leaves several chunks; the scan and the legacy view agree."""
    ix, q = _index(3000 + 11, max(out_dim, 64), out_dim, bits, seed=2, batches=batches)
    assert len(ix._chunks) == batches and all(c.scannable for c in ix._chunks)
    one, _ = _index(3000 + 11, max(out_dim, 64), out_dim, bits, seed=2, batches=1)
    np.testing.assert_array_equal(np.asarray(ix._codes), np.asarray(one._codes))
    q_rot, qbias = ix._query_terms(q)
    k = 20
    idx_c, sc_c = ix.search(q, k=k)
    idx_1, sc_1 = one.search(q, k=k)
    np.testing.assert_allclose(sc_c, sc_1, rtol=1e-6, atol=1e-7)
    assert all(set(a) == set(b) for a, b in zip(idx_c, idx_1))
    ref = _uniform_reference(ix, q_rot, qbias, k)
    np.testing.assert_allclose(sc_c, ref, rtol=2e-5, atol=2e-6)
    # in RAM: half a byte per code plus two float32 per row
    assert (
        ix.nbytes
        <= 1.05 * (ix.size * out_dim / 2 + 8 * ix.size) + 16 * out_dim * batches
    )


def test_probe_subset_equals_scan_of_those_chunks():
    ix, q = _index(2000 + 5, 64, 48, 4, seed=3, batches=4)
    q_rot, qbias = ix._query_terms(q)
    nc = len(ix._chunks)
    probes = np.broadcast_to(np.asarray([0, 2, -1, -1], np.int32), (len(q), 4))
    biases = np.broadcast_to(qbias[:, None], (len(q), 4))
    idx, sc = ix.search_chunks(q_rot, probes, biases, 15)
    starts = np.concatenate([[0], np.cumsum([c.n for c in ix._chunks])[:-1]])
    rows = np.concatenate(
        [np.arange(starts[c], starts[c] + ix._chunks[c].n) for c in (0, 2)]
    )
    assert all(set(r) <= set(rows) for r in idx)
    full_idx, full_sc = ix.search_chunks(
        q_rot,
        np.broadcast_to(np.arange(nc, dtype=np.int32), (len(q), nc)),
        np.broadcast_to(qbias[:, None], (len(q), nc)),
        ix.size,
    )
    for i in range(len(q)):
        want = {
            int(r): float(s) for r, s in zip(full_idx[i], full_sc[i]) if r in set(rows)
        }
        top = sorted(want.values(), reverse=True)[:15]
        np.testing.assert_allclose(sc[i], top, rtol=1e-6, atol=1e-7)


def test_per_dim_tables_and_segments_match_integer_reference():
    """Dims with their own tables and symbol counts, two weighted segments."""
    rng = np.random.default_rng(11)
    N, d, k = 3000 + 13, 200, 20
    nsym = rng.choice([4, 8, 16], size=d).astype(np.int32)
    tables = np.zeros((d, 16), np.float32)
    for j in range(d):
        tables[j, : nsym[j]] = np.sort(rng.standard_normal(nsym[j])).astype(np.float32)
    codes = np.stack(
        [rng.integers(0, nsym[j], size=N) for j in range(d)], axis=1
    ).astype(np.uint8)
    segs = np.asarray([0, 70, d], np.int32)
    segw = rng.uniform(0.2, 1.0, size=(N, 2)).astype(np.float32)
    vnorm = rng.uniform(0.5, 2.0, size=N).astype(np.float32)
    vrnorm = rng.uniform(0.5, 2.0, size=N).astype(np.float32)
    q_rot = rng.standard_normal((9, d)).astype(np.float32)
    biases = rng.standard_normal(9).astype(np.float32)
    parts = [1000, 1000, N - 2000]
    blocks, ns, offsets = [], [], []
    s = 0
    for n in parts:
        blocks.append(pack_blocks(codes[s : s + n]))
        ns.append(n)
        offsets.append(s)
        s += n
    for use_simd in (True, False):
        idx, sc = kernel.search_chunks(
            blocks,
            np.asarray(ns, np.int64),
            np.asarray(offsets, np.int64),
            q_rot,
            tables,
            nsym,
            segs,
            vnorm,
            vrnorm,
            segw,
            np.broadcast_to(np.arange(3, dtype=np.int32), (9, 3)),
            np.broadcast_to(biases[:, None], (9, 3)),
            k,
            use_simd,
        )
        if use_simd:
            ref = _replay(
                codes, tables, nsym, segs, segw, q_rot, vnorm, vrnorm, biases, k
            )
            np.testing.assert_allclose(sc, ref, rtol=2e-5, atol=2e-6)
        # the returned rows' exact float scores: tight on the float-LUT scalar path,
        # loose on the SIMD path, whose uint8 tables round each lookup (about one
        # percent of the score here, with random tables and weights)
        for i in range(9):
            cc = tables[np.arange(d)[None, :], codes[idx[i]]]
            inner = np.zeros(k, np.float32)
            for g in range(2):
                inner += segw[idx[i], g] * (
                    cc[:, segs[g] : segs[g + 1]] @ q_rot[i, segs[g] : segs[g + 1]]
                )
            exact = (biases[i] + vnorm[idx[i]] * inner) * vrnorm[idx[i]]
            tol = 3e-2 if use_simd else 2e-4
            np.testing.assert_allclose(sc[i], exact, rtol=tol, atol=tol)


def test_search_chunks_rejects_malformed_inputs():
    ix, q = _index(100, 32, 16, 4)
    q_rot, qbias = ix._query_terms(q)
    good = dict(probes=np.zeros((len(q), 1), np.int32), biases=qbias[:, None])
    with pytest.raises(ValueError):
        ix.search_chunks(q_rot, np.full((len(q), 1), 5, np.int32), good["biases"], 5)
    with pytest.raises(ValueError):
        ix.search_chunks(q_rot[:, :8], good["probes"], good["biases"], 5)


# --------------------------------------------------------------------------- #
# Two-pass pruned scan (experimental, docs/PREREG_pruned_scan.md)             #
# --------------------------------------------------------------------------- #


def _structured_index(n, dim, out_dim, bits, seed=0):
    """Low-rank data with near-duplicate neighbours, so pruning has work to do."""
    rng = np.random.default_rng(seed)
    basis = rng.standard_normal((32, dim)).astype(np.float32)
    x = rng.standard_normal((n, 32)).astype(np.float32) @ basis
    x += 0.3 * rng.standard_normal((n, dim)).astype(np.float32)
    x /= np.linalg.norm(x, axis=1, keepdims=True)
    pca = PCAMatryoshka(input_dim=dim, output_dim=out_dim)
    pca.fit(x[: min(n, 4000)])
    ix = ADCIndex(pca.with_quantizer(bits=bits, seed=seed)).add(x)
    q = x[:25] + 0.02 * rng.standard_normal((25, dim)).astype(np.float32)
    return ix, q


def _pruned_args(ix, q):
    q_rot, qbias = ix._query_terms(q)
    chunk = ix._chunks[0]
    return (
        chunk.codes.blocked,
        chunk.n,
        q_rot,
        ix._coder.tables,
        ix._coder.nsym,
        ix._cnorm,
        ix._vrnorm,
        qbias,
    )


def _plain_args(ix, q):
    q_rot, qbias = ix._query_terms(q)
    return (np.asarray(ix._codes), q_rot, ix._cent, ix._cnorm, ix._vrnorm, qbias)


@pytest.mark.parametrize("out_dim,bits", [(64, 4), (300, 2), (1024, 3)])
def test_pruned_without_pruning_equals_unpruned(out_dim, bits):
    ix, q = _structured_index(3000 + 11, max(out_dim, 64), out_dim, bits)
    ia, sa = kernel.search(*_plain_args(ix, q), 20, True)
    ib, sb, surv = kernel.search_pruned(
        *_pruned_args(ix, q), ix.code_frequencies(), 20, out_dim // 4, 1e9
    )
    assert (surv == ix.size).all()
    np.testing.assert_array_equal(sb, sa)
    assert all(set(x) == set(y) for x, y in zip(ia, ib))


@pytest.mark.parametrize(
    "out_dim,bits,m", [(128, 4, 32), (512, 2, 128), (1024, 4, 512)]
)
def test_pruned_scores_are_exact_and_recall_holds(out_dim, bits, m):
    ix, q = _structured_index(4000, max(out_dim, 64), out_dim, bits, seed=2)
    k = 10
    all_ids, all_sc = kernel.search(*_plain_args(ix, q), ix.size, True)
    ref = [dict(zip(all_ids[i].tolist(), all_sc[i].tolist())) for i in range(len(q))]
    ib, sb, surv = kernel.search_pruned(
        *_pruned_args(ix, q), ix.code_frequencies(), k, m, 3.0
    )
    for i in range(len(q)):  # each returned score equals the unpruned score of that id
        for n, s in zip(ib[i], sb[i]):
            assert ref[i][int(n)] == pytest.approx(float(s), rel=1e-6, abs=1e-7)
    recall = np.mean([len(set(ib[i]) & set(all_ids[i, :k])) / k for i in range(len(q))])
    assert recall >= 0.95
    assert surv.mean() < ix.size  # something was pruned


def test_pruned_k_larger_than_corpus_pads():
    ix, q = _structured_index(40, 64, 32, 4)
    ib, sb, surv = kernel.search_pruned(
        *_pruned_args(ix, q), ix.code_frequencies(), 50, 8, 3.0
    )
    assert (ib[:, :40] >= 0).all() and (ib[:, 40:] == -1).all()
    assert (
        surv == 40
    ).all()  # no threshold exists while fewer than k lower bounds are known


def test_index_search_prune_option_matches_default():
    ix, q = _structured_index(2000, 128, 96, 4, seed=4)
    ids_default, _ = ix.search(q, k=10)
    ids_pruned, _ = ix.search(q, k=10, prune=(0.25, 1e9))
    assert all(set(x) == set(y) for x, y in zip(ids_default, ids_pruned))
    assert ix.last_survivors.shape == (len(q),)


# --------------------------------------------------------------------------- #
# A segmented (spectrum) index through the kernel                             #
# --------------------------------------------------------------------------- #


def test_segmented_index_matches_integer_reference_and_numpy():
    rng = np.random.default_rng(21)
    n, dim = 3000 + 9, 96
    x = rng.standard_normal((n, dim)).astype(np.float32) * (0.95 ** np.arange(dim))
    x /= np.linalg.norm(x, axis=1, keepdims=True)
    pca = PCAMatryoshka(input_dim=dim, output_dim=72)
    pca.fit(x[:2000])
    pipe = pca.with_weighted_quantizer(bit_schedule=[(24, 4), (24, 3), (24, 1)])
    ix = ADCIndex(pipe).add(x[:1000]).add(x[1000:])
    assert ix._kernel_scan() and ix._coder.nseg == 3
    q = x[:11] + 0.03 * rng.standard_normal((11, dim)).astype(np.float32)
    q_rot, qbias = ix._query_terms(q)
    k = 20
    idx, sc = ix.search(q, k=k)
    ref = _replay(
        np.asarray(ix._codes),
        ix._coder.tables,
        ix._coder.nsym,
        ix._coder.segs,
        ix._segw,
        q_rot,
        ix._cnorm,
        ix._vrnorm,
        qbias,
        k,
    )
    np.testing.assert_allclose(sc, ref, rtol=2e-5, atol=2e-6)
    inp, snp = ix._search_numpy(q_rot, qbias, k)
    # the uint8 tables round each lookup, so the kernel's ranking is the exact
    # ranking up to table noise: the top-k sets overlap almost entirely
    overlap = np.mean([len(set(a) & set(b)) / k for a, b in zip(idx, inp)])
    assert overlap >= 0.9
