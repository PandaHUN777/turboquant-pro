# TurboQuant Pro: Open-source TurboQuant for LLM KV cache compression
# Copyright (c) 2026 Andrew H. Bond
# MIT License

"""Observer contracts: who reads the data, how, and with what guarantees.

A consumer-relative distortion is not interpretable on its own: two defensible
read operators for one attention head differ by about 0.3 in subspace overlap,
which is why a certificate records the provider and the hash of the operator it
was computed against (``docs/CERTIFICATE_SPEC.md``, ``reference``). The
contract makes that concept a first-class object, independent of any one
certificate. It declares the source, the consumers that read the data with
their weights, the population and its strata, the requirements, the budget and
the fallback, and it is content-addressed: the sha256 of its canonical form is
the name a plan record, a certificate or a monitor report uses to say which
observer it was computed for.

The file form (``.tqo``) is YAML when PyYAML is installed (the ``yaml`` extra)
and JSON always, since JSON is YAML. The consumers are the registered consumer
metrics of :mod:`turboquant_pro.consumers`; a ``read_operator`` consumer names
a provider registered in :mod:`turboquant_pro.read_operators`. Nothing here is
a new metric: the contract binds names that already carry their own evidence.

Phase 1 (issue #173). The planner reads one consumer, so
:meth:`ObserverContract.to_workload_spec` hands it the primary one, the
largest weight, and the plan record says so. Weighted mixtures, refinement
layers and expiry are the later issues of the family (#174 to #183).
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import Any

PROFILE = "tqp-observer/1"
SCHEMA_ID = "turboquant-pro/observer-contract"
FALLBACK_ACTIONS = ("exact_rerank", "abstain", "refuse", "none")
TARGETS = ("embedding", "kv_key", "kv_value", "weight")

__all__ = [
    "PROFILE",
    "SCHEMA_ID",
    "FALLBACK_ACTIONS",
    "ConsumerClause",
    "ObserverContract",
    "ContractError",
    "load_contract",
    "save_contract",
    "parse_contract",
]


class ContractError(ValueError):
    """A contract that cannot be read, or does not validate."""


def _canonical(obj: Any) -> str:
    """Identity conventions shared with the area map: sorted keys, tight
    separators, no NaN, ASCII."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    )


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ConsumerClause:
    """One reader of the data: a registered consumer metric, its configuration,
    and its share of the observer."""

    metric: str
    config: dict = field(default_factory=dict)
    weight: float = 1.0
    name: str | None = None

    def as_dict(self) -> dict:
        d: dict = {
            "metric": self.metric,
            "config": dict(self.config),
            "weight": self.weight,
        }
        if self.name is not None:
            d["name"] = self.name
        return d

    @classmethod
    def from_dict(cls, d: dict) -> ConsumerClause:
        if not isinstance(d, dict) or "metric" not in d:
            raise ContractError(f"a consumer needs a 'metric'; got {d!r}")
        return cls(
            metric=str(d["metric"]),
            config=dict(d.get("config") or {}),
            weight=float(d.get("weight", 1.0)),
            name=d.get("name"),
        )

    @property
    def label(self) -> str:
        return self.name or self.metric


