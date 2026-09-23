# TurboQuant Pro: Open-source TurboQuant for LLM KV cache compression
# Copyright (c) 2026 Andrew H. Bond. MIT License.
"""The documented examples run as written.

The README quickstart and the user guide both chained ``.with_quantizer`` onto
``PCAMatryoshka(...).fit(x)``, but ``fit`` fits in place and returns a
``PCAFitResult``, so the first example a reader copied raised AttributeError.
The README also unpacked ``ids, scores`` from a reranked search, which returns
ids only. Nothing ran the examples, so nothing noticed.

This runs every fenced ``python`` block of each file verbatim, in order, in one
namespace, as a reader pasting them would. The only things supplied are the
inputs the prose asks the reader to bring (``train_vectors``, ``corpus``,
``queries``, ``reconstructed``) and ``np.load`` for the files the user guide
loads. A block that ``.open(...)``s an index from disk is skipped by name,
because it documents reading an artifact this test does not have.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
DOCS = ("README.md", "docs/guides/user_guide.md")
FENCE = re.compile(r"```python\n(.*?)```", re.S)


def _embeddings(n=3000, d=768, rank=48, seed=0):
    """Unit rows with a concentrated spectrum, the shape real sentence
    embeddings have, so a certificate or recall claim in the prose is tested
    against data it is meant for rather than isotropic noise."""
    rng = np.random.default_rng(seed)
    basis = np.linalg.qr(rng.standard_normal((d, rank)))[0].T
    x = rng.standard_normal((n, rank)) @ basis + 0.02 * rng.standard_normal((n, d))
    x = x.astype(np.float32)
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def _blocks(doc: str) -> list[tuple[int, str]]:
    return list(enumerate(FENCE.findall((REPO / doc).read_text(encoding="utf-8"))))


@pytest.mark.parametrize("doc", DOCS)
def test_documented_examples_run(doc, monkeypatch, tmp_path):
    x = _embeddings()
    corpus, queries = x, x[:20]
    jitter = np.random.default_rng(1).standard_normal(corpus.shape).astype(np.float32)
    ns = {
        "train_vectors": x[:2000],
        "corpus": corpus,
        "queries": queries,
        "reconstructed": corpus + 1e-3 * jitter,  # a stand-in lossy reconstruction
    }
    monkeypatch.setattr(
        np, "load", lambda f, *a, **k: queries if "quer" in str(f) else corpus
    )
    monkeypatch.chdir(tmp_path)
    ran = 0
    for i, src in _blocks(doc):
        if ".open(" in src:
            continue  # reads an index from disk; documents an artifact, not a recipe
        exec(compile(src, f"{doc} [python block {i}]", "exec"), ns)
        ran += 1
    assert ran >= 2, f"{doc}: expected its quickstart blocks to run, ran {ran}"
