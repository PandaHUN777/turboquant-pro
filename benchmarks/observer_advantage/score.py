"""Registered verdicts (docs/PREREG_observer_advantage.md section 4).

    python -m observer_advantage.score --results /data/oa/results \
        --cb-results /data/cb/results --markdown out.md --json out.json

The cell statistic is consumer_basis.score's, imported: paired per-query
difference in recall@10, percentile bootstrap over evaluation queries, 10,000
resamples, seed 0, BETTER / WORSE / TIE / INCONCLUSIVE at +-0.01. Per-query hits
are averaged over a configuration's seeds first; a configuration missing a
seed is excluded and listed, never imputed.

Gates run first and a failed or unchecked gate withholds every verdict:
  G0  EXACT reproduces RESULTS_consumer_basis single-pass recall (P, O; msmarco,
      hotpotqa; k in KS) to within 0.002, and EXACT O equals EXACT Oey to within
      0.002 on every arm and k (the split is invisible to exact search). Needs
      --cb-results.
  G1  under EXACT, O vs P on msmarco and hotpotqa is BETTER in >= 5 of 6 cells.
  G2  every codec configuration: recall <= its EXACT recall + 0.005, and > 0.01.
  G3  the two sides of every scored comparison used the same scan path, and all
      seeds of one configuration did (the TQ kernel and numpy scans differ within
      the kernel's rounding bound, so a mixed pair is not a paired comparison).
``--ungated`` scores anyway for development and stamps every line "UNGATED".

Hypotheses, per family f in (TQ, RBQ, OPQ), single-pass endpoint:
  H1  O vs P on msmarco, hotpotqa; k in KS; b in BITS (12 cells): HOLDS if
      BETTER >= 9 and WORSE 0; REFUTED if BETTER <= 3 or WORSE >= 2; else MIXED.
  H2  O vs P on msmarco-sym (6 cells): HOLDS if TIE + BETTER >= 5 and WORSE 0;
      REFUTED if WORSE >= 2; else MIXED.
  H3  Spearman(mismatch, mean O - P) over the seven arms at H3_CELL: HOLDS if
      rho >= SPEARMAN_CRIT; REFUTED if rho <= 0; else MIXED.
  H4  O vs O_foreign on msmarco (6 cells): HOLDS if BETTER >= 5 and WORSE 0;
      REFUTED if WORSE in any (the wrong observer won a cell); else MIXED.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
from collections import Counter, defaultdict

import numpy as np
from consumer_basis.score import N_BOOT, paired, verdict

from .grid import (
    ARM_SYM,
    ARMS_ASYM,
    ARMS_H3,
    BITS,
    EXACT,
    FAMILIES,
    FOREIGN,
    FOREIGN_ARM,
    H3_CELL,
    KS,
    QUALITY_LEVELS,
    SEEDS,
    SPEARMAN_CRIT,
)

G0_TOL, G2_SLACK, G2_FLOOR = 0.002, 0.005, 0.01


# --------------------------------------------------------------------------- #
# Records -> seed-averaged configurations                                      #
# --------------------------------------------------------------------------- #


def load(results_dir):
    """{(arm, transform, family, k, b): config} with seed-averaged hits."""
    by = defaultdict(list)
    for p in glob.glob(os.path.join(results_dir, "*.json")):
        with open(p) as f:
            r = json.load(f)
        c = r["cell"]
        by[(c["arm"], c["transform"], c["family"], c["k"], c["b"])].append(r)
    configs, excluded = {}, []
    for key, recs in sorted(by.items(), key=lambda kv: str(kv[0])):
        want = {0} if key[2] == EXACT else set(SEEDS)
        have = {r["cell"]["seed"] for r in recs}
        if have != want:
            excluded.append(dict(config=key, seeds=sorted(have)))
            continue
        recs = sorted(recs, key=lambda r: r["cell"]["seed"])
        single = np.mean([r["hits_single"] for r in recs], axis=0)
        per_seed = [float(np.mean(r["hits_single"])) / 10 for r in recs]
        configs[key] = dict(
            single=single,
            rr5=np.mean([r["hits_rr5"] for r in recs], axis=0),
            recall=float(single.mean()) / 10,
            seed_spread=max(per_seed) - min(per_seed),
            scans={r["extra"].get("scan") for r in recs},
            stored=recs[0]["stored_bytes_per_vec"],
            mismatch=recs[0]["mismatch_index"],
            seconds=float(np.mean([r["build_and_search_s"] for r in recs])),
        )
    return configs, excluded


def compare(configs, a, b, endpoint="single"):
    """Cell verdict for config a minus config b, or None if either is missing."""
    if a not in configs or b not in configs:
        return None
    m, lo, hi = paired(configs[a][endpoint], configs[b][endpoint])
    return dict(a=a, b=b, mean=m, lo=lo, hi=hi, verdict=verdict(m, lo, hi))


def _key(arm, t, fam, k, b):
    return (arm, t, fam, k, None if fam == EXACT else b)


# --------------------------------------------------------------------------- #
# Gates                                                                        #
# --------------------------------------------------------------------------- #


def gate_g0(configs, cb_dir):
    if not cb_dir:
        return "NOT CHECKED", ["no --cb-results given"]
    notes, ok = [], True
    for arm in ARMS_ASYM:
        path = os.path.join(cb_dir, f"{arm}.json")
        if not os.path.exists(path):
            return "NOT CHECKED", [f"missing {path}"]
        with open(path) as f:
            ref = json.load(f)["results"]
        for t in ("P", "O"):
            for k in KS:
                mine = configs.get(_key(arm, t, EXACT, k, None))
                if mine is None:
                    return "NOT CHECKED", [f"no EXACT {arm} {t} k={k}"]
                theirs = float(np.mean(ref[f"{t}-{k}"]["hits_single"])) / 10
                d = mine["recall"] - theirs
                ok &= abs(d) <= G0_TOL
                notes.append(f"{arm} {t} k={k}: {mine['recall']:.4f} vs {theirs:.4f}")
    # The balanced split and the Eckart-Young split must be the same basis to
    # exact search: they differ by a diagonal moved between the two maps.
    pairs = [
        (key, (key[0], "Oey", *key[2:]))
        for key in configs
        if key[1] == "O" and key[2] == EXACT
    ]
    if not pairs or any(ey not in configs for _, ey in pairs):
        return "NOT CHECKED", notes + ["EXACT Oey missing for the split identity"]
    for o, ey in pairs:
        d = configs[o]["recall"] - configs[ey]["recall"]
        ok &= abs(d) <= G0_TOL
        notes.append(f"split identity {o[0]} k={o[3]}: O - Oey = {d:+.4f}")
    return ("PASS" if ok else "FAIL"), notes


def gate_g1(configs):
    cs = [
        compare(configs, _key(a, "O", EXACT, k, None), _key(a, "P", EXACT, k, None))
        for a in ARMS_ASYM
        for k in KS
    ]
    if any(c is None for c in cs):
        return "NOT CHECKED", ["EXACT O or P missing"]
    n = sum(c["verdict"] == "BETTER" for c in cs)
    return ("PASS" if n >= 5 else "FAIL"), [f"BETTER in {n} of {len(cs)}"]


def gate_g2(configs):
    bad = []
    for (arm, t, fam, k, b), c in configs.items():
        if fam == EXACT:
            continue
        ex = configs.get((arm, t, EXACT, k, None))
        if ex is None:
            return "NOT CHECKED", [f"no EXACT ceiling for {arm} {t} k={k}"]
        if not (G2_FLOOR < c["recall"] <= ex["recall"] + G2_SLACK):
            bad.append(
                f"{arm} {t} {fam} k={k} b={b}: {c['recall']:.4f} vs {ex['recall']:.4f}"
            )
    return ("PASS" if not bad else "FAIL"), bad


def gate_g3(configs, comparisons):
    bad = [
        f"{key}: {sorted(c['scans'])}"
        for key, c in configs.items()
        if len(c["scans"]) > 1
    ]
    for cmp in comparisons:
        if cmp and configs[cmp["a"]]["scans"] != configs[cmp["b"]]["scans"]:
            bad.append(f"{cmp['a']} vs {cmp['b']}: scan paths differ")
    return ("PASS" if not bad else "FAIL"), bad


# --------------------------------------------------------------------------- #
# Hypotheses                                                                   #
# --------------------------------------------------------------------------- #


def _counts(cs):
    return Counter(c["verdict"] for c in cs)


def rule_h1(cs):
    n = _counts(cs)
    if n["BETTER"] >= 9 and n["WORSE"] == 0:
        return "HOLDS"
    if n["BETTER"] <= 3 or n["WORSE"] >= 2:
        return "REFUTED"
    return "MIXED"


def rule_h2(cs):
    n = _counts(cs)
    if n["TIE"] + n["BETTER"] >= 5 and n["WORSE"] == 0:
        return "HOLDS"
    if n["WORSE"] >= 2:
        return "REFUTED"
    return "MIXED"


def rule_h4(cs):
    n = _counts(cs)
    if n["WORSE"] > 0:
        return "REFUTED"
    if n["BETTER"] >= 5:
        return "HOLDS"
    return "MIXED"


def spearman(x, y):
    def ranks(v):
        v = np.asarray(v, float)
        order = np.argsort(v, kind="stable")
        r = np.empty(len(v))
        r[order] = np.arange(len(v), dtype=float)
        for val in np.unique(v):  # average ranks over ties
            r[v == val] = r[v == val].mean()
        return r

    rx, ry = ranks(x), ranks(y)
    rx, ry = rx - rx.mean(), ry - ry.mean()
    return float((rx * ry).sum() / np.sqrt((rx**2).sum() * (ry**2).sum()))


def hypotheses(configs, fam, endpoint="single"):
    """{name: (verdict, cells)} for one family."""
    grid = [(k, b) for k in KS for b in BITS]
    out = {}
    h1 = [
        compare(configs, _key(a, "O", fam, k, b), _key(a, "P", fam, k, b), endpoint)
        for a in ARMS_ASYM
        for k, b in grid
    ]
    h2 = [
        compare(
            configs,
            _key(ARM_SYM, "O", fam, k, b),
            _key(ARM_SYM, "P", fam, k, b),
            endpoint,
        )
        for k, b in grid
    ]
    h4 = [
        compare(
            configs,
            _key(FOREIGN_ARM, "O", fam, k, b),
            _key(FOREIGN_ARM, FOREIGN, fam, k, b),
            endpoint,
        )
        for k, b in grid
    ]
    for name, cs, rule in (
        ("H1", h1, rule_h1),
        ("H2", h2, rule_h2),
        ("H4", h4, rule_h4),
    ):
        out[name] = ("UNSCORED", cs) if any(c is None for c in cs) else (rule(cs), cs)
    k, b = H3_CELL
    pts = []
    for arm in ARMS_H3:
        o, p = _key(arm, "O", fam, k, b), _key(arm, "P", fam, k, b)
        if o not in configs or p not in configs:
            pts = None
            break
        gain = (configs[o][endpoint].mean() - configs[p][endpoint].mean()) / 10
        pts.append((arm, configs[o]["mismatch"], gain))
    if pts is None:
        out["H3"] = ("UNSCORED", [])
    else:
        rho = spearman([m for _, m, _ in pts], [g for _, _, g in pts])
        v = "HOLDS" if rho >= SPEARMAN_CRIT else "REFUTED" if rho <= 0 else "MIXED"
        out["H3"] = (v, dict(rho=rho, points=pts))
    return out, h1 + h2 + h4


def platform_claim(by_family):
    holds = [f for f, h in by_family.items() if h["H1"][0] == h["H2"][0] == "HOLDS"]
    h4 = sum(h["H4"][0] == "HOLDS" for h in by_family.values())
    refuted = sum(h["H1"][0] == "REFUTED" for h in by_family.values())
    if refuted >= 2:
        return "WITHDRAWN (H1 refuted in two or more families)"
    if len(holds) == len(FAMILIES) and h4 >= 2:
        return "LICENSED: the observer layer is codec-independent (asymmetric text retrieval, one embedding family)"
    if holds:
        return f"HOLDS FOR {', '.join(holds)} ONLY"
    return "NOT LICENSED"


# --------------------------------------------------------------------------- #
# Observer Advantage table (descriptive)                                       #
# --------------------------------------------------------------------------- #


def lower_bound(hits_mean):
    x = np.asarray(hits_mean, float) / 10
    rng = np.random.default_rng(0)
    means = x[rng.integers(0, len(x), size=(N_BOOT, len(x)))].mean(axis=1)
    return float(np.percentile(means, 2.5))


def advantage_table(configs, endpoint="single"):
    lb = {
        key: lower_bound(c[endpoint])
        for key, c in configs.items()
        if key[2] in FAMILIES and key[1] in ("P", "O")
    }
    rows = []
    for fam in FAMILIES:
        for arm in ARMS_H3:
            for q in QUALITY_LEVELS:
                need = {}
                for t in ("P", "O"):
                    ok = [
                        c["stored"]
                        for (a, tt, f, _k, _b), c in configs.items()
                        if (a, tt, f) == (arm, t, fam) and lb[(a, tt, f, _k, _b)] >= q
                    ]
                    need[t] = min(ok) if ok else None
                ratio = (
                    need["P"] / need["O"] if need["P"] and need["O"] else "not measured"
                )
                rows.append(
                    dict(
                        family=fam,
                        arm=arm,
                        q=q,
                        bytes_P=need["P"],
                        bytes_O=need["O"],
                        ratio=ratio,
                    )
                )
    return rows


# --------------------------------------------------------------------------- #


def score(results_dir, cb_dir=None, ungated=False):
    configs, excluded = load(results_dir)
    by_family, compared = {}, []
    for fam in FAMILIES:
        by_family[fam], cs = hypotheses(configs, fam)
        compared += cs
    gates = dict(
        G0=gate_g0(configs, cb_dir),
        G1=gate_g1(configs),
        G2=gate_g2(configs),
        G3=gate_g3(configs, compared),
    )
    gated = all(v[0] == "PASS" for v in gates.values())
    return dict(
        gates=gates,
        gated=gated,
        stamp="" if gated else "UNGATED, not a verdict: ",
        verdicts=by_family if (gated or ungated) else None,
        rr5=(
            {f: hypotheses(configs, f, "rr5")[0] for f in FAMILIES}
            if (gated or ungated)
            else None
        ),
        claim=platform_claim(by_family) if (gated or ungated) else None,
        advantage_single=advantage_table(configs, "single"),
        advantage_rr5=advantage_table(configs, "rr5"),
        excluded=excluded,
        configs=configs,
    )


def markdown(res):
    s = res["stamp"]
    lines = ["## Gates", ""]
    for g, (v, notes) in res["gates"].items():
        lines.append(f"- **{g}**: {v}")
        lines += [f"  - {n}" for n in notes[:40]]
    if res["verdicts"] is None:
        lines += ["", "**Verdicts withheld: a gate failed or was not checked.**"]
    else:
        lines += ["", f"## {s}Registered verdicts (single-pass recall@10)", ""]
        for fam, hs in res["verdicts"].items():
            for h, (v, detail) in sorted(hs.items()):
                if h == "H3":
                    extra = f" rho={detail['rho']:+.3f}" if detail else ""
                    lines.append(f"- {s}**{fam} {h}**: {v}{extra}")
                    continue
                lines.append(f"- {s}**{fam} {h}**: {v} {dict(_counts(detail))}")
                for c in detail:
                    (arm, t, _f, k, b), (_, t2, *_r) = c["a"], c["b"]
                    lines.append(
                        f"  - {arm} {t}-{t2} k={k} b={b}: {c['mean']:+.4f} "
                        f"[{c['lo']:+.4f}, {c['hi']:+.4f}] {c['verdict']}"
                    )
        lines += ["", f"**{s}Platform claim: {res['claim']}**", ""]
        lines += ["## Reported, not scored: the same hypotheses after 5x rerank", ""]
        for fam, hs in res["rr5"].items():
            lines.append(
                f"- {fam}: " + ", ".join(f"{h} {v}" for h, (v, _) in sorted(hs.items()))
            )
    lines += [
        "",
        "## Observer Advantage table (descriptive; measured byte levels only)",
        "",
    ]
    lines += [
        "| family | arm | Q | endpoint | bytes P | bytes O | P/O |",
        "|---|---|---:|---|---:|---:|---|",
    ]
    for ep in ("single", "rr5"):
        for r in res[f"advantage_{ep}"]:
            ratio = r["ratio"] if isinstance(r["ratio"], str) else f"{r['ratio']:.2f}"
            lines.append(
                f"| {r['family']} | {r['arm']} | {r['q']:.2f} | {ep} | {r['bytes_P']} | {r['bytes_O']} | {ratio} |"
            )
    if res["excluded"]:
        lines += ["", "## Excluded (seeds short)", ""]
        lines += [f"- {e['config']}: seeds {e['seeds']}" for e in res["excluded"]]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--cb-results")
    ap.add_argument("--markdown")
    ap.add_argument("--json")
    ap.add_argument("--ungated", action="store_true")
    a = ap.parse_args()
    res = score(a.results, a.cb_results, a.ungated)
    md = markdown(res)
    if a.markdown:
        with open(a.markdown, "w", encoding="utf-8") as f:
            f.write(md)
    if a.json:
        slim = {k: v for k, v in res.items() if k != "configs"}
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(slim, f, default=str, indent=1)
    print(md)


if __name__ == "__main__":
    main()