@dataclass(frozen=True)
class ObserverContract:
    """The observer as an artifact.

    ``observer`` names it for people; :meth:`digest` names it for machines.
    ``source`` and ``population`` are provenance (what was embedded, which
    strata, which calibration sample) and take any keys; ``requirements``,
    ``budget`` and ``fallback`` have the keys the planner reads, listed in the
    schema. Every field participates in the digest.
    """

    observer: str
    consumers: tuple[ConsumerClause, ...]
    target: str = "embedding"
    source: dict = field(default_factory=dict)
    population: dict = field(default_factory=dict)
    requirements: dict = field(default_factory=dict)
    budget: dict = field(default_factory=dict)
    fallback: dict = field(default_factory=dict)
    profile: str = PROFILE

    # ---- identity -------------------------------------------------------

    def as_dict(self) -> dict:
        return {
            "schema": SCHEMA_ID,
            "profile": self.profile,
            "observer": self.observer,
            "target": self.target,
            "source": dict(self.source),
            "consumers": [c.as_dict() for c in self.consumers],
            "population": dict(self.population),
            "requirements": dict(self.requirements),
            "budget": dict(self.budget),
            "fallback": dict(self.fallback),
        }

    @classmethod
    def from_dict(cls, d: dict) -> ObserverContract:
        if not isinstance(d, dict):
            raise ContractError(f"a contract is a mapping; got {type(d).__name__}")
        schema = d.get("schema", SCHEMA_ID)
        if schema != SCHEMA_ID:
            raise ContractError(f"not an observer contract: schema {schema!r}")
        if "observer" not in d or not str(d["observer"]).strip():
            raise ContractError("a contract needs an 'observer' name")
        raw = d.get("consumers")
        if not isinstance(raw, list) or not raw:
            raise ContractError("a contract needs a non-empty 'consumers' list")
        return cls(
            observer=str(d["observer"]),
            consumers=tuple(ConsumerClause.from_dict(c) for c in raw),
            target=str(d.get("target", "embedding")),
            source=dict(d.get("source") or {}),
            population=dict(d.get("population") or {}),
            requirements=dict(d.get("requirements") or {}),
            budget=dict(d.get("budget") or {}),
            fallback=dict(d.get("fallback") or {}),
            profile=str(d.get("profile", PROFILE)),
        )

    def canonical(self) -> str:
        return _canonical(self.as_dict())

    def digest(self) -> str:
        """sha256 of the canonical form. Key order, whitespace and the file
        format do not change it; any declared value does."""
        return _sha256(self.canonical())

    def reference(self) -> dict:
        """The section a plan record or certificate carries to name this
        contract: enough to find it and to refuse a mismatch."""
        p = self.primary()
        return {
            "profile": self.profile,
            "observer": self.observer,
            "sha256": self.digest(),
            "target": self.target,
            "consumers": [c.label for c in self.consumers],
            "primary_consumer": {
                "metric": p.metric,
                "config": dict(p.config),
                "weight": p.weight,
            },
        }

    # ---- reading --------------------------------------------------------

    def primary(self) -> ConsumerClause:
        """The consumer with the largest weight; the first on a tie."""
        best = self.consumers[0]
        for c in self.consumers[1:]:
            if c.weight > best.weight:
                best = c
        return best

    def normalized_weights(self) -> dict:
        total = sum(c.weight for c in self.consumers)
        return {
            c.label: (c.weight / total if total > 0 else 0.0) for c in self.consumers
        }

    def floor(self):
        """The requirements' floor as the planner's ``QualityFloor``, or ``None``."""
        from turboquant_pro.planner import QualityFloor

        f = self.requirements.get("floor")
        if not f:
            return None
        return QualityFloor(
            minimum=float(f["minimum"]), confidence=float(f.get("confidence", 0.95))
        )

    def to_workload_spec(self, **overrides: Any):
        """A :class:`turboquant_pro.planner.WorkloadSpec` for the primary
        consumer, with the contract's budget and floor. ``overrides`` are
        passed through (``seed``, ``n_boot``, ``candidates``, ``objective``)."""
        from turboquant_pro.planner import Budget, WorkloadSpec

        p = self.primary()
        b = self.budget
        budget = Budget(
            max_bytes_per_vector=b.get("max_bytes_per_vector"),
            max_bits=b.get("max_bits"),
            max_total_bytes=b.get("max_total_bytes"),
        )
        return WorkloadSpec(
            target=self.target,
            consumer=p.metric,
            consumer_config=dict(p.config),
            budget=budget,
            floor=self.floor(),
            **overrides,
        )

    # ---- validation -----------------------------------------------------

    def validate(self, *, registries: bool = True) -> list[str]:
        """Problems with this contract, an empty list when there are none.

        Structure first (the shipped schema when ``jsonschema`` is installed,
        the same rules by hand otherwise), then the registries: every
        consumer metric must be registered for the contract's target, and a
        ``read_operator`` consumer must name a registered provider. A
        contract that names an unknown consumer is refused rather than
        planned around; the planner abstains on unregistered consumers for
        the same reason.
        """
        problems: list[str] = []
        d = self.as_dict()
        problems += _schema_problems(d)
        if problems:
            return problems
        if registries:
            problems += self._registry_problems()
        return problems

    def _registry_problems(self) -> list[str]:
        from turboquant_pro import consumers as consumers_mod
        from turboquant_pro import read_operators as ro_mod

        out: list[str] = []
        for c in self.consumers:
            try:
                spec = consumers_mod.get_consumer(c.metric)
            except KeyError as e:
                out.append(f"consumer {c.label!r}: {e}")
                continue
            if self.target not in spec.targets:
                out.append(
                    f"consumer {c.label!r}: metric {c.metric!r} is registered for "
                    f"{sorted(spec.targets)}, not for target {self.target!r}"
                )
            if c.metric == "read_operator":
                provider = c.config.get("provider")
                if not provider:
                    out.append(
                        f"consumer {c.label!r}: read_operator needs config.provider"
                    )
                else:
                    try:
                        ro_mod.get_read_operator(str(provider))
                    except KeyError as e:
                        out.append(f"consumer {c.label!r}: {e}")
        return out

    def ensure_valid(self, *, registries: bool = True) -> ObserverContract:
        problems = self.validate(registries=registries)
        if problems:
            raise ContractError("; ".join(problems))
        return self


