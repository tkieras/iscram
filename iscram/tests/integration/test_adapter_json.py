from importlib.resources import read_text

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


def test_adapter_json_load_dump_same():
    components = frozenset([Component(i, "name") for i in range(10)])

    suppliers = frozenset([Supplier(i, "name") for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation(i, -1) for i in {1, 2, 3}]))

    offerings = frozenset({Offering(15, 5, 0.5, 30), Offering(16, 5, 0.5, 30), Offering(17, 3, 0.5, 30)})

    deps = frozenset({RiskRelation(1, 3), RiskRelation(2, 3), RiskRelation(5, 6)})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    json = dump_system_graph_json(sg)

    loaded = load_system_graph_json(json)

    assert sg == loaded

    assert loaded.validate()


def test_adapter_save_json():
    components = frozenset({Component(1, "one", "and", 0.5),
                            Component(2, "two", "and", 0.125),
                            Component(3, "three", "and", 0.75)})

    indicator = Indicator("and", frozenset({RiskRelation(3, -1)}))

    deps = frozenset({RiskRelation(1, 3), RiskRelation(2, 3)})

    sg = SystemGraph("simple", components, frozenset(), deps, frozenset(), indicator)

    with open("tmp_test_output.json", "w") as outfile:
        outfile.write(dump_system_graph_json_str(sg))


def test_adapter_load_json_str():
    json_str = read_text("iscram.tests.system_graph_test_data", "simple_and.json")

    sg = load_system_graph_json_str(json_str)

    assert(sg.name == "simple")
    assert(len(sg.components) == 3)