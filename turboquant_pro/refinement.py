# TurboQuant Pro: Open-source TurboQuant for LLM KV cache compression
# Copyright (c) 2026 Andrew H. Bond
# MIT License

"""Successive refinement across observers: can two readers share a code?

Observation Theory's two-observer region (geometric-observation, Paper III)
says when a base description for one observer can be refined into one for a
second without paying twice, and when it cannot: the refinement is free when
the two read operators share their eigendirections, and costs a tax that grows
with how differently they weigh the directions. This module makes that a
number before anything is built (issue #174, phase 1).

The model. A code quantizes the source in one orthonormal basis ``U`` at
integer widths ``b_i`` per direction, drawn from the widths the v3 scan
stores (0 to 4 bits). The error along ``u_i`` has variance
``sigma_i^2 D(b_i)`` with ``D`` the Lloyd-Max distortion table of
:mod:`turboquant_pro.spectrum`, and the errors are independent across
directions, so an observer with read operator ``P`` sees

    d_P(b; U) = sum_i (u_i^T P u_i) sigma_i^2 D(b_i).

Only the diagonal of ``P`` in the code's basis enters, exactly, because the
error covariance is diagonal there. Four quantities follow.

- **alone**: each observer at its own budget in its own eigenbasis, the
  spectrum allocation of :func:`turboquant_pro.spectrum.allocate_bits`; its
  distortion ``d*`` is the quality that observer would have had by itself.
- **progressive**: the base observer's allocation, then bits added in the
  same basis where they cut the second observer's distortion most per bit,
  until it reaches its ``d*``. The base reader reads the base bytes; the
  second reads base plus layer.
- **flat joint**: one code in the eigenbasis of the average operator meeting
  both ``d*`` at once, the fewest bits a single representation needs.
- **separate**: two codes, the sum of the budgets.

The **refinement tax** is the progressive total over the flat joint total,
minus one. Small means the observers can share a representation and the
first can stop early; large means they are geometrically incompatible and
two representations cost less than one layered one. The **overlap**
``tr(P_A P_B) / (||P_A|| ||P_B||)`` says why.

This is a prediction from the distortion table, the same one the spectrum
allocation was preregistered and measured on (``benchmarks/RESULTS_spectrum_bits.md``).
The layered container that stores base and refinement, and the measurement
of a real reader against it, are the later phases of #174.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from turboquant_pro.spectrum import DISTORTION, allocate_bits

NORM_BYTES = 4
DEFAULT_TAX_THRESHOLD = 0.15

__all__ = [
    "ObserverGeometry",
    "RefinementReport",
    "observer_operator",
    "refinement_report",
    "layer_bytes",
]


def layer_bytes(bits: np.ndarray, *, norm: bool = True) -> int:
    """Stored bytes per row for a width vector: packed bits, plus the norm."""
    total = int(np.asarray(bits).sum())
    return -(-total // 8) + (NORM_BYTES if norm else 0)


def _symmetric(P: np.ndarray) -> np.ndarray:
    A = np.asarray(P, dtype=np.float64)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("a read operator must be a square matrix")
    return 0.5 * (A + A.T)


def _eigenbasis(P: np.ndarray) -> np.ndarray:
    vals, vecs = np.linalg.eigh(_symmetric(P))
    order = np.argsort(vals)[::-1]
    return np.ascontiguousarray(vecs[:, order])


def _variance_along(basis: np.ndarray, x: np.ndarray) -> np.ndarray:
    centred = x - x.mean(axis=0, keepdims=True)
    proj = centred @ basis
    return np.maximum((proj**2).mean(axis=0), 0.0)


def _sensitivity_along(basis: np.ndarray, P: np.ndarray) -> np.ndarray:
    """``u_i^T P u_i`` for each column: the diagonal of ``P`` in the basis."""
    return np.maximum(np.einsum("ij,jk,ki->i", basis.T, _symmetric(P), basis), 0.0)


def _distortion(weights: np.ndarray, bits: np.ndarray) -> float:
    d = np.array([DISTORTION[int(b)] for b in bits])
    return float(np.sum(weights * d))


def _greedy_until(
    targets: list[tuple[np.ndarray, float]],
    bits: np.ndarray,
    levels: list[int],
) -> tuple[np.ndarray, bool]:
    """Add width steps, largest drop of the worst normalised distortion per
    bit first, until every ``(weights, ceiling)`` pair is met. Returns the
    widths and whether every target was met before the widths ran out."""
    bits = bits.copy()
    d = bits.size
    idx = {lvl: i for i, lvl in enumerate(levels)}
    level_at = np.array([idx[int(b)] for b in bits])

    def worst(b: np.ndarray) -> float:
        return max(_distortion(w, b) / c if c > 0 else 0.0 for w, c in targets)

    current = worst(bits)
    if current <= 1.0:
        return bits, True

    def step(j: int):
        i = level_at[j]
        if i + 1 >= len(levels):
            return None
        b0, b1 = levels[i], levels[i + 1]
        # the drop of the worst normalised distortion from one step on dim j
        trial = bits.copy()
        trial[j] = b1
        gain = current - worst(trial)
        return (-(gain / (b1 - b0)), j, b1)

    heap = [s for s in (step(j) for j in range(d)) if s is not None]
    heapq.heapify(heap)
    while heap and current > 1.0:
        neg_gain, j, b1 = heapq.heappop(heap)
        # the gain was computed against an older ``current``; recompute and
        # re-queue if it went stale (another dim moved since), so the greedy
        # stays exact for the objective it claims
        fresh = step(j)
        if fresh is None:
            continue
        if fresh[0] > neg_gain + 1e-15:
            heapq.heappush(heap, fresh)
            continue
        level_at[j] += 1
        bits[j] = levels[level_at[j]]
        current = worst(bits)
        nxt = step(j)
        if nxt is not None:
            heapq.heappush(heap, nxt)
    return bits, current <= 1.0


@dataclass(frozen=True)
class ObserverGeometry:
    """One observer as the planner sees it: a label, its read operator on the
    channel axis, and the bytes per vector it is allowed."""

    label: str
    operator: np.ndarray
    budget_bytes: float
    meta: dict = field(default_factory=dict)

    @property
    def budget_bits(self) -> int:
        return int(max(0.0, (self.budget_bytes - NORM_BYTES)) * 8)


@dataclass
class RefinementReport:
    base: str
    refined: str
    dim: int
    overlap: float
    alone: dict
    progressive: dict
    flat: dict
    separate: dict
    tax: float | None
    tax_threshold: float
    verdict: str
    reason: str
    meta: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "schema": "turboquant-pro/refinement-report",
            "schema_version": 1,
            "base": self.base,
            "refined": self.refined,
            "dim": self.dim,
            "overlap": self.overlap,
            "alone": self.alone,
            "progressive": self.progressive,
            "flat": self.flat,
            "separate": self.separate,
            "tax": self.tax,
            "tax_threshold": self.tax_threshold,
            "verdict": self.verdict,
            "reason": self.reason,
            **self.meta,
        }

    def explain(self) -> str:
        L = ["SUCCESSIVE REFINEMENT REPORT"]
        L.append(
            f"Observers: {self.base} (base), {self.refined} (refined)   dim {self.dim}"
        )
        L.append(f"Read-operator overlap: {self.overlap:.3f}")
        for k, v in self.alone.items():
            L.append(
                f"  {k} alone: {v['bytes']} B/vec, consumer distortion "
                f"{v['distortion_fraction']:.4f} of unstored"
            )
        p = self.progressive
        if p["feasible"]:
            L.append(
                f"Progressive: base {p['base_bytes']} B + layer {p['layer_bytes']} B "
                f"= {p['total_bytes']} B/vec"
            )
        else:
            L.append(
                "Progressive: the refined observer's target is not reachable by "
                "adding bits in the base's basis"
            )
        L.append(f"Flat joint code meeting both: {self.flat['bytes']} B/vec")
        L.append(f"Separate representations: {self.separate['bytes']} B/vec (sum)")
        if self.tax is not None:
            L.append(
                f"Refinement tax: {self.tax * 100:+.1f}% "
                f"(threshold {self.tax_threshold * 100:.0f}%)"
            )
        L.append(f"VERDICT: {self.verdict}")
        L.append(f"  {self.reason}")
        return "\n".join(L)


def observer_operator(
    contract: Any,
    activations: np.ndarray,
    *,
    queries: np.ndarray | None = None,
) -> np.ndarray:
    """A contract's read operator on the channel axis: the weighted sum of
    its consumers' operators. A ``read_operator`` consumer asks its
    registered provider; a top-k retrieval consumer reads along the
    queries, ``E[q q^T]`` over unit queries, since its score is ``q . x``,
    and reads every direction equally when no queries are given; any other
    consumer reads every direction equally and says so in ``meta``."""
    from turboquant_pro.read_operators import create_read_operator

    x = np.asarray(activations, dtype=np.float64).reshape(-1, np.shape(activations)[-1])
    d = x.shape[1]
    weights = contract.normalized_weights()
    P = np.zeros((d, d))
    for c in contract.consumers:
        w = weights[c.label]
        if c.metric == "read_operator":
            cfg = dict(c.config)
            provider = cfg.pop("provider")
            op = create_read_operator(provider, **cfg)
            Pc = np.asarray(op.operator(x, queries=queries), dtype=np.float64)
        elif c.metric.startswith("topk_") and queries is not None:
            q = np.asarray(queries, dtype=np.float64).reshape(-1, d)
            q = q / np.maximum(np.linalg.norm(q, axis=1, keepdims=True), 1e-12)
            Pc = (q.T @ q) / q.shape[0]
        else:
            Pc = np.eye(d)
        P += w * _symmetric(Pc)
    return P


def refinement_report(
    activations: np.ndarray,
    a: ObserverGeometry,
    b: ObserverGeometry,
    *,
    tax_threshold: float = DEFAULT_TAX_THRESHOLD,
    choices: tuple[int, ...] = (0, 1, 2, 3, 4),
) -> RefinementReport:
    """Whether observers ``a`` and ``b`` should share a progressive code.

    ``a`` is the base (its budget is the smaller one; the two are swapped
    if not). Distortions are reported as fractions of the observer's
    distortion when nothing is stored, ``tr(P Sigma)``, so 0.01 means the
    code leaves one percent of what the observer reads.
    """
    x = np.asarray(activations, dtype=np.float64)
    x = x.reshape(-1, x.shape[-1])
    d = x.shape[1]
    for g in (a, b):
        if np.shape(g.operator) != (d, d):
            raise ValueError(
                f"observer {g.label!r}: operator is {np.shape(g.operator)}, "
                f"activations have {d} channels"
            )
    if b.budget_bytes < a.budget_bytes:
        a, b = b, a
    levels = sorted({int(c) for c in choices})
    if levels[0] != 0:
        levels = [0] + levels

    # ---- alone ------------------------------------------------------------
    alone: dict = {}
    d_star: dict = {}
    for g in (a, b):
        U = _eigenbasis(g.operator)
        var = _variance_along(U, x)
        sens = _sensitivity_along(U, g.operator)
        w = sens * var
        unstored = float(w.sum())
        bits = allocate_bits(w, g.budget_bits, tuple(levels))
        dist = _distortion(w, bits)
        d_star[g.label] = dist
        alone[g.label] = {
            "bytes": layer_bytes(bits),
            "budget_bytes": g.budget_bytes,
            "bits_total": int(bits.sum()),
            "distortion": dist,
            "distortion_fraction": dist / unstored if unstored > 0 else 0.0,
            "unstored_distortion": unstored,
        }

    # ---- progressive: A's basis, A's allocation, then B's refinement -------
    U = _eigenbasis(a.operator)
    var = _variance_along(U, x)
    wa = _sensitivity_along(U, a.operator) * var
    wb = _sensitivity_along(U, b.operator) * var
    base_bits = allocate_bits(wa, a.budget_bits, tuple(levels))
    total_bits, feasible = _greedy_until([(wb, d_star[b.label])], base_bits, levels)
    base_bytes = layer_bytes(base_bits)
    total_bytes = layer_bytes(total_bits)
    progressive = {
        "basis": a.label,
        "feasible": bool(feasible),
        "base_bytes": base_bytes,
        "layer_bytes": total_bytes - base_bytes,
        "total_bytes": total_bytes,
        "base_bits_total": int(base_bits.sum()),
        "total_bits_total": int(total_bits.sum()),
        "distortion_base_for_base": _distortion(wa, base_bits),
        "distortion_total_for_refined": _distortion(wb, total_bits),
        "distortion_total_for_base": _distortion(wa, total_bits),
    }

    # ---- flat joint: the average operator's basis, both targets at once ----
    Pj = 0.5 * (_symmetric(a.operator) + _symmetric(b.operator))
    Uj = _eigenbasis(Pj)
    varj = _variance_along(Uj, x)
    wja = _sensitivity_along(Uj, a.operator) * varj
    wjb = _sensitivity_along(Uj, b.operator) * varj
    flat_bits, flat_ok = _greedy_until(
        [(wja, d_star[a.label]), (wjb, d_star[b.label])],
        np.zeros(d, dtype=np.int64),
        levels,
    )
    flat = {
        "feasible": bool(flat_ok),
        "bytes": layer_bytes(flat_bits),
        "bits_total": int(flat_bits.sum()),
        "distortion_for_base": _distortion(wja, flat_bits),
        "distortion_for_refined": _distortion(wjb, flat_bits),
    }
    separate = {"bytes": alone[a.label]["bytes"] + alone[b.label]["bytes"]}

    # ---- overlap, tax, verdict --------------------------------------------
    A, B = _symmetric(a.operator), _symmetric(b.operator)
    na, nb = np.linalg.norm(A), np.linalg.norm(B)
    overlap = float(np.trace(A @ B) / (na * nb)) if na > 0 and nb > 0 else 0.0

    tax = None
    if feasible and flat_ok and flat["bytes"] > 0:
        tax = total_bytes / flat["bytes"] - 1.0
    progressive_v = "progressive representation recommended"
    separate_v = "separate representations recommended"
    if not feasible:
        verdict = separate_v
        reason = (
            f"adding bits in {a.label}'s basis cannot bring {b.label} to the quality "
            f"it has alone at {b.budget_bytes:g} B; the readers do not share "
            f"directions (overlap {overlap:.2f})"
        )
    elif total_bytes >= separate["bytes"]:
        verdict = separate_v
        reason = (
            f"the layered code ({total_bytes} B) saves nothing over two codes "
            f"({separate['bytes']} B): {b.label}'s directions are not {a.label}'s "
            f"(overlap {overlap:.2f})"
        )
    elif not flat_ok:
        verdict = progressive_v
        reason = (
            "no single flat code meets both observers at the widths available; "
            f"the layered code does at {total_bytes} B against {separate['bytes']} B "
            f"for two codes, and {a.label} reads {base_bytes} B"
        )
    elif tax is not None and tax <= tax_threshold:
        verdict = progressive_v
        reason = (
            f"refinement tax {tax * 100:+.1f}% against one flat code; {a.label} "
            f"reads {base_bytes} B instead of {flat['bytes']} B, {b.label} reads "
            f"{total_bytes} B"
        )
    else:
        verdict = separate_v
        reason = (
            f"observers are geometrically incompatible at this tax ({tax * 100:+.1f}% "
            f"over one flat code, threshold {tax_threshold * 100:.0f}%; overlap "
            f"{overlap:.2f})"
        )
    return RefinementReport(
        base=a.label,
        refined=b.label,
        dim=d,
        overlap=overlap,
        alone=alone,
        progressive=progressive,
        flat=flat,
        separate=separate,
        tax=tax,
        tax_threshold=tax_threshold,
        verdict=verdict,
        reason=reason,
        meta={
            "widths": levels,
            "n_rows": int(x.shape[0]),
            "model": (
                "Lloyd-Max distortion table, independent errors in the code's basis"
            ),
        },
    )
