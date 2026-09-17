# TurboQuant Pro: Open-source TurboQuant for LLM KV cache compression
# Copyright (c) 2026 Andrew H. Bond
# MIT License

"""Bits that follow the spectrum: integer bit allocation over PCA dimensions.

A PCA-Matryoshka pipeline quantizes every retained dimension at the same width.
The public RaBitQ comparison (``docs/PREREG_rabitq_public.md``, interim scoring
2026-09-17) showed that uniform widths lose at both ends of the byte axis: at
equal bytes, half the dims at 4 bits beat all of them at 2, and more dims at 2
bits beat fewer at 4 when bytes are scarce. The optimum sits between: more bits
on the leading components, fewer on the tail, none on the dims not worth a bit.

This module chooses that allocation. Given eigenvalues ``lambda_j`` (the
variance each PCA dimension carries) and a budget of bits per vector, it picks
``b_j`` from a set of widths to minimise the expected reconstruction error

    sum_j lambda_j * D(b_j),

where ``D(b)`` is the relative mean-squared error of the Lloyd-Max quantizer for
a Gaussian coordinate at ``b`` bits (``D(0) = 1``: the dimension is dropped).
The marginal gain of one more bit decreases with ``b``, so the greedy allocation
that repeatedly spends a bit where it buys the most is optimal, and because the
eigenvalues are sorted the result is monotone in ``j``: the widths form
contiguous segments, which is exactly the shape :class:`EigenweightedPipeline`
quantizes and the v3 scan kernel scores.
"""

from __future__ import annotations

import heapq

import numpy as np

# Relative MSE of the Lloyd-Max quantizer of a standard normal coordinate
# (Max 1960; Lloyd 1982): the fraction of the coordinate's variance that
# survives quantization. 0 bits means the coordinate is not stored.
DISTORTION: dict[int, float] = {
    0: 1.0,
    1: 0.3634,
    2: 0.1175,
    3: 0.03454,
    4: 0.009497,
}


def allocate_bits(
    eigenvalues: np.ndarray,
    budget_bits: int,
    choices: tuple[int, ...] = (0, 1, 2, 3, 4),
) -> np.ndarray:
    """Widths ``b_j`` (one per dimension) minimising ``sum lambda_j D(b_j)`` under
    ``sum b_j <= budget_bits``, each ``b_j`` drawn from ``choices``.

    Every dimension starts at the smallest choice; bits are then spent one step
    at a time where the gain per bit is largest, ties going to the earlier (larger)
    eigenvalue, until the budget cannot pay for any further step. With the
    consecutive widths ``(0, 1, 2, 3, 4)`` this is the exact optimum; with a
    thinned set such as ``(2, 3, 4)`` it is the same greedy rule on the steps
    that remain.
    """
    lam = np.asarray(eigenvalues, dtype=np.float64).reshape(-1)
    if lam.size == 0:
        return np.zeros(0, dtype=np.int64)
    if np.any(lam < 0):
        raise ValueError("eigenvalues must be non-negative")
    levels = sorted({int(c) for c in choices})
    if not levels or levels[0] < 0 or levels[-1] > max(DISTORTION):
        raise ValueError(f"choices must lie in 0..{max(DISTORTION)}, got {choices}")
    d = lam.size
    lo = levels[0]
    if budget_bits < lo * d:
        raise ValueError(
            f"budget {budget_bits} bits cannot give {d} dims the minimum width {lo}"
        )
    bits = np.full(d, lo, dtype=np.int64)
    level_at = np.zeros(d, dtype=np.int64)  # index into ``levels`` per dim
    remaining = int(budget_bits) - lo * d

    def step(j: int):
        """The next step for dim j as ``(-gain_per_bit, j, cost)``, or None."""
        i = level_at[j]
        if i + 1 >= len(levels):
            return None
        b0, b1 = levels[i], levels[i + 1]
        gain = lam[j] * (DISTORTION[b0] - DISTORTION[b1])
        return (-(gain / (b1 - b0)), j, b1 - b0)

    heap = [s for s in (step(j) for j in range(d)) if s is not None]
    heapq.heapify(heap)
    while heap and remaining > 0:
        neg_gain, j, cost = heapq.heappop(heap)
        if cost > remaining:
            continue  # this dim's next step does not fit; larger ones will not either
        if neg_gain == 0.0:
            break  # nothing left to gain: a zero eigenvalue is not worth a bit
        level_at[j] += 1
        bits[j] = levels[level_at[j]]
        remaining -= cost
        nxt = step(j)
        if nxt is not None:
            heapq.heappush(heap, nxt)
    return bits


