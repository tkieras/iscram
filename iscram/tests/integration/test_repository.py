import pytest

from iscram.domain.model import SystemGraph
from iscram.adapters.repository import LRUCacheRepository, RepositoryLookupError


def test_basic_put_get(minimal: SystemGraph):
    repo = LRUCacheRepository()
    repo.put(minimal)
    retrieved = repo.get(minimal.get_id())
    assert retrieved == minimal


def test_basic_get(minimal: SystemGraph):
    repo = LRUCacheRepository()
    repo._storage[LRUCacheRepository._make_key(minimal)] = minimal
    retrieved = repo.get(minimal.get_id())
    assert retrieved == minimal


def test_make_key(minimal):
    expected = minimal.get_id()
    assert LRUCacheRepository._make_key(minimal) == expected

    expected = str(hash(minimal)) + "|" + str(hash("something"))
    assert LRUCacheRepository._make_key(minimal, "something") == expected


def test_evicted_gone(minimal: SystemGraph, full_example_system: SystemGraph):
    tiny = LRUCacheRepository(1)
    tiny.put(minimal)
    tiny.put(full_example_system)

    with pytest.raises(RepositoryLookupError):
        tiny.get(minimal.get_id())

    tiny.get(full_example_system.get_id())


def test_evicted_lru(minimal: SystemGraph, diamond: SystemGraph, full_example_system: SystemGraph):
    tiny = LRUCacheRepository(2)
    # add two
    tiny.put(minimal)
    tiny.put(diamond)
    # use first; should now move ahead of second
    tiny.get(minimal.get_id())
    # add a third; second should be evicted
    tiny.put(full_example_system)

    with pytest.raises(RepositoryLookupError):
        tiny.get(diamond.get_id())

    tiny.get(full_example_system.get_id())


def test_raise_error_on_absent_graph():
    repo = LRUCacheRepository()
    with pytest.raises(RepositoryLookupError):
        repo.get("hi")