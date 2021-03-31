from pytest import approx

from iscram.domain.metrics.importance import (
    birnbaum_importance, birnbaum_structural_importance, fractional_importance_traits
)
from iscram.domain.model import (
    SystemGraph, Component, Indicator, RiskRelation
)


def test_birnbaum_importance_simple_and(simple_and: SystemGraph):
    b_imps = birnbaum_importance(simple_and)
    assert b_imps == {"one": 0.0, "two": 0.0, "three": 1.0}


def test_birnbaum_structural_importance_simple_and(simple_and: SystemGraph):
    b_imps = birnbaum_structural_importance(simple_and)
    assert b_imps == {"one": 0.25, "two": 0.25, "three": 0.75}


def test_select_birnbaum_importance(simple_and: SystemGraph):
    b_imps = birnbaum_importance(simple_and, select=["two", "three"])
    assert len(b_imps) == 1
    assert "select" in b_imps
    assert b_imps["select"] == 1.0


def test_select_birnbaum_importance_none(full_example: SystemGraph):
    b_imp = birnbaum_importance(full_example, select=[])
    assert b_imp["select"] == 0.0


def test_fractional_importance_traits(full_example: SystemGraph):
    f_imps = fractional_importance_traits(full_example)

    assert approx((5/28), f_imps[("domestic", False)])
    assert approx((9/28), f_imps[("domestic", True)])
    assert approx((7/28), f_imps[("certified", False)])
    assert approx((7/28), f_imps[("certified", True)])
