# TurboQuant Pro: Open-source TurboQuant for LLM KV cache compression
# Copyright (c) 2026 Andrew H. Bond
# MIT License

"""Certificates expire: what a certificate records so it can later be found
no longer applicable, and the checks that decide it.

A rank certificate says that a statement was true for an observer under an
environment: these inputs, this read operator, this calibration sample. When
the observer's read geometry changes, or the data drifts out of the
calibration's coverage, the certificate is not false; it is no longer
applicable. That is a different thing from monitoring, which reports drift:
this is invalidation, a status with a reason and an action, computed from
what the certificate itself recorded at issue (issue #177, phase 1;
``docs/DESIGN_certificate_expiry.md``).

Two sketches travel in the certificate's additive ``validity`` section:

- an **operator sketch**, the top eigenvectors of the reference read operator
  and the fraction of its trace they carry, so a later operator's overlap
  with the certified read subspace can be measured, not only its hash
  compared;
- a **coverage sketch**, per-channel mean and variance of the certified
  sample and its row count, so later data can be tested against the
  calibration's coverage without storing a ``D x D`` covariance.

The thresholds the status is decided against are recorded beside them.
"""

from __future__ import annotations

from typing import Any

import numpy as np

DEFAULT_MIN_OVERLAP = 0.85
DEFAULT_MAX_DIVERGENCE = 0.5
DEFAULT_SKETCH_CAP = 8
MIN_SKETCH_TRACE = 0.8
VALID, STALE, UNCHECKED = "VALID", "STALE", "UNCHECKED"

__all__ = [
    "DEFAULT_MIN_OVERLAP",
    "DEFAULT_MAX_DIVERGENCE",
    "DEFAULT_SKETCH_CAP",
    "operator_sketch",
    "coverage_sketch",
    "validity_section",
    "operator_overlap",
    "coverage_divergence",
    "check_validity",
    "validity_summary",
]


def _round(a: np.ndarray, digits: int = 6) -> list:
    return [float(f"{v:.{digits}g}") for v in np.asarray(a, dtype=np.float64).ravel()]


def operator_sketch(P: np.ndarray, cap: int = DEFAULT_SKETCH_CAP) -> dict:
    """The top ``r`` eigenvectors of a PSD read operator, ``r`` the ceiling of
    its effective rank up to ``cap``, with the fraction of the trace they
    carry. A flat operator (identity, or nearly) gets a sketch that carries
    little of the trace, and the overlap check says so instead of testing
    against arbitrary directions."""
    A = np.asarray(P, dtype=np.float64)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("a read operator must be a square matrix")
    A = 0.5 * (A + A.T)
    vals, vecs = np.linalg.eigh(A)
    order = np.argsort(vals)[::-1]
    vals, vecs = np.clip(vals[order], 0.0, None), vecs[:, order]
    trace = float(vals.sum())
    s2 = float((vals**2).sum())
    eff = (trace * trace / s2) if s2 > 0 else 0.0
    r = int(min(max(1, int(np.ceil(eff))), cap, vals.size))
    carried = float(vals[:r].sum() / trace) if trace > 0 else 0.0
    return {
        "dim": int(A.shape[0]),
        "rank": r,
        "effective_rank": eff,
        "trace": trace,
        "trace_fraction": carried,
        "eigenvalues": _round(vals[:r]),
        "basis": [_round(vecs[:, i]) for i in range(r)],
    }


def coverage_sketch(sample: np.ndarray) -> dict:
    """Per-channel mean and variance of the certified sample."""
    x = np.asarray(sample, dtype=np.float64)
    x = x.reshape(-1, x.shape[-1])
    return {
        "rows": int(x.shape[0]),
        "dim": int(x.shape[1]),
        "mean": _round(x.mean(axis=0)),
        "variance": _round(x.var(axis=0)),
    }


