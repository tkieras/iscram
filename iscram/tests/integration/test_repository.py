import pytest

from iscram.domain.model import (
    SystemGraph, Component, Indicator, Supplier, RiskRelation
)

from iscram.adapters.repository import (
    FakeRepository, RepositoryError
)

from iscram.service_layer.services import get_risk


def test_fake_repository_risk_put_first():
    components = frozenset({Component(1, "one", "and"),
                            Component(2, "two", "and"),
                            Component(3, "three", "and")})

    indicator = Indicator("and", frozenset({RiskRelation(3, -1)}))

    deps = frozenset({RiskRelation(1, 3), RiskRelation(2, 3)})

    sg = SystemGraph("simple", components, frozenset(), deps, frozenset(), indicator)

    repo = FakeRepository()

    saved = 0.123456789

    repo.put(sg, "risk", saved)

    assert get_risk(sg, repo) == saved


def test_fake_repository_risk_calculate_first():
    components = frozenset({Component(1, "one", "and", 0.5),
                            Component(2, "two", "and", 0.5),
                            Component(3, "three", "and", 0.0)})

    indicator = Indicator("and", frozenset({RiskRelation(3, -1)}))

    deps = frozenset({RiskRelation(1, 3), RiskRelation(2, 3)})

    sg = SystemGraph("simple", components, frozenset(), deps, frozenset(), indicator)

    repo = FakeRepository()

    expected = 0.25
    assert get_risk(sg, repo) == expected


def test_fake_repository_put():
    components = frozenset({Component(1, "one", "and", 0.5),
                            Component(2, "two", "and", 0.5),
                            Component(3, "three", "and", 0.0)})

    indicator = Indicator("and", frozenset({RiskRelation(3, -1)}))

    deps = frozenset({RiskRelation(1, 3), RiskRelation(2, 3)})

    sg = SystemGraph("simple", components, frozenset(), deps, frozenset(), indicator)

    repo = FakeRepository()

    expected = 0.25

    get_risk(sg, repo)

    assert repo.storage[sg]["risk"] == expected


def test_fake_repository_get_bad_key(simple_and: SystemGraph):
    repo = FakeRepository()

    get_risk(simple_and, repo)

    with pytest.raises(RepositoryError):
        repo.get(simple_and, "ice cream")


def test_fake_repository_delete():
    components = frozenset({Component(1, "one", "and", 0.5),
                            Component(2, "two", "and", 0.5),
                            Component(3, "three", "and", 0.0)})

    indicator = Indicator("and", frozenset({RiskRelation(3, -1)}))

    deps = frozenset({RiskRelation(1, 3), RiskRelation(2, 3)})

    sg = SystemGraph("simple", components, frozenset(), deps, frozenset(), indicator)

    repo = FakeRepository()

    expected = 0.25

    get_risk(sg, repo)

    assert repo.storage[sg]["risk"] == expected

    repo.delete(sg, "risk")

    with pytest.raises(RepositoryError):
        repo.delete(sg, "risk")

