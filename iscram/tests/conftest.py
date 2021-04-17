import pytest
from importlib.resources import read_text
from typing import Dict
import json

from iscram.domain.model import SystemGraph


def get_sg_from_file(filename: str) -> SystemGraph:
    file_data = read_text("iscram.tests.system_graph_test_data", filename)
    sg_dict = json.loads(file_data)
    return SystemGraph(**sg_dict)


def get_data_from_file(filename: str) -> Dict:
    file_data = read_text("iscram.tests.system_graph_test_data", filename)
    return json.loads(file_data)


@pytest.fixture
def minimal():
    return get_sg_from_file("minimal.json")


@pytest.fixture
def diamond():
    return get_sg_from_file("diamond.json")


@pytest.fixture
def diamond_suppliers():
    return get_sg_from_file("diamond_suppliers.json")


@pytest.fixture
def canonical():
    return get_sg_from_file("canonical.json")


@pytest.fixture
def full_example_system():
    return get_sg_from_file("full_example_system.json")


@pytest.fixture
def full_example_data_1():
    return get_data_from_file("full_example_data_1.json")
