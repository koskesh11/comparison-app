"""The scenario picker (decision 010): a scenario sets only PoB's "Is the enemy a Boss?" box, for both builds.

The box values are PoB's own (ConfigOptions.lua:2086); pob/lua/analysis/scenario.lua refuses any value PoB does not
list. Mapping keeps the box at Pinnacle (decision 022). The words shown for each scenario live in app/present.
"""

from collections.abc import Mapping
from enum import StrEnum


class Scenario(StrEnum):
    STANDARD_BOSS = "standard_boss"
    PINNACLE_BOSS = "pinnacle_boss"
    UBER_PINNACLE_BOSS = "uber_pinnacle_boss"
    MAPPING = "mapping"


DEFAULT = Scenario.PINNACLE_BOSS

BOSS_BOX: Mapping[Scenario, str] = {
    Scenario.STANDARD_BOSS: "Boss",
    Scenario.PINNACLE_BOSS: "Pinnacle",
    Scenario.UBER_PINNACLE_BOSS: "Uber",
    Scenario.MAPPING: "Pinnacle",
}
