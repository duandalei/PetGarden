"""宠物物种目录、等级/阶段/心情派生、神兽解锁规则。"""

from typing import Literal

SpeciesId = Literal["cat", "dog", "rabbit", "panda", "fox", "dragon"]

SPECIES_CATALOG: list[dict[str, str]] = [
    {"id": "cat", "name": "小猫", "type": "normal"},
    {"id": "dog", "name": "小狗", "type": "normal"},
    {"id": "rabbit", "name": "小兔", "type": "normal"},
    {"id": "panda", "name": "熊猫", "type": "normal"},
    {"id": "fox", "name": "小狐", "type": "normal"},
    {"id": "dragon", "name": "青龙", "type": "divine"},
]

NORMAL_SPECIES: list[str] = [s["id"] for s in SPECIES_CATALOG if s["type"] == "normal"]
DIVINE_SPECIES: list[str] = [s["id"] for s in SPECIES_CATALOG if s["type"] == "divine"]
ALL_SPECIES: list[str] = [s["id"] for s in SPECIES_CATALOG]
SPECIES_NAMES: dict[str, str] = {s["id"]: s["name"] for s in SPECIES_CATALOG}
SPECIES_TYPES: dict[str, str] = {s["id"]: s["type"] for s in SPECIES_CATALOG}

LEVEL_THRESHOLDS: list[int] = [0, 20, 40, 60, 80]
STAGE_NAMES: list[str] = ["初遇", "相伴", "默契", "蜕变", "传说"]

MIN_SCORE = 0
MAX_SCORE = 100


def clamp_score(score: int) -> int:
    return max(MIN_SCORE, min(MAX_SCORE, score))


def level_from_score(score: int) -> int:
    s = clamp_score(score)
    if s < 20:
        return 1
    if s < 40:
        return 2
    if s < 60:
        return 3
    if s < 80:
        return 4
    return 5


def stage_from_level(level: int) -> str:
    level = max(1, min(5, level))
    return STAGE_NAMES[level - 1]


def mood_from_score(score: int) -> str:
    s = clamp_score(score)
    if s >= 60:
        return "happy"
    if s >= 20:
        return "neutral"
    return "sad"


def is_valid_species(species: str) -> bool:
    return species in SPECIES_NAMES


def divine_unlocked(best_levels: dict[str, int]) -> bool:
    """任意普通物种历史最高等级达到 5 即解锁神兽。"""
    return any(best_levels.get(sp, 0) >= 5 for sp in NORMAL_SPECIES)


def can_switch_pet(
    current_score: int,
    current_species: str,
    target_species: str,
    unlocked: bool,
) -> tuple[bool, str]:
    """返回 (是否允许, 错误码)。错误码为空字符串表示允许。"""
    if not is_valid_species(target_species):
        return False, "INVALID_SPECIES"
    if target_species == current_species:
        return False, "SAME_SPECIES"
    if level_from_score(current_score) < 5:
        return False, "PET_SWITCH_NOT_READY"
    if target_species in DIVINE_SPECIES and not unlocked:
        return False, "DIVINE_LOCKED"
    return True, ""