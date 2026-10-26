import random

import pytest

from petgarden.domain.rollcall import NoStudentsError, RollcallEntry, choose, fair_pool


def e(i: int, ts: str | None = None) -> RollcallEntry:
    return RollcallEntry(id=i, last_picked_at=ts)


def test_empty_raises() -> None:
    with pytest.raises(NoStudentsError):
        fair_pool([])
    with pytest.raises(NoStudentsError):
        choose([], "fair", None, random.Random(1))


def test_single_student() -> None:
    pool = fair_pool([e(1)])
    assert [x.id for x in pool] == [1]


def test_null_last_picked_first() -> None:
    entries = [e(1, "2026-10-25T08:00:00Z"), e(2, None), e(3, "2026-10-24T08:00:00Z"), e(4, None)]
    pool = fair_pool(entries)
    ids = [x.id for x in pool]
    assert len(ids) == 2  # ceil(4/3)=2
    assert ids == [2, 4]  # NULL 最前，按 id 稳定


def test_pool_size() -> None:
    entries = [e(i) for i in range(1, 10)]
    assert len(fair_pool(entries)) == 3  # ceil(9/3)
    entries = [e(i) for i in range(1, 11)]
    assert len(fair_pool(entries)) == 4  # ceil(10/3)


def test_exclude_last_picked() -> None:
    entries = [e(1), e(2), e(3), e(4), e(5)]
    # 不指定 last 时池子是前 2 个
    pool = fair_pool(entries, last_picked_id=None)
    assert [x.id for x in pool] == [1, 2]
    # 指定 last=1 后应排除 1
    pool = fair_pool(entries, last_picked_id=1)
    assert 1 not in [x.id for x in pool]
    assert len(pool) >= 1


def test_last_picked_fallback_when_pool_empties() -> None:
    entries = [e(1), e(2)]
    pool = fair_pool(entries, last_picked_id=1)
    assert [x.id for x in pool] == [2]


def test_choose_random_mode() -> None:
    entries = [e(i) for i in range(1, 7)]
    rng = random.Random(42)
    picked = choose(entries, "random", None, rng)
    assert picked.id in range(1, 7)


def test_choose_fair_deterministic() -> None:
    entries = [e(i) for i in range(1, 7)]
    rng = random.Random(7)
    picked = choose(entries, "fair", None, rng)
    pool_ids = [x.id for x in fair_pool(entries)]
    assert picked.id in pool_ids