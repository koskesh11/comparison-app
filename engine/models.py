"""Vault Models: corrections for mechanics PoB doesn't calculate, applied to evaluated contexts."""

import math
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from vault import FRONTMATTER, VAULT_DIR

MODEL_BLOCK = re.compile(r"```model\n(.*?)```", re.DOTALL)
UNITS_PER_METRE = 10


@dataclass(frozen=True)
class Model:
    name: str
    status: str
    spec: dict


def load_models(vault_dir: Path = VAULT_DIR) -> list[Model]:
    models = []
    for path in sorted((vault_dir / "Models").glob("*.md")):
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        front, block = FRONTMATTER.match(text), MODEL_BLOCK.search(text)
        if front and block:
            meta = yaml.safe_load(front.group(1)) or {}
            spec = yaml.safe_load(block.group(1)) or {}
            if spec.get("kind"):  # only models with an implemented kind are executable
                models.append(Model(path.stem, meta.get("status", "draft"), spec))
    return models


LINE_OFFSET_SAMPLES = 100  # where the "rough line" lands relative to the target, averaged


def line_hits_at_offset(projectiles: int, spacing: float, reach: float, offset: float) -> int:
    """Impacts within reach of the target for a line centred at `offset` (in spacings) from it."""
    centre = (projectiles - 1) / 2
    return sum(abs((i - centre + offset) * spacing) <= reach for i in range(projectiles))


def line_overlap_hits(out: dict, params: dict, nova: bool) -> dict:
    """Expected hits on one target: projectiles land in a rough line whose position relative to the
    target varies, so average over a uniform offset of up to half a spacing either way."""
    projectiles = int(out.get("ProjectileCount") or 1)
    if nova:
        return {"expected": projectiles, "min": projectiles, "max": projectiles}
    radius_m = (out.get("AreaOfEffectRadius") or 0) / UNITS_PER_METRE
    reach = radius_m + params["enemy_radius_m"]
    samples = [line_hits_at_offset(projectiles, params["spacing_m"], reach, -0.5 + (k + 0.5) / LINE_OFFSET_SAMPLES)
               for k in range(LINE_OFFSET_SAMPLES)]
    return {"expected": max(1.0, sum(samples) / len(samples)), "min": max(1, min(samples)), "max": max(samples)}


KINDS = {"line_overlap": line_overlap_hits}


def stat_keys(models: list[Model]) -> set[str]:
    return {"ProjectileCount", "AreaOfEffectRadius"} if models else set()


def apply_models(models: list[Model], ctx: dict, equipped: set[str]) -> dict:
    """Return a copy of ctx with model multipliers applied to matching skills."""
    skills = []
    modelled_counts = {}
    for skill in ctx["skills"]:
        out = dict(skill["out"])
        applied = []
        for model in models:
            if model.spec.get("applies_to", {}).get("skill") != skill["name"]:
                continue
            params = model.spec.get("params") or {}
            nova = bool(equipped & set(params.get("nova_items") or []))
            result = KINDS[model.spec["kind"]](out, params, nova)
            # PoE rounds down: whole hits only (vault rule "Models round down")
            hits = max(1, math.floor(result["expected"]))
            # FullDPS already includes PoB's per-gem count (users set it to model overlaps by hand):
            # the model replaces that count instead of stacking on top of it.
            pob_count = skill.get("count") or 1
            for key in model.spec.get("multiplies") or []:
                if out.get(key) is not None:
                    out[key] = out[key] * (hits / pob_count if key == "FullDPS" else hits)
                    if key == "FullDPS":
                        modelled_counts[skill["name"]] = hits
            applied.append({"model": model.name, "multiplier": hits, "expected": result["expected"],
                            "range": [result["min"], result["max"]], "pobCount": pob_count})
        skills.append({**skill, "out": out, "models": applied})
    result = {**ctx, "skills": skills}
    if "skillDPS" in ctx:
        rows = [{**row, "count": modelled_counts[row["name"]], "pobCount": row.get("count") or 1}
                if row["name"] in modelled_counts else {**row} for row in ctx["skillDPS"]]
        result = {**result, "skillDPS": rows}
    return result
