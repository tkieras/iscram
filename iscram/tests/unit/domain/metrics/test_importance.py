from pytest import approx
from typing import Dict
from iscram.domain.model import SystemGraph
from iscram.domain.metrics.importance import (
    birnbaum_importance, birnbaum_structural_importance, fractional_importance_of_attributes
)
from iscram.domain.metrics.probability_providers import provide_p_direct_from_data


def test_birnbaum_importance_minimal(minimal: SystemGraph):
    p = {"x1": 0, "x2": 0, "x3": 0, "indicator": 0}
    b_imps = birnbaum_importance(minimal, p)
    assert b_imps == {"x1": 0.0, "x2": 0.0, "x3": 1.0}


def test_birnbaum_structural_importance_minimal(minimal: SystemGraph):
    b_imps = birnbaum_structural_importance(minimal)
    assert b_imps == {"x1": 0.25, "x2": 0.25, "x3": 0.75}


def test_select_birnbaum_importance(minimal: SystemGraph):
    p = {"x1": 0, "x2": 0, "x3": 0, "indicator": 0}
    b_imps = birnbaum_importance(minimal, p, select=["x2", "x3"])
    assert b_imps == {"select": 1.0}


def test_select_birnbaum_importance_none(full_example_system: SystemGraph, full_example_data_1: Dict):
    p = provide_p_direct_from_data(full_example_system, full_example_data_1)
    b_imp = birnbaum_importance(full_example_system, p, select=[])
    assert b_imp["select"] == 0.0


def test_fractional_importance_traits(full_example_system: SystemGraph, full_example_data_1: Dict):
    f_imps = fractional_importance_of_attributes(full_example_system, full_example_data_1)

    assert approx((5/28), f_imps["domestic"][False])
    assert approx((9/28), f_imps["domestic"][True])
    assert approx((7/28), f_imps["certified"][False])
    assert approx((7/28), f_imps["certified"][True])
