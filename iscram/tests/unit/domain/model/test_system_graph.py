from iscram.domain.model import (
    Node, Edge, SystemGraph, validate_data
)


def test_minimal(minimal: SystemGraph):
    minimal.self_validate()


def test_diamond(diamond: SystemGraph):
    diamond.self_validate()


def test_diamond_suppliers(diamond_suppliers: SystemGraph):
    diamond_suppliers.self_validate()


# Tests for System Graph Hashing
def test_sg_hashable(minimal: SystemGraph):
    assert hash(minimal)


def test_sg_hash_very_different(minimal: SystemGraph, diamond: SystemGraph):
    assert hash(minimal) != hash(diamond)


def test_sg_hash_very_close_node_missing(minimal: SystemGraph):
    pre = hash(minimal)
    del minimal.nodes["x1"]
    assert pre != hash(minimal)


def test_sg_hash_very_close_extra_node(minimal: SystemGraph):
    pre = hash(minimal)
    minimal.nodes["new"] = Node()
    assert pre != hash(minimal)

# Tests for model validation errors

# Tests for data validation errors


def test_load_from_dict():
    d = {
        "nodes": {
            "indicator": {"tags": {"indicator"}, "logic": {"component": "and"}},
            "x1" : {"tags": {"component"}, "logic": {"component": "and"}},
            "x2": {"tags": {"component"}, "logic": {"component": "and"}}
        },
        "edges": [
            {"src": "x1", "dst": "x2"}
        ]
    }
    sg = SystemGraph(**d)
    sg.self_validate()