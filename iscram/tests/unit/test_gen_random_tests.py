import pytest

from iscram.domain.metrics.risk import risk_by_cutsets
from iscram.tests.unit.domain.model.gen_random_sg import gen_random_tree


@pytest.mark.parametrize("count", range(10))
def test_rand_tree_is_valid(rand_tree_sg, count):
    assert rand_tree_sg.valid_values()


@pytest.mark.parametrize("count", range(10))
def test_smoke_rand_tree_risk(rand_tree_sg, count):
    assert(0 <= risk_by_cutsets(rand_tree_sg) <= 1.0)


def test_gen_random_tree():
    gen_random_tree(10, False)
    gen_random_tree(25, False)
    gen_random_tree(50, False)
    gen_random_tree(75, False)
    gen_random_tree(100, False)