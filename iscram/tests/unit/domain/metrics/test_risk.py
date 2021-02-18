from iscram.domain.metrics.risk import (
    risk_by_cutsets, risk_by_function, collect_x
)
from iscram.domain.model import (
    SystemGraph, Component, Indicator, RiskRelation
)


def test_collect_x():
    components = frozenset({Component(1, "one", "and", 0.5),
                            Component(2, "two", "and", 0.125),
                            Component(3, "three", "and", 0.75)})

    indicator = Indicator("and", frozenset({RiskRelation(3, -1)}))

    deps = frozenset({RiskRelation(1, 3), RiskRelation(2, 3)})

    sg = SystemGraph("simple", components, frozenset(), deps, frozenset(), indicator)

    expected = {-1: 0, 1: 0.5, 2: 0.125, 3: 0.75}

    assert (collect_x(sg) == expected)


def test_risk_by_cutsets_simple_and():
    components = frozenset({Component(1, "one", "and"),
                            Component(2, "two", "and"),
                            Component(3, "three", "and")})

    indicator = Indicator("and", frozenset({RiskRelation(3, -1)}))

    deps = frozenset({RiskRelation(1, 3), RiskRelation(2, 3)})

    sg = SystemGraph("simple", components, frozenset(), deps, frozenset(), indicator)

    x = {-1: 0, 1: 0, 2: 0, 3: 0}
    assert (risk_by_cutsets(sg, x) == 0)

    x = {-1: 0, 1: 0, 2: 0, 3: 1}
    assert (risk_by_cutsets(sg, x) == 1)

    x = {-1: 0, 1: 0, 2: 1, 3: 0}
    assert (risk_by_cutsets(sg, x) == 0)

    x = {-1: 0, 1: 1, 2: 0, 3: 0}
    assert (risk_by_cutsets(sg, x) == 0)

    x = {-1: 0, 1: 1, 2: 1, 3: 0}
    assert (risk_by_cutsets(sg, x) == 1)

    x = {-1: 0, 1: 0.5, 2: 0.5, 3: 0}
    assert (risk_by_cutsets(sg, x) == 0.25)

    x = {-1: 0, 1: 0, 2: 0, 3: 0.5}
    assert (risk_by_cutsets(sg, x) == 0.5)


def test_risk_by_function_simple_and():
    components = frozenset({Component(1, "one", "and"),
                            Component(2, "two", "and"),
                            Component(3, "three", "and")})

    indicator = Indicator("and", frozenset({RiskRelation(3, -1)}))

    deps = frozenset({RiskRelation(1, 3), RiskRelation(2, 3)})

    sg = SystemGraph("simple", components, frozenset(), deps, frozenset(), indicator)

    x = {-1: 0, 1: 0, 2: 0, 3: 0}
    assert (risk_by_function(sg, x) == 0)

    x = {-1: 0, 1: 0, 2: 0, 3: 1}
    assert (risk_by_function(sg, x) == 1)

    x = {-1: 0, 1: 0, 2: 1, 3: 0}
    assert (risk_by_function(sg, x) == 0)

    x = {-1: 0, 1: 1, 2: 0, 3: 0}
    assert (risk_by_function(sg, x) == 0)

    x = {-1: 0, 1: 1, 2: 1, 3: 0}
    assert (risk_by_function(sg, x) == 1)

    x = {-1: 0, 1: 0.5, 2: 0.5, 3: 0}
    assert (risk_by_function(sg, x) == 0.25)

    x = {-1: 0, 1: 0, 2: 0, 3: 0.5}
    assert (risk_by_function(sg, x) == 0.5)
