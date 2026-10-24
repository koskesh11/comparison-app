"""Sourced interaction notes and vault-note metadata."""

import logging
from pathlib import Path

import yaml

from vault import FRONTMATTER, GAP_BLOCK, VAULT_DIR

INTERACTIONS = (
    {"when": {"category": "item"},
     "note": "Tested as the whole item replacing yours (mods, implicits, enchant and anoint together; Path of Building does not check socket links).",
     "refs": ["Attribute requirements must be met"]},
    {"when": {"flag": "same-name"},
     "note": "Same item, different version: the differing mods are listed on the row.",
     "refs": ["Mods PoB can't value"]},
    {"when": {"flag": "handedness"},
     "note": "A two-handed weapon clears your Weapon 2 in the calculation; a one-handed pair is tested together.",
     "refs": []},
    {"when": {"category": "flask"},
     "note": "Counts only if the matching flask slot is active in your build.",
     "refs": []},
    {"when": {"category": "jewel", "flag": "paired"},
     "note": "Needs both pieces: tested as one row.", "refs": []},
    {"when": {"category": "jewel"},
     "note": "A jewel is tested together with the path to its socket; radius jewels change nearby nodes.",
     "refs": []},
    {"when": {"category": "group-add"},
     "note": "A new skill: its cost and reservation count against your pools.",
     "refs": ["Reservation must fit the pool", "Total skill cost must be sustainable"]},
    {"when": {"flag": "trigger"},
     "note": "The trigger attack's level trades mana margin against quality of life (vault rule).",
     "refs": ["Trigger attack stays at cheapest level"]},
    {"when": {"category": "tree-add"},
     "note": "Travel nodes cost points; attribute nodes can matter for requirements.",
     "refs": ["Attribute requirements must be met"]},
    {"when": {"nodeType": "Keystone"},
     "note": "A keystone is valued on your current gear, not the guide's.", "refs": []},
    {"when": {"category": "tree-remove"},
     "note": "Removing a node also removes everything that depends on it (listed on the row).",
     "refs": ["Mastery needs a notable in its cluster", "Attribute requirements must be met"]},
)

MODEL_CATEGORIES = {"group-add", "support-add", "support-replace", "gem-level"}
GAP_CATEGORIES = {"item", "flask", "jewel"}  # slotless patterns (M8) also fit flasks and jewels
_warned = set()


def vault_note_status(vault_dir: Path = VAULT_DIR) -> dict[str, str]:
    result = {}
    for folder in ("Rules", "Models", "Gaps", "Scenarios"):
        for path in sorted((vault_dir / folder).glob("*.md")):
            text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
            match = FRONTMATTER.match(text)
            if match:
                result[path.stem] = str((yaml.safe_load(match.group(1)) or {}).get("status", "draft"))
    return result


def load_named_gap_patterns(vault_dir: Path = VAULT_DIR) -> list[dict]:
    result = []
    for path in sorted((vault_dir / "Gaps").glob("*.md")):
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        block = GAP_BLOCK.search(text)
        for pattern in ((yaml.safe_load(block.group(1)) or {}).get("patterns") or []) if block else []:
            result.append({**pattern, "note": path.stem})
    return result


def _matches(entry: dict, row: dict) -> bool:
    when = entry["when"]
    if "category" in when and row.get("category") != when["category"]:
        return False
    if when == {"category": "jewel"} and "paired" in (row.get("flags") or []):
        return False
    if "flag" in when and when["flag"] not in (row.get("flags") or []):
        return False
    if "nodeType" in when and (row.get("info") or {}).get("nodeType") != when["nodeType"]:
        return False
    return True


def _model_notes(models: list[dict]) -> tuple[list[str], list[str]]:
    texts, refs = [], []
    for model in models:
        name = model.get("model")
        texts.append(f"PoB number; model not applied: {name} would count {model.get('multiplier')} hits "
                     f"(PoB counts {model.get('pobCount')}).")
        refs.append(name)
    return texts, refs


def _gap_notes(guide: dict | None, player: dict | None, patterns: list[dict]) -> tuple[list[str], list[str]]:
    if not guide:
        return [], []
    player_mods = {str(value).casefold() for value in (player or {}).get("mods") or []}
    texts, refs = [], []
    for line in guide.get("mods") or []:
        if str(line).casefold() in player_mods:
            continue
        for pattern in patterns:
            if pattern.get("slot", "") not in str(guide.get("slot") or ""):
                continue
            if str(pattern.get("match") or "").casefold() in str(line).casefold():
                texts.append(str(pattern.get("why") or ""))
                refs.append(pattern["note"])
    return texts, refs


def interaction_for(row: dict, ctx_models: list[dict], guide_item=None, player_item=None,
                    gap_patterns=None, statuses=None) -> dict | None:
    texts, refs = [], list(row.get("vaultRefs") or [])
    carries = list(refs)
    for entry in INTERACTIONS:
        if _matches(entry, row):
            texts.append(entry["note"])
            refs += entry["refs"]
    model_text, model_refs = _model_notes(ctx_models or [])
    texts += model_text
    refs += model_refs
    if row.get("category") in MODEL_CATEGORIES:
        carries += model_refs  # a gem change can matter for the model even when PoB shows no effect
    if row.get("category") in GAP_CATEGORIES:
        gap_text, gap_refs = _gap_notes(guide_item, player_item, gap_patterns or [])
        texts += gap_text
        refs += gap_refs
        carries += gap_refs
    statuses = vault_note_status() if statuses is None else statuses
    known = []
    for name in sorted(set(filter(None, refs)), key=str.casefold):
        if name in statuses:
            known.append(name)
        elif name not in _warned:
            logging.warning("unknown guide interaction vault note: %s", name)
            _warned.add(name)
    note = " ".join(filter(None, texts))
    # carries: refs that make THIS row matter although PoB shows no effect (not the generic notes of its category)
    carried = sorted({name for name in carries if name in known}, key=str.casefold)
    return {"note": note, "vaultRefs": known, "carries": carried} if note or known else None
