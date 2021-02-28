import pytest

from iscram.domain.metrics.graph_functions import prep_for_mocus, is_tree
from iscram.domain.metrics.risk import risk_by_cutsets


@pytest.mark.parametrize("count", range(10))
def test_rand_tree_is_valid(rand_tree_sg, count):
    assert rand_tree_sg.valid_values()


@pytest.mark.parametrize("count", range(10))
def test_rand_tree_is_tree(rand_tree_sg, count):
    graph, logic = prep_for_mocus(rand_tree_sg, ignore_suppliers=True)
    assert(is_tree(graph, "indicator"))


@pytest.mark.parametrize("count", range(10))
def test_smoke_rand_tree_risk(rand_tree_sg, count):
    assert(0 <= risk_by_cutsets(rand_tree_sg) <= 1.0)