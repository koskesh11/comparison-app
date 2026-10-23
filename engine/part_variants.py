"""Pure helpers for displaying suggestion values for every PoB skill part."""

from display import fmt_pct
from scoring import change_pct, skill_changes, skill_out


def saved_part_name(base_ctx: dict, skill: str) -> str | None:
    row = next((item for item in base_ctx.get("skills", []) if item["name"] == skill), None)
    return row.get("part") if row else None


def main_dps(ctx: dict, dps_key: str) -> float | None:
    main = next((skill for skill in ctx.get("skills", []) if skill.get("isMain")), None)
    return skill_out(main or {}).get(dps_key)


def parts_dims(ctx: dict, base_ctx: dict, dims: dict, dps_key: str) -> list[dict]:
    variants, base_variants = ctx.get("byPart") or [], base_ctx.get("byPart") or []
    if not variants or not base_variants:
        return []
    rows = []
    for skill in dict.fromkeys(item["skill"] for item in variants):
        rows.append({"skill": skill, "partName": saved_part_name(base_ctx, skill), "saved": True,
                     "dps": dims["dps"], "skills": dims["skills"]})
        alternatives = sorted((item for item in variants if item["skill"] == skill),
                              key=lambda item: item["partIndex"])
        for item in alternatives:
            base = next((candidate for candidate in base_variants
                         if (candidate["skill"], candidate["partIndex"]) ==
                         (skill, item["partIndex"])), None)
            alt_dps = (None if base is None else
                       change_pct(main_dps(item["ctx"], dps_key) or 0,
                                  main_dps(base["ctx"], dps_key) or 0))
            skills = [] if base is None else skill_changes(item["ctx"], base["ctx"])
            rows.append({"skill": skill, "partName": item.get("partName"), "saved": False,
                         "dps": alt_dps, "skills": skills})
    return rows


def parts_text(dims: dict) -> str:
    parts = dims.get("parts") or []
    if not parts:
        return ""
    multiple_skills = len({row["skill"] for row in parts}) > 1
    labels = []
    for row in parts:
        name = row.get("partName") or row["skill"]
        saved = " (saved)" if row["saved"] else ""
        prefix = f"{row['skill']}: " if multiple_skills else ""
        labels.append(f"{prefix}{name}{saved} {fmt_pct(row['dps'])}")
    return "parts: " + " | ".join(labels)
