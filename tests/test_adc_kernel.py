"""The compiled ADC kernel against an exact integer reference of its own arithmetic.

The kernel quantizes each query's lookup table to uint8 and sums the lookups. The
reference below recomputes that uint8 LUT exactly (same float32 operations) and sums in
int64, so the kernel must return the same top-k scores: any accumulator wraparound, or
a packing or top-k bug, shows up as a mismatch. v1 of the kernel summed in uint16 and
wrapped for d' > 257, which only this kind of test catches. Skipped when the kernel is
not compiled (``python -m turboquant_pro._adc``).
"""

import numpy as np
import pytest

from turboquant_pro import ADCIndex, PCAMatryoshka, _adc

kernel = _adc.load()
pytestmark = pytest.mark.skipif(kernel is None, reason="ADC kernel not compiled")


def _index(n, dim, out_dim, bits, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal((n, dim)).astype(np.float32)
    x /= np.linalg.norm(x, axis=1, keepdims=True)
    pca = PCAMatryoshka(input_dim=dim, output_dim=out_dim)
    pca.fit(x[: min(n, 4000)])
    ix = ADCIndex(pca.with_quantizer(bits=bits, seed=seed)).add(x)
    q = x[:17] + 0.05 * rng.standard_normal((17, dim)).astype(np.float32)
    return ix, q


def _uint8_reference(ix, q_rot, qbias, k):
    """Exact integer replay of the kernel's SIMD score; top-k scores per query."""
    cent = ix._cent.astype(np.float32)
    codes = ix._codes
    d = codes.shape[1]
    out = []
    for qi in range(len(q_rot)):
        lut_f = (q_rot[qi][:, None].astype(np.float32) * cent[None, :]).astype(
            np.float32
        )
        dmin = lut_f.min(axis=1)
        rmax = np.float32(
            max(np.float32((lut_f.max(axis=1) - dmin).max()), np.float32(1e-20))
        )
        scale = np.float32(rmax / np.float32(255.0))
        bias = np.float32(0.0)
        for j in range(d):  # float32 accumulation in the kernel's order
            bias = np.float32(bias + dmin[j])
        u = ((lut_f - dmin[:, None]) / scale + np.float32(0.5)).astype(np.int64)
        u = np.clip(u, 0, 255)
        acc = u[np.arange(d)[None, :], codes].sum(axis=1)
        s = (
            np.float32(qbias[qi]) + ix._cnorm * (scale * acc.astype(np.float32) + bias)
        ) * ix._vrnorm
        out.append(np.sort(s.astype(np.float32))[::-1][:k])
    return np.array(out)


@pytest.mark.parametrize("out_dim", [16, 255, 256, 257, 512, 1024])
@pytest.mark.parametrize("bits", [2, 3, 4])
def test_simd_matches_uint8_reference(out_dim, bits):
    dim = max(out_dim, 64)
    ix, q = _index(3000 + 7, dim, out_dim, bits)  # N not a multiple of 32
    q_rot, qbias = ix._query_terms(q)
    k = 25
    _, sk = kernel.search(
        ix._codes, q_rot, ix._cent, ix._cnorm, ix._vrnorm, qbias, k, True
    )
    ref = _uint8_reference(ix, q_rot, qbias, k)
    np.testing.assert_allclose(sk, ref, rtol=2e-5, atol=2e-6)


@pytest.mark.parametrize("out_dim,bits", [(64, 4), (600, 2), (1536, 3)])
def test_scalar_path_matches_numpy(out_dim, bits):
    ix, q = _index(2000, max(out_dim, 64), out_dim, bits, seed=1)
    q_rot, qbias = ix._query_terms(q)
    k = 30
    ik, sk = kernel.search(
        ix._codes, q_rot, ix._cent, ix._cnorm, ix._vrnorm, qbias, k, False
    )
    inp, snp = ix._search_numpy(q_rot, qbias, k)
    np.testing.assert_allclose(sk, snp.astype(np.float32), rtol=2e-4, atol=2e-5)


def test_k_larger_than_corpus_pads():
    ix, q = _index(40, 32, 16, 4)
    q_rot, qbias = ix._query_terms(q)
    ik, sk = kernel.search(
        ix._codes, q_rot, ix._cent, ix._cnorm, ix._vrnorm, qbias, 50, True
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
