import pytest

from petgarden.domain.pets import (
    LEVEL_THRESHOLDS,
    STAGE_NAMES,
    can_switch_pet,
    clamp_score,
    divine_unlocked,
    level_from_score,
    mood_from_score,
    stage_from_level,
)
from petgarden.domain.scoring import ScoreAtLimitError, apply_delta, validate_delta


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (-1, 1),
        (0, 1),
        (19, 1),
        (20, 2),
        (39, 2),
        (40, 3),
        (59, 3),
        (60, 4),
        (79, 4),
        (80, 5),
        (100, 5),
        (101, 5),
    ],
)
def test_level_from_score_boundaries(score: int, expected: int) -> None:
    assert level_from_score(score) == expected


def test_stage_names() -> None:
    assert STAGE_NAMES == ["初遇", "相伴", "默契", "蜕变", "传说"]
    assert [stage_from_level(i) for i in range(1, 6)] == STAGE_NAMES
    assert LEVEL_THRESHOLDS == [0, 20, 40, 60, 80]


@pytest.mark.parametrize(
    ("score", "expected"),
    [(0, "sad"), (19, "sad"), (20, "neutral"), (59, "neutral"), (60, "happy"), (100, "happy")],
)
def test_mood_from_score(score: int, expected: str) -> None:
    assert mood_from_score(score) == expected


def test_clamp_score() -> None:
    assert clamp_score(-5) == 0
    assert clamp_score(105) == 100
    assert clamp_score(50) == 50


def test_apply_delta() -> None:
    assert apply_delta(50, 1) == 51
    assert apply_delta(50, -1) == 49
    assert apply_delta(98, 5) == 100
    assert apply_delta(2, -5) == 0


def test_apply_delta_at_limit() -> None:
    with pytest.raises(ScoreAtLimitError):
        apply_delta(100, 1)
    with pytest.raises(ScoreAtLimitError):
        apply_delta(0, -1)
    with pytest.raises(ScoreAtLimitError):
        apply_delta(100, 5)
    with pytest.raises(ScoreAtLimitError):
        apply_delta(0, -5)


def test_validate_delta() -> None:
    for bad in (0, 6, -6):
        with pytest.raises(ValueError):
            validate_delta(bad)
    assert validate_delta(-5) == -5
    assert validate_delta(5) == 5


def test_divine_unlocked() -> None:
    assert not divine_unlocked({})
    assert not divine_unlocked({"cat": 4})
    assert divine_unlocked({"cat": 5})
    assert divine_unlocked({"fox": 5})
    # 神兽自己 L5 不算解锁条件
    assert not divine_unlocked({"dragon": 5})


def test_can_switch_pet() -> None:
    ok, _ = can_switch_pet(79, "cat", "dog", unlocked=False)
    assert not ok
    ok, code = can_switch_pet(80, "cat", "dog", unlocked=False)
    assert ok and code == ""
    ok, code = can_switch_pet(80, "cat", "cat", unlocked=False)
    assert not ok and code == "SAME_SPECIES"
    ok, code = can_switch_pet(80, "cat", "dragon", unlocked=False)
    assert not ok and code == "DIVINE_LOCKED"
    ok, _ = can_switch_pet(80, "cat", "dragon", unlocked=True)
    assert ok
    ok, code = can_switch_pet(80, "cat", "unicorn", unlocked=True)
    assert not ok and code == "INVALID_SPECIES"