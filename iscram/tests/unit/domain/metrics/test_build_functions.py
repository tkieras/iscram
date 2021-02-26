from iscram.domain.metrics.graph_functions import (
    get_tree_boolean_function_lambda, get_graph_dicts_from_system_graph
)

from iscram.domain.model import (
    SystemGraph, Component, Indicator, RiskRelation
)


def test_build_simple_logic_and():
    components = frozenset({Component(1, "one", "and"), Component(2, "two", "and"), Component(3, "three", "and")})

    indicator = Indicator("and", frozenset({RiskRelation(3, -1)}))

    deps = frozenset({RiskRelation(1, 3), RiskRelation(2, 3)})

    sg = SystemGraph("simple", components, frozenset(), deps, frozenset(), indicator)

    graph, logic = get_graph_dicts_from_system_graph(sg, ignore_suppliers=True)

    fn = get_tree_boolean_function_lambda(-1, graph, logic)

    x = {-1: False, 1: True, 2: True, 3: True}
    expected = True
    assert fn(x) == expected

    x = {-1: False, 1: False, 2: False, 3: True}
    expected = True
    assert fn(x) == expected

    x = {-1: False, 1: True, 2: True, 3: False}
    expected = True
    assert fn(x) == expected

    x = {-1: False, 1: False, 2: True, 3: False}
    expected = False
    assert fn(x) == expected

    x = {-1: False, 1: True, 2: False, 3: False}
    expected = False
    assert fn(x) == expected


def test_build_simple_logic_or():
    components = frozenset({Component(1, "one", "and"), Component(2, "two", "and"), Component(3, "three", "or")})

    indicator = Indicator("and", frozenset({RiskRelation(3, -1)}))

    deps = frozenset({RiskRelation(1, 3), RiskRelation(2, 3)})

    sg = SystemGraph("simple", components, frozenset(), deps, frozenset(), indicator)

    graph, logic = get_graph_dicts_from_system_graph(sg, ignore_suppliers=True)

    fn = get_tree_boolean_function_lambda(-1, graph, logic)

    x = {-1: False, 1: True, 2: True, 3: True}
    expected = True
    assert fn(x) == expected

    x = {-1: False, 1: False, 2: False, 3: True}
    expected = True
    assert fn(x) == expected

    x = {-1: False, 1: True, 2: True, 3: False}
    expected = True
    assert fn(x) == expected

    x = {-1: False, 1: False, 2: True, 3: False}
    expected = True
    assert fn(x) == expected

    x = {-1: False, 1: True, 2: False, 3: False}
    expected = True
    assert fn(x) == expected

    x = {-1: False, 1: False, 2: False, 3: False}
    expected = False
    assert fn(x) == expected
