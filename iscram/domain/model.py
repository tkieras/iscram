from typing import FrozenSet, Dict, List
from dataclasses import field

from pydantic.dataclasses import dataclass


def validate_identifier(identifier: str) -> bool:
    if len(identifier) == 0:
        return False
    return identifier[0].isalpha()


def validate_logic_function(logic_function: str) -> bool:
    return logic_function in ["and", "or"]


def validate_risk(risk: float) -> bool:
    return 0.0 <= risk <= 1.0


def validate_cost(cost: int) -> bool:
    return cost >= 0


class ModelValidationError(Exception):
    pass


class DataValidationError(Exception):
    pass


@dataclass(frozen=True)
class Node:
    logic: Dict = field(default_factory=dict)
    tags: FrozenSet[str] = field(default_factory=frozenset)

    def __hash__(self):
        return hash((self.tags, frozenset([(k, v) for k, v in self.logic.items()])))

    def __str__(self):
        return "{} {}".format(self.tags, self.logic)

    def self_validate(self) -> None:
        for key, value in self.logic.items():
            if not validate_logic_function(value):
                raise ModelValidationError("Invalid logic value in node: {}".format(self))
        if "component" in self.tags and "component" not in self.logic:
            raise ModelValidationError("Missing component logic function for node: {}".format(self))
        if not ("component" in self.tags or "supplier" in self.tags or "indicator" in self.tags):
            raise ModelValidationError("Missing tag (component/supplier/indicator) for node: {}".format(self))
        if "component" in self.tags and "supplier" in self.tags:
            raise ModelValidationError("A node is marked as both supplier and component: {}".format(self))


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    tags: FrozenSet[str] = field(default_factory=frozenset)

    def __str__(self):
        return "{} {} {}".format(self.src, self.dst, self.tags)


@dataclass(frozen=True)
class SystemGraph:
    nodes: Dict[str, Node]
    edges: List[Edge]

    def __hash__(self):
        node_hash = hash(frozenset((k,v) for k,v in self.nodes.items()))
        edge_hash = hash(frozenset(self.edges))
        return node_hash * 37 + edge_hash

    def self_validate(self) -> None:
        system_names = set()
        roots = 0
        for name, node in self.nodes.items():
            node.self_validate()
            if not validate_identifier(name):
                raise ModelValidationError("Invalid name in node: {} {}".format(name, node))
            if name in system_names:
                raise ModelValidationError("Name of node is used more than once: {}".format(name))
            system_names.add(name)
            roots += ("indicator" in node.tags)
        if roots != 1:
            raise ModelValidationError("Exactly one node must be tagged with 'indicator'.")
        for edge in self.edges:
            if edge.src not in self.nodes or edge.dst not in self.nodes:
                raise ModelValidationError("Could not find src or dst of edge: {}".format(edge))


def validate_data(sg: SystemGraph, data: Dict) -> None:
    """ A data dictionary is valid only for a particular SystemGraph """

    # If node data is given, it must be valid and correspond to this System Graph
    if "nodes" in data:
        for key, value in data["nodes"]:
            if key not in sg.nodes:
                raise DataValidationError("Node name not in System Graph: {}".format(key))
            if "risk" in value and not validate_risk(value["risk"]):
                raise DataValidationError("Risk data is invalid for node: {} {}".format(key, value))

    # If edges are described in data dict, edge data must be valid for this System Graph
    if "edges" in data:
        for edge in data["edges"]:
            if "src" not in edge or "dst" not in edge:
                raise DataValidationError("Edge data missing src or dst field: {}".format(edge))
            if edge["src"] not in sg.nodes or edge["dst"] not in sg.nodes:
                raise DataValidationError("Could not find src or dst of edge: {}".format(edge))
            if "risk" in edge and not validate_risk(edge["risk"]):
                raise DataValidationError("Risk is not valid for edge: {}".format(edge))
            if "cost" in edge and not validate_cost(edge["cost"]):
                raise DataValidationError("Cost is not valid for edge: {}".format(edge))