def validity_section(
    *,
    observer_sha256: str | None = None,
    reference: dict | None = None,
    operator: np.ndarray | None = None,
    sample: np.ndarray | None = None,
    min_overlap: float = DEFAULT_MIN_OVERLAP,
    max_divergence: float = DEFAULT_MAX_DIVERGENCE,
    sketch_cap: int = DEFAULT_SKETCH_CAP,
) -> dict:
    """The ``validity`` section of a certificate."""
    issued: dict[str, Any] = {"observer_sha256": observer_sha256}
    if reference:
        issued["reference_provider"] = reference.get("provider")
        issued["operator_sha256"] = reference.get("operator_sha256")
    out: dict[str, Any] = {
        "issued_for": issued,
        "thresholds": {
            "min_operator_overlap": float(min_overlap),
            "max_coverage_divergence": float(max_divergence),
        },
        "operator_sketch": (
            operator_sketch(operator, sketch_cap) if operator is not None else None
        ),
        "coverage_sketch": coverage_sketch(sample) if sample is not None else None,
    }
    return out


def operator_overlap(sketch: dict, P_new: np.ndarray) -> float:
    """``tr(U^T P' U) / tr(P')``: the fraction of the new operator's sensitivity
    that lies inside the certified read subspace ``U``."""
    U = np.asarray(sketch["basis"], dtype=np.float64).T  # (D, r)
    A = np.asarray(P_new, dtype=np.float64)
    A = 0.5 * (A + A.T)
    if A.shape != (U.shape[0], U.shape[0]):
        raise ValueError(
            f"new operator is {A.shape}; the sketch is {U.shape[0]}-dimensional"
        )
    t = float(np.trace(A))
    if t <= 0:
        return 0.0
    return float(np.clip(np.trace(U.T @ A @ U) / t, 0.0, 1.0))


def coverage_divergence(sketch: dict, sample: np.ndarray, ridge: float = 1e-9) -> float:
    """Diagonal Jeffreys divergence per channel between the certified sample's
    moments and a new sample's, averaged over channels: zero when the moments
    agree, growing with a mean shift measured in either variance and with a
    variance mismatch in either direction."""
    x = np.asarray(sample, dtype=np.float64)
    x = x.reshape(-1, x.shape[-1])
    m1 = np.asarray(sketch["mean"], dtype=np.float64)
    v1 = np.asarray(sketch["variance"], dtype=np.float64) + ridge
    if x.shape[1] != m1.size:
        raise ValueError(f"sample has {x.shape[1]} channels; the sketch has {m1.size}")
    m2 = x.mean(axis=0)
    v2 = x.var(axis=0) + ridge
    per = 0.5 * (v1 / v2 + v2 / v1 - 2.0) + 0.5 * (m1 - m2) ** 2 * (1.0 / v1 + 1.0 / v2)
    return float(per.mean())


def _rebuild_operator(doc: dict, contract, data: np.ndarray, queries):
    """The observer's operator on new data: from the contract when one is
    given, else from the certificate's recorded reference provider."""
    if contract is not None:
        from turboquant_pro.refinement import observer_operator

        return observer_operator(contract, data, queries=queries), "contract"
    ref = doc.get("reference")
    if ref and ref.get("provider"):
        from turboquant_pro.read_operators import create_read_operator

        op = create_read_operator(ref["provider"], **(ref.get("config") or {}))
        x = np.asarray(data, dtype=np.float64).reshape(-1, np.shape(data)[-1])
        return (
            np.asarray(op.operator(x, queries=queries), dtype=np.float64),
            "reference",
        )
    return None, None


