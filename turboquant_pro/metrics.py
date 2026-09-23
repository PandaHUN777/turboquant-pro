# TurboQuant Pro: Open-source TurboQuant for LLM KV cache compression
# Copyright (c) 2026 Andrew H. Bond
# MIT License

"""The retrieval metrics, defined once.

Three metrics rank a corpus for a query, and every part of the package that
ranks, scores or reranks means one of them:

* ``inner_product`` ranks by ``q . x``. Query and row magnitudes both count.
  It is the metric of a maximum-inner-product consumer, and the only one that
  is correct when the query and the corpus pass through different linear maps
  (a two-map consumer basis), because such maps do not preserve norms.
* ``cosine`` ranks by ``q . x / (||q|| ||x||)``. Magnitudes are discarded.
* ``l2`` ranks by ``-||q - x||^2``.

:func:`exact_scores` is the full-precision reference that consumers score
against and that exact reranking reorders by. The compressed-domain form of
the same three scores is :func:`turboquant_pro.adc_index.score_block`; the two
must name the same metrics, which is why both validate through
:func:`check_metric`.
"""

from __future__ import annotations

import numpy as np

INNER_PRODUCT, COSINE, L2 = "inner_product", "cosine", "l2"
METRICS = (INNER_PRODUCT, COSINE, L2)

__all__ = ["COSINE", "INNER_PRODUCT", "L2", "METRICS", "check_metric", "exact_scores"]


def check_metric(metric: str) -> str:
    """Return ``metric`` if it is one of :data:`METRICS`, else raise ValueError."""
    if metric not in METRICS:
        raise ValueError(
            f"unknown retrieval metric {metric!r}; expected one of {METRICS}"
        )
    return metric


def _unit(x: np.ndarray) -> np.ndarray:
    return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-30)


def exact_scores(queries: np.ndarray, corpus: np.ndarray, metric: str) -> np.ndarray:
    """``(n_q, n_c)`` exact scores, larger is nearer, in the dtype of the inputs.

    ``l2`` returns the negative squared distance, floored at zero distance so
    cancellation cannot produce a score above a row's own.
    """
    check_metric(metric)
    if metric == INNER_PRODUCT:
        return queries @ corpus.T
    if metric == COSINE:
        return _unit(queries) @ _unit(corpus).T
    d2 = (
        (queries**2).sum(axis=1)[:, None]
        - 2.0 * (queries @ corpus.T)
        + (corpus**2).sum(axis=1)[None, :]
    )
    return -np.maximum(d2, 0.0)
