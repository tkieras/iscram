from importlib.resources import read_text
import tempfile

from iscram.domain.model import (
    SystemGraph, Indicator, Component, Supplier, RiskRelation, Offering
)

from iscram.adapters.json import (
    dump_system_graph_json, load_system_graph_json,
    dump_system_graph_json_str, load_system_graph_json_str
)


def test_adapter_json_dump_minimal():
    sg = SystemGraph("test", frozenset(), frozenset(), frozenset(), frozenset(), Indicator("and", frozenset()))

    json = dump_system_graph_json(sg)

    expected = {
        "name": "test",
        "components": [],
        "suppliers": [],
        "offerings": [],
        "security_dependencies": [],
        "indicator": {
            "logic_function": "and",
            "dependencies": []
        }
    }

    assert json == expected


def test_adapter_json_load_minimal():
    json = {
        "name": "test",
        "components": [],
        "suppliers": [],
        "offerings": [],
        "security_dependencies": [],
        "indicator": {
            "logic_function": "and",
            "dependencies": []
        }
    }

    sg = load_system_graph_json(json)

    expected = SystemGraph("test", frozenset(), frozenset(), frozenset(), frozenset(), Indicator("and", frozenset()))

    assert sg == expected


def test_adapter_json_load_dump_same(canonical: SystemGraph):
    json = dump_system_graph_json(canonical)

    loaded = load_system_graph_json(json)

    assert canonical == loaded

    assert loaded.valid_values()


def test_adapter_save_json(simple_and: SystemGraph):

    with tempfile.TemporaryFile() as fp:
        fp.write(bytes(dump_system_graph_json_str(simple_and), 'utf-8'))
        fp.seek(0)
        json_str = fp.read()

    sg_loaded = load_system_graph_json_str(json_str.decode('utf-8'))
    assert sg_loaded == simple_and


def test_adapter_load_json_str():
    json_str = read_text("iscram.tests.system_graph_test_data", "simple_and.json")

    sg = load_system_graph_json_str(json_str)

    assert(sg.name == "simple")
    assert(len(sg.components) == 3)