def check_validity(
    doc: dict,
    *,
    contract=None,
    data: np.ndarray | None = None,
    queries: np.ndarray | None = None,
    inputs_ok: bool | None = None,
) -> dict:
    """Decide whether a certificate is still applicable.

    ``inputs_ok`` is the recompute's hash verdict when one ran. ``contract``
    is the observer contract the certificate should have been issued for
    (its hash is compared with ``validity.issued_for`` and the top-level
    ``observer`` section). ``data`` is a sample of the current serving
    distribution, with ``queries`` for a retrieval consumer's operator.
    """
    v = doc.get("validity") or {}
    checks: dict[str, Any] = {}
    reasons: list[str] = []
    actions: list[str] = []

    checks["source_artifact"] = (
        {"status": "not_checked"}
        if inputs_ok is None
        else {"status": "ok" if inputs_ok else "FAIL"}
    )
    if inputs_ok is False:
        reasons.append("certified inputs changed")
        actions.append("RECERTIFY")

    if contract is not None:
        recorded = (doc.get("observer") or {}).get("sha256") or (
            v.get("issued_for") or {}
        ).get("observer_sha256")
        ok = recorded == contract.digest()
        checks["observer_contract"] = {
            "status": "ok" if ok else "FAIL",
            "recorded": recorded,
            "given": contract.digest(),
        }
        if not ok:
            reasons.append(
                "certificate names no observer"
                if not recorded
                else "observer contract changed"
            )
            actions.append("REPLAN")
    else:
        checks["observer_contract"] = {"status": "not_checked"}

    sk = v.get("operator_sketch")
    th = v.get("thresholds") or {}
    if data is not None and sk:
        if sk.get("trace_fraction", 0.0) < MIN_SKETCH_TRACE:
            checks["operator_overlap"] = {
                "status": "not_checked",
                "reason": (
                    f"the certified operator is not low-rank (its top {sk['rank']} "
                    f"directions carry {sk['trace_fraction']:.2f} of the trace); "
                    "overlap is not a meaningful test"
                ),
            }
        else:
            P_new, source = _rebuild_operator(doc, contract, data, queries)
            if P_new is None:
                checks["operator_overlap"] = {
                    "status": "not_checked",
                    "reason": "no contract and no recorded reference provider",
                }
            else:
                ov = operator_overlap(sk, P_new)
                lim = float(th.get("min_operator_overlap", DEFAULT_MIN_OVERLAP))
                ok = ov >= lim
                checks["operator_overlap"] = {
                    "status": "ok" if ok else "FAIL",
                    "overlap": ov,
                    "min": lim,
                    "operator_from": source,
                }
                if not ok:
                    reasons.append("consumer read geometry changed")
                    actions.append("REPLAN")
    else:
        checks["operator_overlap"] = {"status": "not_checked"}

    cs = v.get("coverage_sketch")
    if data is not None and cs:
        div = coverage_divergence(cs, data)
        lim = float(th.get("max_coverage_divergence", DEFAULT_MAX_DIVERGENCE))
        ok = div <= lim
        checks["data_coverage"] = {
            "status": "ok" if ok else "FAIL",
            "divergence": div,
            "max": lim,
            "rows": int(np.shape(data)[0]),
        }
        if not ok:
            reasons.append("data outside calibration coverage")
            actions.append("RECERTIFY")
    else:
        checks["data_coverage"] = {"status": "not_checked"}

    checks["strata_coverage"] = {"status": "not_checked", "reason": "phase 2"}

    statuses = [c["status"] for c in checks.values()]
    if "FAIL" in statuses:
        status = STALE
    elif "ok" in statuses:
        status = VALID
    else:
        status = UNCHECKED
    action = None
    if actions:
        # REPLAN subsumes RECERTIFY: a changed observer needs a new plan first
        action = "REPLAN" if "REPLAN" in actions else "RECERTIFY"
    return {
        "status": status,
        "applicable": status != STALE,
        "reason": "; ".join(reasons) if reasons else None,
        "action": action,
        "checks": checks,
    }


def validity_summary(result: dict) -> str:
    labels = {
        "source_artifact": "source artifact unchanged",
        "observer_contract": "observer contract unchanged",
        "operator_overlap": "observer read geometry",
        "data_coverage": "data within calibration coverage",
        "strata_coverage": "strata coverage",
    }
    lines = ["CERTIFICATE STATUS"]
    for key, c in result["checks"].items():
        st = c["status"]
        detail = ""
        if key == "operator_overlap" and "overlap" in c:
            detail = f" (overlap {c['overlap']:.2f}, min {c['min']:.2f})"
        elif key == "data_coverage" and "divergence" in c:
            detail = f" (divergence {c['divergence']:.3f}, max {c['max']:.2f})"
        elif st == "not_checked" and c.get("reason"):
            detail = f" ({c['reason']})"
        lines.append(f"  {labels[key]:<34} {st}{detail}")
    tail = f"STATUS: {result['status']}"
    if result.get("reason"):
        tail += f"   reason: {result['reason']}"
    if result.get("action"):
        tail += f"   action: {result['action']}"
    lines.append(tail)
    return "\n".join(lines)
