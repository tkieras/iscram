from collections import defaultdict

from iscram.domain.metrics.graph_functions import (
    get_tree_boolean_function_lambda, prep_for_mocus
)

from iscram.domain.model import SystemGraph


x_all = [
    {"indicator": False, "one": True, "two": True, "three": True},
    {"indicator": False, "one": False, "two": False, "three": True},
    {"indicator": False, "one": False, "two": True, "three": False},
    {"indicator": False, "one": True, "two": False, "three": False},
    {"indicator": False, "one": True, "two": True, "three": False},
    {"indicator": False, "one": False, "two": False, "three": False}
]


def test_build_simple_logic_and(simple_and: SystemGraph):
    graph, logic = prep_for_mocus(simple_and, ignore_suppliers=True)
    fn = get_tree_boolean_function_lambda("indicator", graph, logic)

    expected_x_and = [True, True, False, False, True, False]

    for x, expected in zip(x_all, expected_x_and):
        y = defaultdict(lambda: False)
        y.update(x)

        assert fn(y) == expected


def test_build_simple_logic_or(simple_or):
    graph, logic = prep_for_mocus(simple_or, ignore_suppliers=True)

    fn = get_tree_boolean_function_lambda("indicator", graph, logic)

    expected_x_or = [True, True, True, True, True, False]

    for x, expected in zip(x_all, expected_x_or):
        y = defaultdict(lambda: False)
        y.update(x)
        assert fn(y) == expected
