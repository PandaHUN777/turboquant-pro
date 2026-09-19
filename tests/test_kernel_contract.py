# TurboQuant Pro: Open-source TurboQuant for LLM KV cache compression
# Copyright (c) 2026 Andrew H. Bond. MIT License.
"""What the compiled ADC kernel promises, and what it does not (issue #171).

For a long time four tests in the index and IVF suites asserted that a search
returns identical neighbour ids whichever way the index was opened. That is
true with no kernel built, and false with one, because the two sides of

    if self._mmap or block is not None or exact:   # numpy, exact float ADC
    else:                                          # compiled kernel, uint8 LUT

are different scorers rather than two orderings of one. The kernel quantizes
its per-dim table to 255 levels of a query-global scale, which is what makes
it fast; the cost is a score that differs from the exact one by the table's
resolution, and a top-k boundary that can reorder within it.

These tests pin the promise that is actually true:

* with the kernel suppressed, every path agrees bit for bit (the original
  guarantee, kept where it holds);
* with the kernel present, its scores sit within a bounded fraction of the
  top-k score spread;
* and its disagreements with the exact ranking are confined to that margin,
  so it only reorders neighbours it cannot resolve.

The bound is 5% of the top-k score spread. Measured on Atlas across six
shapes (n 800 to 4000, dim 48 to 128, output 16 to 128, bits 2 to 4) the worst
observed was 2.3%; 5% leaves room for a different machine's rounding without
being loose enough to hide a real regression.
"""

from __future__ import annotations

import numpy as np
import pytest

from turboquant_pro import TQEIndex, _adc
from turboquant_pro import adc_index as ai

SPREAD_FRACTION = 0.05


def _corpus(n=800, dim=48, seed=0):
    rng = np.random.default_rng(seed)
    return rng.standard_normal((n, dim)).astype(np.float32)


@pytest.fixture
def no_kernel(monkeypatch):
    """Every ADCIndex built inside this fixture scores in numpy."""
    monkeypatch.setattr(ai._adc, "load", lambda: None)
    return True


# --------------------------------------------------------------------------- #
# What holds in every build                                                     #
# --------------------------------------------------------------------------- #


def test_exact_is_reproducible_across_layouts(tmp_path):
    """exact=True must not depend on how the index was opened. This is the
    guarantee `tqp certify` anchors and claim replay rely on."""
    x = _corpus()
    idx = TQEIndex.create(x, output_dim=32, bits=4, seed=11, keep_originals=False)
    p = tmp_path / "e.tqe"
    idx.save(str(p))
    q = x[:40]
    a, asc = idx.search(q, k=10, exact=True)
    b, bsc = TQEIndex.open(str(p)).search(q, k=10, exact=True)
    c, csc = TQEIndex.open(str(p), mmap=True).search(q, k=10, exact=True)
    d, dsc = idx.search(q, k=10, exact=True, block=128)
    for other, osc in ((b, bsc), (c, csc), (d, dsc)):
        np.testing.assert_array_equal(a, other)
        np.testing.assert_allclose(asc, osc, rtol=0, atol=0)


def test_exact_and_blocked_agree_bitwise():
    x = _corpus()
    idx = TQEIndex.create(x, output_dim=32, bits=4, seed=11)
    q = x[:20]
    a, asc = idx.search(q, k=10, exact=True)
    b, bsc = idx.search(q, k=10, block=256)
    np.testing.assert_array_equal(a, b)
    np.testing.assert_allclose(asc, bsc, rtol=0, atol=0)


def test_without_a_kernel_every_path_agrees_bitwise(no_kernel):
    """The original guarantee, kept where it is true."""
    x = _corpus()
    idx = TQEIndex.create(x, output_dim=32, bits=4, seed=11)
    q = x[:20]
    a, asc = idx.search(q, k=10)
    b, bsc = idx.search(q, k=10, block=256)
    np.testing.assert_array_equal(a, b)
    np.testing.assert_allclose(asc, bsc, rtol=0, atol=0)
    assert not idx._adc.uses_kernel


# --------------------------------------------------------------------------- #
# What the kernel promises when it is there                                     #
# --------------------------------------------------------------------------- #