# ---- structure -----------------------------------------------------------


def _schema_problems(d: dict) -> list[str]:
    """Structural problems, via the shipped JSON Schema when ``jsonschema`` is
    available and by the same rules in plain Python otherwise, so the check
    never silently weakens on a host without the extra."""
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return _manual_schema_problems(d)
    from turboquant_pro.schemas import load_schema

    schema = load_schema("observer_contract.schema.json")
    v = jsonschema.Draft202012Validator(schema)
    out = []
    for err in sorted(v.iter_errors(d), key=lambda e: list(e.path)):
        where = "/".join(str(p) for p in err.path) or "<root>"
        out.append(f"{where}: {err.message}")
    return out


def _manual_schema_problems(d: dict) -> list[str]:
    out: list[str] = []
    if d.get("profile") != PROFILE:
        out.append(f"profile: expected {PROFILE!r}, got {d.get('profile')!r}")
    if d.get("target") not in TARGETS:
        out.append(f"target: {d.get('target')!r} is not one of {list(TARGETS)}")
    for i, c in enumerate(d.get("consumers") or []):
        w = c.get("weight")
        if not isinstance(w, (int, float)) or w <= 0:
            out.append(f"consumers/{i}/weight: must be a number > 0")
        if not isinstance(c.get("config"), dict):
            out.append(f"consumers/{i}/config: must be a mapping")
    f = (d.get("requirements") or {}).get("floor")
    if f is not None:
        m = f.get("minimum") if isinstance(f, dict) else None
        if not isinstance(m, (int, float)) or not 0.0 <= m <= 1.0:
            out.append("requirements/floor/minimum: must be a number in [0, 1]")
        conf = f.get("confidence", 0.95) if isinstance(f, dict) else None
        if not isinstance(conf, (int, float)) or not 0.0 < conf < 1.0:
            out.append("requirements/floor/confidence: must be a number in (0, 1)")
    w = (d.get("requirements") or {}).get("worst_stratum_minimum")
    if w is not None and (not isinstance(w, (int, float)) or not 0.0 <= w <= 1.0):
        out.append("requirements/worst_stratum_minimum: must be a number in [0, 1]")
    for k in ("max_bytes_per_vector", "max_bits", "max_total_bytes"):
        v = (d.get("budget") or {}).get(k)
        if v is not None and (not isinstance(v, (int, float)) or v <= 0):
            out.append(f"budget/{k}: must be a number > 0")
    a = (d.get("fallback") or {}).get("action")
    if a is not None and a not in FALLBACK_ACTIONS:
        out.append(f"fallback/action: {a!r} is not one of {list(FALLBACK_ACTIONS)}")
    return out


# ---- files ---------------------------------------------------------------


def parse_contract(text: str) -> ObserverContract:
    """A contract from YAML or JSON text. JSON parses without PyYAML; YAML
    that is not JSON needs the ``yaml`` extra and says so."""
    try:
        data = json.loads(text)
    except ValueError:
        try:
            import yaml  # type: ignore
        except ImportError:
            raise ContractError(
                "the contract is not JSON and PyYAML is not installed; "
                "pip install 'turboquant-pro[yaml]' or write the contract as JSON"
            ) from None
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as e:  # pragma: no cover - message passthrough
            raise ContractError(f"contract is not valid YAML: {e}") from None
    return ObserverContract.from_dict(data)


def load_contract(path: str) -> ObserverContract:
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        raise ContractError(f"cannot read contract {path!r}: {e}") from None
    return parse_contract(text)


def save_contract(contract: ObserverContract, path: str, fmt: str | None = None) -> str:
    """Write the contract. ``fmt`` is ``"json"`` or ``"yaml"``; by default
    ``.json`` files are JSON and everything else is YAML when PyYAML is
    installed, JSON otherwise. Returns the format written."""
    if fmt is None:
        fmt = "json" if os.path.splitext(path)[1].lower() == ".json" else "yaml"
    d = contract.as_dict()
    if fmt == "yaml":
        try:
            import yaml  # type: ignore
        except ImportError:
            fmt = "json"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        if fmt == "yaml":
            yaml.safe_dump(d, f, sort_keys=False, allow_unicode=False)
        else:
            json.dump(d, f, indent=2, sort_keys=False, allow_nan=False)
            f.write("\n")
    return fmt
