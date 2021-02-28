import pytest

from iscram.domain.metrics.graph_functions import (
    probability_union, get_tree_boolean_function_lambda, is_tree, enumerate_all_combinations
)

states = [{"zero": 0, "one": 0, "two": 0},
         {"zero": 0, "one": 0, "two": 1},
         {"zero": 0, "one": 1, "two": 0},
         {"zero": 1, "one": 0, "two": 0},
         {"zero": 1, "one": 1, "two": 0},
         {"zero": 0, "one": 1, "two": 1},
         {"zero": 1, "one": 1, "two": 1}]
results = (0, 1, 0, 0, 1, 1, 1)


@pytest.mark.parametrize("x,expected", (
                         ((0.3, 0.245), 0.4715),
                         ((0.5, 0.5, 0.5), 0.875),
                         ((0.01, 0.93, 0.24, 0.56), 0.976826)
                         ))
def test_probability_union(x, expected):
    assert(probability_union(x) == pytest.approx(expected))


def test_get_tree_boolean_function_lambda():
    graph = {"two" : ["one", "zero"]}
    logic = {"two": "and", "one": "and", "zero": "and"}

    fn = get_tree_boolean_function_lambda("two", graph, logic)

    for state, expected in zip(states, results):
        assert(fn(state) == expected)


def test_is_tree_fail():
    graph = {"two": ["one", "zero"], "one": ["four"], "zero": ["four"]}
    assert not is_tree(graph, "two")


def test_is_tree_success():
    graph = {"one": ["two", "three"], "three": ["four"], "four": ["five", "six"], "six": ["seven"]}
    assert is_tree(graph, "one")


def test_is_tree_cyclic_input():
    graph = {"two": ["one", "zero"], "one": ["two"]}
    assert not is_tree(graph, "two")


def test_enumerate_all_combinations():
    x = (1,2,3)
    combs = set(enumerate_all_combinations(x))

    expected = {(), (1,), (2,), (3,), (1, 2), (2, 3), (1, 3), (1, 2, 3)}
    assert combs == expected