kernel_only = pytest.mark.skipif(
    not _adc.is_available(), reason="needs the compiled ADC kernel"
)


def _exact_scores(idx, q, n):
    ids, sc = idx.search(q, k=n, exact=True)
    return (
        [{int(i): float(s) for i, s in zip(ids[r], sc[r])} for r in range(len(q))],
        ids,
        sc,
    )


@kernel_only
@pytest.mark.parametrize(
    "n,dim,out_dim,bits", [(800, 48, 32, 4), (800, 48, 32, 3), (1200, 64, 16, 4)]
)
def test_kernel_scores_stay_within_the_table_resolution(n, dim, out_dim, bits):
    x = _corpus(n, dim)
    idx = TQEIndex.create(x, output_dim=out_dim, bits=bits, seed=11)
    q = x[:24]
    exact_of, exact_ids, exact_sc = _exact_scores(idx, q, n)
    kern_ids, kern_sc = idx.search(q, k=10)

    dev = 0.0
    for r in range(len(q)):
        for i, s in zip(kern_ids[r], kern_sc[r]):
            e = exact_of[r].get(int(i))
            if e is not None:
                dev = max(dev, abs(float(s) - e))
    spread = float(np.mean([exact_sc[r][0] - exact_sc[r][-1] for r in range(len(q))]))
    assert spread > 0
    assert dev <= SPREAD_FRACTION * spread, (
        f"kernel score deviates {dev:.3e}, more than {SPREAD_FRACTION:.0%} of the "
        f"top-k spread {spread:.3e}: this is a real accuracy regression, not "
        "the lookup table's resolution"
    )


@kernel_only
def test_kernel_only_reorders_neighbours_it_cannot_resolve():
    """Every id the kernel and the exact path disagree on must sit within the
    kernel's own deviation of the k-th exact score. A disagreement further out
    than that would mean the kernel picked a neighbour it could tell was worse."""
    n, k = 800, 10
    x = _corpus(n)
    idx = TQEIndex.create(x, output_dim=32, bits=4, seed=11)
    q = x[:24]
    exact_of, exact_ids, exact_sc = _exact_scores(idx, q, n)
    kern_ids, kern_sc = idx.search(q, k=k)

    dev = max(
        abs(float(s) - exact_of[r][int(i)])
        for r in range(len(q))
        for i, s in zip(kern_ids[r], kern_sc[r])
        if int(i) in exact_of[r]
    )
    tol = 2.0 * dev + 1e-6  # the boundary is decided by two scores, each off by dev
    worst = 0.0
    for r in range(len(q)):
        kth = float(exact_sc[r][k - 1])
        symmetric = set(kern_ids[r].tolist()) ^ set(exact_ids[r][:k].tolist())
        for i in symmetric:
            e = exact_of[r].get(int(i))
            if e is not None:
                worst = max(worst, abs(e - kth))
    assert worst <= tol, (
        f"an id the two paths disagree on sits {worst:.3e} from the k-th exact "
        f"score, beyond the kernel's own deviation {dev:.3e}"
    )


@kernel_only
def test_the_kernel_keeps_nearly_all_of_the_exact_neighbours():
    x = _corpus(1500, 64)
    idx = TQEIndex.create(x, output_dim=32, bits=4, seed=3)
    q = x[:40]
    exact_ids, _ = idx.search(q, k=10, exact=True)
    kern_ids, _ = idx.search(q, k=10)
    per_query = [
        len(set(kern_ids[r].tolist()) & set(exact_ids[r].tolist())) / 10
        for r in range(len(q))
    ]
    assert np.mean(per_query) >= 0.95
    assert np.min(per_query) >= 0.7


@kernel_only
def test_rerank_removes_the_difference():
    """The two-stage path is the answer to the boundary reordering: an exact
    rescoring of a wider candidate set lands on the same neighbours."""
    x = _corpus(1000, 64)
    idx = TQEIndex.create(x, output_dim=32, bits=4, seed=5)
    q = x[:30]
    a, _ = idx.search(q, k=10, rerank=8)
    b, _ = idx.search(q, k=10, rerank=8, exact=True)
    agree = np.mean(
        [len(set(a[r].tolist()) & set(b[r].tolist())) / 10 for r in range(len(q))]
    )
    assert agree >= 0.99
