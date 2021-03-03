from iscram.domain.metrics.importance import (
    birnbaum_importance, birnbaum_structural_importance
)
from iscram.domain.model import (
    SystemGraph, Component, Indicator, RiskRelation
)


def test_birnbaum_importance_simple_and(simple_and: SystemGraph):
    # components = frozenset({Component("one", "and"),
    #                         Component(2, "two", "and"),
    #                         Component(3, "three", "and")})
    #
    # indicator = Indicator("and", frozenset({RiskRelation(3, -1)}))
    #
    # deps = frozenset({RiskRelation(1, 3), RiskRelation(2, 3)})
    #
    # sg = SystemGraph("simple", components, frozenset(), deps, frozenset(), indicator)

    b_imps = birnbaum_importance(simple_and)

    assert b_imps == {"one": 0.0, "two": 0.0, "three": 1.0}


def test_birnbaum_structural_importance_simple_and(simple_and: SystemGraph):
    # components = frozenset({Component("one", "and"),
    #                         Component("two", "and"),
    #                         Component("three", "and")})
    #
    # indicator = Indicator("and", frozenset({RiskRelation(3, -1)}))
    #
    # deps = frozenset({RiskRelation(1, 3), RiskRelation(2, 3)})
    #
    # sg = SystemGraph("simple", components, frozenset(), deps, frozenset(), indicator)

    b_imps = birnbaum_structural_importance(simple_and)

    assert b_imps == {"one": 0.25, "two": 0.25, "three": 0.75}
