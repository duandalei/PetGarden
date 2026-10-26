"""积分计算纯函数。"""

from petgarden.domain.pets import clamp_score

MIN_DELTA = -5
MAX_DELTA = 5


class ScoreAtLimitError(Exception):
    """夹紧后分数没有变化。"""

    def __init__(self, score: int, delta: int) -> None:
        super().__init__("score at limit")
        self.score = score
        self.delta = delta


def validate_delta(delta: int) -> int:
    if not isinstance(delta, int) or isinstance(delta, bool):
        raise ValueError("delta 必须是整数")
    if delta == 0 or delta < MIN_DELTA or delta > MAX_DELTA:
        raise ValueError("delta 必须是 [-5, 5] 之间的非零整数")
    return delta


def apply_delta(score: int, delta: int) -> int:
    """返回夹紧后的新分数；若无变化抛出 ScoreAtLimitError。"""
    validate_delta(delta)
    new_score = clamp_score(score + delta)
    if new_score == score:
        raise ScoreAtLimitError(score, delta)
    return new_score