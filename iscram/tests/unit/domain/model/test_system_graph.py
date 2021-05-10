import copy
import pytest

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
            "x1": {"tags": {"component"}, "logic": {"component": "and"}},
            "x2": {"tags": {"component"}, "logic": {"component": "and"}}
        },
        "edges": [
            {"src": "x1", "dst": "x2"}
        ]
    }
    sg = SystemGraph(**d)
    assert sg is not None


def test_supplier_groups_full(full_example_system: SystemGraph):
    groups = full_example_system.supplier_groups
    keys = {"x16", "x17", "x18", "x19", "x20", "x21", "x22", "x23", "x24", "x25", "x26", "x27", "x28", "x29", "x30"}

    assert set(groups.keys()) == keys
    for key, value in groups.items():
        assert value == {key}


def test_supplier_groups_basic():
    nodes = ["x1", "x2", "x3", "x4", "x5", "x6"]
    edges = [("x1", "x2"), ("x2", "x3"), ("x4", "x5"), ("x4", "x6")]

    nodes = {n: Node(logic=dict(), tags=frozenset(["supplier"])) for n in nodes}
    nodes.update({"indicator": Node(tags=frozenset(["indicator"]))})
    sg = SystemGraph(nodes=nodes,
                     edges=[Edge(src=s, dst=d) for s, d in edges])

    expected = {
        "x1": {"x1", "x2", "x3"},
        "x4": {"x4", "x5", "x6"}
    }

    assert sg.supplier_groups == expected


def test_supplier_groups_monogroup():
    nodes = ["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"]
    edges = [("x1", "x2"), ("x2", "x3"), ("x4", "x5"), ("x4", "x6"), ("x9", "x1"), ("x9", "x4"), ("x9", "x7"),
             ("x7", "x8")]

    nodes = {n: Node(logic=dict(), tags=frozenset(["supplier"])) for n in nodes}
    nodes.update({"indicator": Node(tags=frozenset(["indicator"]))})
    sg = SystemGraph(nodes=nodes,
                     edges=[Edge(src=s, dst=d) for s, d in edges])

    expected = {
        "x9": {"x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"}
    }

    assert sg.supplier_groups == expected


def test_supplier_groups_long_chain():
    nodes = ["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"]
    edges = [("x1", "x2"), ("x2", "x3"), ("x3", "x4"), ("x4", "x5"),
             ("x5", "x6"), ("x6", "x7"), ("x7", "x8"), ("x8", "x9")]

    nodes = {n: Node(logic=dict(), tags=frozenset(["supplier"])) for n in nodes}
    nodes.update({"indicator": Node(tags=frozenset(["indicator"]))})
    sg = SystemGraph(nodes=nodes,
                     edges=[Edge(src=s, dst=d) for s, d in edges])

    expected = {
        "x1": {"x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"}
    }

    assert sg.supplier_groups == expected


def test_supplier_groups_long_chain_reversed():
    nodes = reversed(["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"])
    edges = [("x1", "x2"), ("x2", "x3"), ("x3", "x4"), ("x4", "x5"),
             ("x5", "x6"), ("x6", "x7"), ("x7", "x8"), ("x8", "x9")]

    nodes = {n: Node(logic=dict(), tags=frozenset(["supplier"])) for n in nodes}
    nodes.update({"indicator": Node(tags=frozenset(["indicator"]))})
    sg = SystemGraph(nodes=nodes,
                     edges=[Edge(src=s, dst=d) for s, d in edges])

    expected = {
        "x1": {"x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"}
    }

    assert sg.supplier_groups == expected


def test_supplier_groups_inner_cycle():
    nodes = ["x1", "x2", "x3"]
    edges = [("x1", "x2"), ("x2", "x3"), ("x3", "x2")]

    nodes = {n: Node(logic=dict(), tags=frozenset(["supplier"])) for n in nodes}
    nodes.update({"indicator": Node(tags=frozenset(["indicator"]))})
    sg = SystemGraph(nodes=nodes,
                     edges=[Edge(src=s, dst=d) for s, d in edges])

    assert len(sg.supplier_groups) == 0


def test_supplier_groups_outer_cycle():
    nodes = ["x1", "x2", "x3", "x4", "x5", "x6"]
    edges = [("x1", "x2"), ("x2", "x3"), ("x3", "x4"), ("x4", "x5"), ("x4", "x6"), ("x6", "x1")]

    nodes = {n: Node(logic=dict(), tags=frozenset(["supplier"])) for n in nodes}
    nodes.update({"indicator": Node(tags=frozenset(["indicator"]))})
    sg = SystemGraph(nodes=nodes,
                     edges=[Edge(src=s, dst=d) for s, d in edges])

    assert len(sg.supplier_groups) == 0


def test_with_edges(full_example_system: SystemGraph):
    new_edges = [("x29", "x1"), ("x28", "x2"), ("x27", "x3"), ("x26", "x4"), ("x25", "x5"), ("x24", "x6"),
                 ("x23", "x7"), ("x22", "x8"), ("x21", "x9"), ("x20", "x10"), ("x19", "x11"), ("x18", "x12"),
                 ("x17", "x13"), ("x16", "x14"), ("x18", "x15")]

    new_sg = full_example_system.with_suppliers([Edge(src=s, dst=d) for s, d in new_edges])

    updated_edges = set(new_sg.edges)
    for s, d in new_edges:
        assert(Edge(src=s, dst=d) in updated_edges)

    removed_edges = [("x16", "x1"), ("x17", "x2"), ("x25", "x3"), ("x19", "x4"), ("x20", "x5"), ("x21", "x6"),
                     ("x22", "x7"), ("x23", "x8"), ("x24", "x10"), ("x25", "x9"), ("x26", "x11"), ("x27", "x12"),
                     ("x26", "x11"), ("x27", "x12"), ("x28", "x13"), ("x29", "x14"), ("x29", "x15")]

    for rs, rd in removed_edges:
        assert(Edge(src=rs, dst=rd, tags=frozenset(["potential"])) in updated_edges)


def test_dict_nested_success(canonical: SystemGraph):
    d = canonical.dict()
    assert "nodes" in d and "edges" in d
    assert "x1" in d["nodes"] and d["nodes"]["x1"]["tags"] is not None
