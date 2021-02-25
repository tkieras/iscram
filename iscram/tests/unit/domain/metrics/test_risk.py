import pytest

from iscram.domain.metrics.risk import (
    risk_by_cutsets, risk_by_function, collect_x
)
from iscram.domain.model import (
    SystemGraph, Component, Indicator, RiskRelation
)


def test_collect_x(simple_and: SystemGraph):


    expected = {-1: 0, 1: 0.25, 2: 0.25, 3: 0.25}

    assert (collect_x(simple_and) == expected)


def test_risk_by_cutsets_simple_and(simple_and: SystemGraph):

    sg = simple_and

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


def test_risk_by_function_simple_and(simple_and: SystemGraph):
    sg = simple_and

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


def test_risk_by_function_sg_simple_and(simple_and: SystemGraph):
    assert(risk_by_function(simple_and) == 0.296875)


@pytest.mark.parametrize("count", range(50))
def test_biequal_risk_functions(rand_tree_sg, count):
    assert(risk_by_function(rand_tree_sg) == pytest.approx(risk_by_cutsets(rand_tree_sg)))