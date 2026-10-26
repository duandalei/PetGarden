"""随机点名候选池规则（纯函数）。"""

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass


class NoStudentsError(Exception):
    """没有可抽取的学生。"""


@dataclass(frozen=True)
class RollcallEntry:
    id: int
    last_picked_at: str | None


def fair_pool(
    entries: Sequence[RollcallEntry], last_picked_id: int | None = None
) -> list[RollcallEntry]:
    """公平模式候选池：按 last_picked_at 升序（NULL 最前），取前 ceil(n/3) 人；
    若班级人数 > 1 且候选池包含上次抽中者，则排除之。"""
    if not entries:
        raise NoStudentsError
    ordered = sorted(
        entries,
        key=lambda e: (e.last_picked_at is not None, e.last_picked_at or "", e.id),
    )
    k = max(1, math.ceil(len(entries) / 3))
    pool = list(ordered[:k])
    if len(entries) > 1 and last_picked_id is not None:
        filtered = [e for e in pool if e.id != last_picked_id]
        pool = filtered or [e for e in entries if e.id != last_picked_id]
    return pool


def choose(
    entries: Sequence[RollcallEntry],
    mode: str,
    last_picked_id: int | None,
    rng: random.Random,
) -> RollcallEntry:
    if not entries:
        raise NoStudentsError
    pool = list(entries) if mode == "random" else fair_pool(entries, last_picked_id)
    return rng.choice(pool)