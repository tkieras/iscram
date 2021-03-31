from importlib.resources import read_text
import random

import pytest

from iscram.adapters.json import load_system_graph_json_str, dump_system_graph_json_str

from iscram.tests.unit.domain.model.gen_random_sg import gen_random_tree

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
def simple_and_suppliers():
    json_str = read_text("iscram.tests.system_graph_test_data", "simple_and_suppliers.json")

    return load_system_graph_json_str(json_str)


@pytest.fixture
def full_example():
    json_str = read_text("iscram.tests.system_graph_test_data", "full_example.json")

    return load_system_graph_json_str(json_str)


@pytest.fixture
def rand_tree_sg():
    return gen_random_tree(10)
