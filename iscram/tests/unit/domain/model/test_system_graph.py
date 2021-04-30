import copy

from iscram.domain.model import (
    Node, Edge, SystemGraph, validate_data
)


def test_minimal(minimal: SystemGraph):
    # makes sure validator has run
    assert minimal is not None


def test_diamond(diamond: SystemGraph):
    # makes sure validator has run
    assert diamond is not None


def test_diamond_suppliers(diamond_suppliers: SystemGraph):
    # makes sure validator has run
    assert diamond_suppliers is not None


# Tests for System Graph Hashing
def test_sg_hashable(minimal: SystemGraph):
    assert hash(minimal)


def test_sg_hash_very_different(minimal: SystemGraph, diamond: SystemGraph):
    assert hash(minimal) != hash(diamond)


def test_sg_hash_same(minimal: SystemGraph):
    other = copy.deepcopy(minimal)
    pre = hash(minimal)
    assert pre == hash(other)


def test_sg_hash_very_close_node_missing(minimal: SystemGraph):
    other = copy.deepcopy(minimal)
    pre = hash(minimal)
    del other.nodes["x1"]
    assert pre != hash(other)


def test_sg_hash_very_close_extra_node(minimal: SystemGraph):
    other = copy.deepcopy(minimal)
    pre = hash(minimal)
    other.nodes["new"] = Node()
    assert pre != hash(other)

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
    assert sg is not None
