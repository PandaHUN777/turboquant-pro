"""The README benchmark snapshot, from the public campaign's scorer report.

For each public arm, the most compressed registered tq-pro configuration that
has a matched RaBitQ and OPQ baseline under the preregistration's byte-window
rule (PQ beside them when its window has a configuration), beside those matched baselines: stored
bytes, compression against fp32, recall@10 single-pass and after the 5x
rerank, build seconds. Every number is read from ``registered.md`` of the
scoring directory; the matched baseline per family is the one the scorer
chose (highest rr5 inside 0.80 to 1.05 of the tq-pro bytes), so the table is
the comparison the preregistration scored, not a hand-picked one.

    python -m rabitq_public.snapshot [--stamp 2026-09-18T1115] [--markdown]
"""

import argparse
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ARMS = [
    ("glove-100-angular", "GloVe-100", 100),
    ("deep-image-96-angular", "deep-image-96", 96),
    ("nytimes-256-angular", "NYTimes-256", 256),
    ("dbpedia-ada002-1m", "DBpedia ada-002 (1M)", 1536),
    ("dbpedia-3large-1536-1m", "DBpedia text-embedding-3-large (1M)", 1536),
    ("wiki1024-10m", "Wikipedia-1024 (10M)", 1024),
]
FAMILIES = ["RABITQ", "OPQ", "PQ"]


def _num(cell: str) -> float:
    m = re.match(r"\s*([0-9.]+)", cell)
    return float(m.group(1)) if m else float("nan")


def parse(path):
    """Per-config rows and the rr5 matched pairs keyed by (arm, tq config)."""
    configs, pairs = {}, {}
    section = None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("## "):
            section = line
            continue
        if not line.startswith("| ") or "---" in line:
            continue
        c = [x.strip() for x in line.strip("|").split("|")]
        if section.startswith("## Every scored") and len(c) == 9 and c[0] != "dataset":
            configs[(c[0], c[1])] = dict(
                family=c[2],
                bytes=_num(c[3]),
                single=_num(c[4]),
                rr5=_num(c[6]),
                build=_num(c[7]),
                search=_num(c[8]),
            )
        elif section.startswith("## Matched-byte") and len(c) == 11 and c[6] == "rr5":
            if "anchor" in c[1] or c[10] == "NO-CONFIG":
                continue
            pairs.setdefault((c[0], c[1]), {})[c[3]] = dict(base=c[4], verdict=c[10])
    return configs, pairs


def select(configs, pairs):
    """Per arm: the most compressed tq configuration matched in RaBitQ and OPQ."""
    out = []
    for arm, label, dim in ARMS:
        cands = []
        for (a, cfg), fams in pairs.items():
            if a != arm or "-tq-" not in cfg:
                continue
            if all(f in fams for f in ("RABITQ", "OPQ")) and (arm, cfg) in configs:
                cands.append((configs[(arm, cfg)]["bytes"], cfg))
        if not cands:
            out.append((arm, label, dim, None, {}))
            continue
        _, cfg = min(cands)
        out.append((arm, label, dim, cfg, pairs[(arm, cfg)]))
    return out


def markdown(configs, rows):
    L = []
    L.append(
        "| arm (dim) | method | configuration | B/vec | ratio vs fp32 | recall@10 single | recall@10 +rerank ×5 | build s | verdict vs tq-pro |"
    )
    L.append("|---|---|---|---:|---:|---:|---:|---:|---|")
    for arm, label, dim, cfg, fams in rows:
        if cfg is None:
            L.append(
                f"| {label} ({dim}) | no configuration matched in every family | | | | | | | |"
            )
            continue
        tq = configs[(arm, cfg)]
        L.append(
            f"| **{label}** ({dim}-d) | **tq-pro** | `{cfg.replace(arm + '-', '')}` | {tq['bytes']:g} | "
            f"{dim * 4 / tq['bytes']:.0f}× | **{tq['single']:.3f}** | **{tq['rr5']:.4f}** | {tq['build']:.0f} | |"
        )
        for fam, name in (("RABITQ", "RaBitQ"), ("OPQ", "OPQ"), ("PQ", "PQ")):
            p = fams.get(fam)
            if p is None:
                L.append(
                    f"| | {name} | no configuration inside 0.80–1.05 × {tq['bytes']:g} B | | | | | | |"
                )
                continue
            b = configs[(arm, p["base"])]
            v = {
                "BEATS": "tq-pro wins",
                "TIES": "tie",
                "LOSES": "tq-pro loses",
                "INCONCLUSIVE": "inconclusive",
            }[p["verdict"]]
            L.append(
                f"| | {name} | `{p['base'].replace(arm + '-', '')}` | {b['bytes']:g} | {dim * 4 / b['bytes']:.0f}× | "
                f"{b['single']:.3f} | {b['rr5']:.4f} | {b['build']:.0f} | {v} |"
            )
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stamp", default="2026-09-18T1115")
    ap.add_argument("--markdown", action="store_true", help="print the README table")
    a = ap.parse_args()
    configs, pairs = parse(os.path.join(HERE, "scoring", a.stamp, "registered.md"))
    rows = select(configs, pairs)
    print(markdown(configs, rows))


if __name__ == "__main__":
    main()
