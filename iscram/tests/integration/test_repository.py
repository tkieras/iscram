import pytest

from iscram.domain.model import SystemGraph
from iscram.adapters.repository import FakeRepository
from iscram.service_layer.services import get_bdd


def test_fake_repository_put_first(minimal: SystemGraph):
    repo = FakeRepository()
    saved = {"some object": "with values"}
    repo.put(minimal, "bdd_with_root", saved)
    assert get_bdd(minimal, repo) == saved


def test_fake_repository_get_bad_key(minimal: SystemGraph):
    repo = FakeRepository()
    get_bdd(minimal, repo)
    assert repo.get(minimal, "ice cream") is None


def test_fake_repository_delete(minimal: SystemGraph):
    repo = FakeRepository()
    expected = get_bdd(minimal, repo)
    assert repo.storage[minimal]["bdd_with_root"] == expected
    repo.delete(minimal, "bdd_with_root")
    assert "bdd_with_root" not in repo.storage


def test_fake_repo_delete_nonexisting(minimal: SystemGraph):
    repo = FakeRepository()
    assert repo.delete(minimal, "ice cream") is None