def segments(bits: np.ndarray) -> list[tuple[int, int]]:
    """Runs of equal width, in order: ``[(n_dims, bits), ...]``. Dropped dims
    (``bits == 0``) are omitted; on a sorted spectrum they form the tail."""
    bits = np.asarray(bits, dtype=np.int64).reshape(-1)
    out: list[tuple[int, int]] = []
    for b in bits:
        b = int(b)
        if b == 0:
            continue
        if out and out[-1][1] == b:
            out[-1] = (out[-1][0] + 1, b)
        else:
            out.append((1, b))
    return out


def expected_distortion(eigenvalues: np.ndarray, bits: np.ndarray) -> float:
    """``sum_j lambda_j D(b_j) / sum_j lambda_j``: the variance fraction lost."""
    lam = np.asarray(eigenvalues, dtype=np.float64).reshape(-1)
    bits = np.asarray(bits, dtype=np.int64).reshape(-1)
    if lam.size != bits.size:
        raise ValueError("eigenvalues and bits must have the same length")
    total = float(lam.sum())
    if total <= 0:
        return 0.0
    return float(
        sum(lam[j] * DISTORTION[int(bits[j])] for j in range(lam.size)) / total
    )


def stored_bytes(
    bits: np.ndarray, per_segment_bytes: int = 1, norm_bytes: int = 4
) -> int:
    """Bytes per vector a segmented index stores for this allocation: each
    segment's codes packed at its width, one norm, and one energy fraction per
    segment (one byte each by default)."""
    segs = segments(bits)
    codes = sum(-(-n * b // 8) for n, b in segs)
    return int(codes + norm_bytes + per_segment_bytes * len(segs))


def allocate_for_bytes(
    eigenvalues: np.ndarray,
    budget_bytes: int,
    choices: tuple[int, ...] = (0, 1, 2, 3, 4),
    per_segment_bytes: int = 1,
    norm_bytes: int = 4,
) -> np.ndarray:
    """Allocation whose :func:`stored_bytes` does not exceed ``budget_bytes``.

    The per-segment overhead depends on how many segments the allocation
    produces, so the bit budget is refined until the stored size fits.
    """
    lam = np.asarray(eigenvalues, dtype=np.float64).reshape(-1)
    nseg = 1
    for _ in range(8):
        bit_budget = 8 * (int(budget_bytes) - norm_bytes - per_segment_bytes * nseg)
        if bit_budget < 0:
            raise ValueError(f"budget of {budget_bytes} bytes cannot hold a vector")
        bits = allocate_bits(lam, bit_budget, choices)
        size = stored_bytes(bits, per_segment_bytes, norm_bytes)
        if size <= budget_bytes:
            return bits
        nseg = max(nseg + 1, len(segments(bits)))
    raise RuntimeError("bit allocation did not converge to the byte budget")


def plan_for_bytes(
    eigenvalues: np.ndarray,
    budget_bytes: int,
    choices: tuple[int, ...] = (0, 1, 2, 3, 4),
    per_segment_bytes: int = 1,
    norm_bytes: int = 4,
) -> tuple[int, list[tuple[int, int]]]:
    """From the full spectrum, the ``(output_dim, schedule)`` a pipeline needs at
    ``budget_bytes``: the dims given a non-zero width (a prefix, since the widths
    are monotone on a sorted spectrum) and their contiguous segments. Fit the PCA
    at ``output_dim`` and pass ``schedule`` to ``with_weighted_quantizer``."""
    bits = allocate_for_bytes(
        eigenvalues, budget_bytes, choices, per_segment_bytes, norm_bytes
    )
    kept = int((bits > 0).sum())
    if kept and bits[:kept].min() == 0:
        raise ValueError("widths are not a prefix: pass a spectrum sorted descending")
    return kept, segments(bits)
