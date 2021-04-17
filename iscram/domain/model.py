from typing import FrozenSet, Dict, List
from hashlib import md5
from dataclasses import field

from pydantic import validator, root_validator
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
    def __init__(self, message):
        self.message = message


class DataValidationError(Exception):
    def __init__(self, message):
        self.message = message


@dataclass(frozen=True)
class Node:
    logic: Dict = field(default_factory=dict)
    tags: FrozenSet[str] = field(default_factory=frozenset)

    @validator('logic', each_item=True)
    def logic_valid_functions(cls, v):
        if not validate_logic_function(v):
            raise ValueError("Invalid logic function: {}".format(v))
        return v

    @root_validator()
    def logic_tag_match(cls, values):
        if "tags" not in values or "logic" not in values:
            return values

        if "component" in values["tags"] and "component" not in values["logic"]:
            raise ValueError("Tag 'component' found in tags but not in logic.")
        return values

    def __hash__(self):
        return hash(self.get_id())

    def get_id(self):
        message = ""
        for key in sorted(self.logic.keys()):
            message += (key + self.logic[key])
        for t in sorted(self.tags):
            message += t
        message_hash = md5(message.encode('utf-8'))
        return message_hash.hexdigest()


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    tags: FrozenSet[str] = field(default_factory=frozenset)

    @validator('src')
    def src_must_be_valid_name(cls, v):
        if not validate_identifier(v):
            raise ValueError(f"{v} not a valid name.")
        return v

    @validator('dst')
    def dst_must_be_valid_name(cls, v):
        if not validate_identifier(v):
            raise ValueError(f"{v} not a valid name.")
        return v

    def get_id(self) -> str:
        message = self.src + self.dst
        for t in sorted(self.tags):
            message += t
        message_hash = md5(message.encode('utf-8'))
        return message_hash.hexdigest()

    def __hash__(self):
        return hash(self.get_id())


@dataclass(frozen=True)
class SystemGraph:
    nodes: Dict[str, Node]
    edges: List[Edge]

    @validator('nodes')
    def node_valid(cls, v):
        # Keys must be valid identifiers
        # Names must be unique
        # (Currently) One name must be 'identifier'
        invalid = []
        unique = set()
        for key in v:
            if not validate_identifier(key):
                invalid.append(key)
            if key in unique:
                raise ValueError("Node name is not unique: {}".format(key))
            unique.add(key)

        if len(invalid) > 0:
            raise ValueError("Invalid name(s): {}".format(invalid))

        if 'indicator' not in unique or "indicator" not in v["indicator"].tags:
            raise ValueError("One node must be named 'indicator' and must have 'indicator' as tag.")

        return v

    @validator('edges')
    def edges_must_refer_to_nodes(cls, v, values):
        if "nodes" not in values:
            return v

        for edge in v:
            if edge.src not in values["nodes"] or edge.dst not in values["nodes"]:
                raise ValueError("Edge src node or dst node does not exist: {}".format(edge))
        return v

    def __hash__(self):
        return hash(self.get_id())

    def get_id(self) -> str:
        message = ""
        for key in sorted(self.nodes.keys()):
            message += (key + self.nodes[key].get_id())
        for e in sorted(self.edges, key=lambda ed: (ed.src, ed.dst)):
            message += e.get_id()
        message_hash = md5(message.encode('utf-8'))
        return message_hash.hexdigest()




def validate_data(sg: SystemGraph, data: Dict) -> None:
    """ A data dictionary is valid only for a particular SystemGraph """

    # If node data is given, it must be valid and correspond to this System Graph
    if "nodes" in data:
        for key, value in data["nodes"].items():
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


