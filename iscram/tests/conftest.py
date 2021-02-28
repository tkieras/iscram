from importlib.resources import read_text
import random

import pytest

from iscram.adapters.json import load_system_graph_json_str

from iscram.domain.model import (
    SystemGraph, Component, RiskRelation, Indicator
)


@pytest.fixture
def simple_and():
    json_str = read_text("iscram.tests.system_graph_test_data", "simple_and.json")

    return load_system_graph_json_str(json_str)


@pytest.fixture
def simple_or():
    json_str = read_text("iscram.tests.system_graph_test_data", "simple_or.json")

    return load_system_graph_json_str(json_str)


@pytest.fixture
def canonical():
    json_str = read_text("iscram.tests.system_graph_test_data", "canonical.json")

    return load_system_graph_json_str(json_str)


@pytest.fixture
def non_tree_simple_and():
    json_str = read_text("iscram.tests.system_graph_test_data", "non_tree_simple_and.json")

    return load_system_graph_json_str(json_str)


@pytest.fixture
def rand_tree_sg():
    def rand_logic():
        return random.choice(["and", "or"])

    def rand_risk():
        return random.random()

    def rand_cost():
        return random.randint(0, 100)

    n = 10
    unused = [str(i) for i in range(1, n)]
    random.shuffle(unused)

    used = ["0"]
    nodes = {"0"}
    edges = set()

    while unused:
        child = unused.pop(0)
        parent = random.choice(used)
        nodes.add(child)
        edges.add((child, parent))

    nodes.remove("0")
    ind_edges = list(filter(lambda e: e[1] == "0", edges))
    for edge in ind_edges:
        edges.remove(edge)

    indicator = Indicator(rand_logic(), frozenset([RiskRelation(*edge) for edge in ind_edges]))

    components = frozenset([Component(node, rand_logic(), rand_risk(), rand_cost()) for node in nodes])

    deps = frozenset([RiskRelation(*edge) for edge in edges])

    sg = SystemGraph("rand_tree", components, frozenset(), deps, frozenset(), indicator)

    return sg
