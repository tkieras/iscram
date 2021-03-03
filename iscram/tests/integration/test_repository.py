import pytest

from iscram.domain.model import SystemGraph

from iscram.adapters.repository import FakeRepository

from iscram.service_layer.services import get_risk


def test_fake_repository_risk_put_first(simple_and: SystemGraph):
    repo = FakeRepository()

    saved = 0.123456789

    repo.put(simple_and, "risk", saved)

    assert get_risk(simple_and, repo) == saved


def test_fake_repository_risk_calculate_first(simple_and: SystemGraph):

    repo = FakeRepository()

    expected = 0.0
    assert get_risk(simple_and, repo) == expected


def test_fake_repository_put(simple_and: SystemGraph):
    repo = FakeRepository()

    expected = 0.0

    get_risk(simple_and, repo)

    assert repo.storage[simple_and]["risk"] == expected


def test_fake_repository_get_bad_key(simple_and: SystemGraph):
    repo = FakeRepository()

    get_risk(simple_and, repo)

    assert repo.get(simple_and, "ice cream") is None


def test_fake_repository_delete(simple_and: SystemGraph):
    repo = FakeRepository()

    expected = 0.0

    get_risk(simple_and, repo)

    assert repo.storage[simple_and]["risk"] == expected

    repo.delete(simple_and, "risk")

    assert "risk" not in repo.storage


def test_fake_repo_store_cutsets(simple_and: SystemGraph):

    repo = FakeRepository()

    cutsets = frozenset([frozenset()])

    repo.put(simple_and, "cutsets", cutsets)

    assert simple_and.structure() in repo.storage


def test_fake_repo_get_cutsets(simple_and: SystemGraph):
    repo = FakeRepository()

    cutsets = frozenset([frozenset("hi")])

    repo.put(simple_and, "cutsets", cutsets)

    retrieved = repo.get(simple_and, "cutsets")

    assert cutsets == retrieved


def test_fake_repo_delete_nonexisting(simple_and: SystemGraph):
    repo = FakeRepository()

    assert repo.delete(simple_and, "ice cream") is None