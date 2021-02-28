from collections import defaultdict
import pytest

from iscram.domain.metrics.risk import (
    risk_by_cutsets, risk_by_function, collect_x
)
from iscram.domain.model import SystemGraph


def test_collect_x(simple_and: SystemGraph):

    expected = {"indicator": 0, "one": 0.0, "two": 0.0, "three": 0.0}

    assert (collect_x(simple_and) == expected)


def test_risk_by_cutsets_simple_and(simple_and: SystemGraph):

    sg = simple_and

    x = {"indicator": 0, "one": 0, "two": 0, "three": 0}
    assert (risk_by_cutsets(sg, x) == 0)

    x = {"indicator": 0, "one": 0, "two": 0, "three": 1}
    assert (risk_by_cutsets(sg, x) == 1)

    x = {"indicator": 0, "one": 0, "two": 1, "three": 0}
    assert (risk_by_cutsets(sg, x) == 0)

    x = {"indicator": 0, "one": 1, "two": 0, "three": 0}
    assert (risk_by_cutsets(sg, x) == 0)

    x = {"indicator": 0, "one": 1, "two": 1, "three": 0}
    assert (risk_by_cutsets(sg, x) == 1)

    x = {"indicator": 0, "one": 0.5, "two": 0.5, "three": 0}
    assert (risk_by_cutsets(sg, x) == 0.25)

    x = {"indicator": 0, "one": 0, "two": 0, "three": 0.5}
    assert (risk_by_cutsets(sg, x) == 0.5)


def test_risk_by_function_simple_and(simple_and: SystemGraph):
    sg = simple_and
    y = defaultdict(lambda: False)

    y.update(dict(indicator=0, one=0, two=0, three=0))
    assert (risk_by_function(sg, y) == 0)

    y.update(dict(indicator=0, one=0, two=0, three=1))
    assert (risk_by_function(sg, y) == 1)

    y.update(dict(indicator=0, one=0, two=1, three=0))
    assert (risk_by_function(sg, y) == 0)

    y.update(dict(indicator=0, one=1, two=0, three=0))
    assert (risk_by_function(sg, y) == 0)

    y.update(dict(indicator=0, one=1, two=1, three=0))
    assert (risk_by_function(sg, y) == 1)

    y.update(dict(indicator=0, one=0.5, two=0.5, three=0))
    assert (risk_by_function(sg, y) == 0.25)

    y.update(dict(indicator=0, one=0, two=0, three=0.5))
    assert (risk_by_function(sg, y) == 0.5)


def test_risk_by_function_sg_simple_and(simple_and: SystemGraph):
    assert(risk_by_function(simple_and) == 0.0)


@pytest.mark.parametrize("count", range(5))
def test_biequal_risk_functions(rand_tree_sg, count):
    assert(risk_by_function(rand_tree_sg) == pytest.approx(risk_by_cutsets(rand_tree_sg)))