import pytest

from iscram.domain.metrics.graph_functions import (
    probability_union, get_tree_boolean_function_lambda, is_tree, enumerate_all_combinations
)
from pprint import pprint

states = ((0, 0, 0),
            (0, 0, 1),
            (0, 1, 0),
            (1, 0, 0),
            (1, 1, 0),
            (0, 1, 1),
            (1, 1, 1))
results = (0, 1, 0, 0, 1, 1, 1)


@pytest.mark.parametrize("x,expected", (
                         ((0.3, 0.245), 0.4715),
                         ((0.5, 0.5, 0.5), 0.875),
                         ((0.01, 0.93, 0.24, 0.56), 0.976826)
                         ))
def test_probability_union(x, expected):
    assert(probability_union(x) == pytest.approx(expected))


def test_get_tree_boolean_function_lambda():
    graph = {2 : [1, 0]}
    logic = {2: "and", 1: "and", 0: "and"}

    fn = get_tree_boolean_function_lambda(2, graph, logic)

    for state, expected in zip(states, results):
        assert(fn(state) == expected)


def test_is_tree_fail():
    graph = {2: [1, 0], 1: [4], 0: [4]}
    assert not is_tree(graph, 2)


def test_is_tree_success():
    graph = {2: [1, 0], 0: [3], 3: [5, 6], 6: [7]}
    assert is_tree(graph, 2)


def test_is_tree_cyclic_input():
    graph = {2: [1, 0], 1: [2]}
    assert not is_tree(graph, 2)


def test_enumerate_all_combinations():
    x = (1,2,3)
    combs = set(enumerate_all_combinations(x))

    expected = {(), (1,), (2,), (3,), (1, 2), (2, 3), (1, 3), (1, 2, 3)}
    assert combs == expected

