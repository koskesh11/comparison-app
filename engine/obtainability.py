"""What is actually obtainable in the current league, from poe.ninja (cached daily) + vault overrides."""

import json
import re
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from vault import VAULT_DIR

CACHE_DIR = Path(__file__).resolve().parent / "cache"
CACHE_MAX_AGE_S = 24 * 3600
USER_AGENT = "pob-autobuilder/0.1"
TRADE_LEAGUES_URL = "https://www.pathofexile.com/api/trade/data/leagues"
NINJA_URL = "https://poe.ninja/poe1/api/economy/stash/current/item/overview?league={league}&type={type}"
PERMANENT_LEAGUES = {"Standard", "Hardcore", "Ruthless", "Hardcore Ruthless"}
OVERRIDE_BLOCK = re.compile(r"```obtainable\n(.*?)```", re.DOTALL)


def _fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def current_league() -> str:
    """First PC challenge league (softcore, non-Ruthless) listed by the official trade API."""
    for league in _fetch_json(TRADE_LEAGUES_URL)["result"]:
        name = league["id"]
        if league["realm"] == "pc" and name not in PERMANENT_LEAGUES and not re.match(r"(Hardcore|HC|Ruthless) ", name):
            return name
    raise RuntimeError("no current challenge league found")


def _ninja_lines(league: str, item_type: str) -> list[dict]:
    path = CACHE_DIR / league / f"{item_type}.json"
    if not path.exists() or time.time() - path.stat().st_mtime > CACHE_MAX_AGE_S:
        data = _fetch_json(NINJA_URL.format(league=urllib.request.quote(league), type=item_type))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
    return json.loads(path.read_text(encoding="utf-8"))["lines"]


def gem_key(name: str) -> str:
    """PoB says 'Brutality', poe.ninja says 'Brutality Support'."""
    return name.removesuffix(" Support").strip().lower()


def normal_version(name: str) -> str | None:
    """Return the non-Awakened gem name when one is present."""
    if not name.startswith("Awakened "):
        return None
    normal = name.removeprefix("Awakened ").strip()
    return normal or None


def _cache_date_for_path(path: Path) -> str | None:
    if not path.is_file():
        return None
    return time.strftime("%Y-%m-%d", time.localtime(path.stat().st_mtime))


def cache_date_for(league: str) -> str | None:
    """Return the local calendar date of the league's cached gem data."""
    return _cache_date_for_path(CACHE_DIR / league / "SkillGem.json")


@dataclass(frozen=True)
class GemVariant:
    level: int
    quality: int
    corrupted: bool


@dataclass
class Obtainability:
    league: str
    gems: dict[str, list[GemVariant]] = field(default_factory=dict)
    allow: set[str] = field(default_factory=set)
    deny: set[str] = field(default_factory=set)
    deny_sources: dict[str, dict] = field(default_factory=dict)
    cache_date: str | None = None

    @staticmethod
    def _gems_from_lines(lines: list[dict]) -> dict[str, list[GemVariant]]:
        gems: dict[str, list[GemVariant]] = {}
        for line in lines:
            variant = GemVariant(line.get("gemLevel") or 1, line.get("gemQuality") or 0,
                                 bool(line.get("corrupted")))
            gems.setdefault(gem_key(line["name"]), []).append(variant)
        return gems

    @classmethod
    def load(cls, league: str | None = None) -> "Obtainability":
        league = league or current_league()
        lines = _ninja_lines(league, "SkillGem")
        result = cls(league, gems=cls._gems_from_lines(lines), cache_date=cache_date_for(league))
        result._load_overrides()
        return result

    @classmethod
    def from_cache(cls, league: str, path: str | Path | None = None) -> "Obtainability":
        cache_path = Path(path) if path else CACHE_DIR / league / "SkillGem.json"
        lines = json.loads(cache_path.read_text(encoding="utf-8"))["lines"]
        result = cls(league, gems=cls._gems_from_lines(lines), cache_date=_cache_date_for_path(cache_path))
        result._load_overrides()
        return result

    def _load_overrides(self) -> None:
        for path in (VAULT_DIR / "Gaps").glob("*.md"):
            block = OVERRIDE_BLOCK.search(path.read_text(encoding="utf-8").replace("\r\n", "\n"))
            if block:
                spec = yaml.safe_load(block.group(1)) or {}
                self.allow |= {gem_key(n) for n in spec.get("allow") or []}
                source = {
                    "note": path.stem,
                    "since": str(spec.get("since") or ""),
                    "reason": str(spec.get("reason") or ""),
                }
                for name in spec.get("deny") or []:
                    key = gem_key(name)
                    self.deny.add(key)
                    self.deny_sources[key] = source.copy()

    def deny_reason(self, name: str) -> dict | None:
        source = self.deny_sources.get(gem_key(name))
        return source.copy() if source is not None else None

    def status(self, name: str) -> dict:
        key = gem_key(name)
        if key in self.deny:
            source = self.deny_sources.get(key, {"note": "", "since": "", "reason": ""})
            return {
                "state": "denied",
                "note": source.get("note", ""),
                "since": source.get("since", ""),
                "reason": source.get("reason", ""),
            }
        if key in self.allow:
            return {"state": "allowed"}
        if key in self.gems:
            return {"state": "listed"}
        return {"state": "unlisted", "league": self.league, "cacheDate": self.cache_date}

    def gem_obtainable(self, name: str) -> bool:
        key = gem_key(name)
        return key not in self.deny and (key in self.allow or key in self.gems)

    def best_gem_variants(self, name: str) -> list[GemVariant]:
        """Highest level (with its best quality) and highest quality (with its best level) seen this league."""
        variants = self.gems.get(gem_key(name), [])
        if not variants:
            return []
        by_level = max(variants, key=lambda v: (v.level, v.quality))
        by_quality = max(variants, key=lambda v: (v.quality, v.level))
        return list(dict.fromkeys([by_level, by_quality]))

    def best_uncorrupted(self, name: str) -> GemVariant | None:
        variants = (variant for variant in self.gems.get(gem_key(name), []) if not variant.corrupted)
        return max(variants, key=lambda variant: (variant.level, variant.quality), default=None)

    @staticmethod
    def normal_version(name: str) -> str | None:
        return normal_version(name)
