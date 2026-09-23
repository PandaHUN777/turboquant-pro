# TurboQuant Pro: Open-source TurboQuant for LLM KV cache compression
# Copyright (c) 2026 Andrew H. Bond. MIT License.
"""The utilization guard reads usage from the metrics API.

`kubectl top pods` failed the whole namespace when one pod had no metrics yet
(a pod that just completed), and the guard then sampled nothing. The metrics
API returns the pods it has; these tests pin the parsing of its units,
including memory in milli-bytes, which the old parser crashed on.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "benchmarks"))

from nrp import utilization_guard as g  # noqa: E402


def test_units():
    assert g.parse_cpu("1350m") == 1.35
    assert g.parse_cpu("250000000n") == 0.25
    assert g.parse_cpu("0") == 0.0
    assert g.parse_mem("3329188Ki") == 3329188 * 1024
    assert g.parse_mem("10933589333m") == 10933589333e-3
    assert g.parse_mem("2Gi") == 2 * 2**30


def test_metrics_list_sums_containers_and_skips_nothing_it_has():
    doc = {
        "items": [
            {
                "metadata": {"name": "a"},
                "containers": [
                    {"usage": {"cpu": "1350m", "memory": "3329188Ki"}},
                    {"usage": {"cpu": "50m", "memory": "1Mi"}},
                ],
            },
            {
                "metadata": {"name": "leaf"},
                "containers": [{"usage": {"cpu": "0", "memory": "10933589333m"}}],
            },
        ]
    }
    got = g.parse_metrics(doc)
    assert set(got) == {"a", "leaf"}
    assert abs(got["a"][0] - 1.4) < 1e-12
    assert got["a"][1] == 3329188 * 1024 + 2**20
    assert got["leaf"] == (0.0, 10933589333e-3)
    assert g.parse_metrics({}) == {}
