from typing import FrozenSet, Dict, List, Set
from hashlib import md5
from dataclasses import field
from functools import cached_property
import collections
import json

from pydantic import validator, root_validator
from pydantic.json import pydantic_encoder
from pydantic.dataclasses import dataclass

from iscram.domain.metrics.bdd_functions import build_bdd


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

    @cached_property
    def components(self):
        return set(filter(lambda n: "component" in self.nodes[n].tags, self.nodes))

    @cached_property
    def suppliers(self):
        return set(filter(lambda n: "supplier" in self.nodes[n].tags, self.nodes))

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
        return hash(self._id)

    def dict(self):
        return json.loads(json.dumps(self, default=pydantic_encoder))

    @cached_property
    def _id(self) -> str:
        message = ""
        for key in sorted(self.nodes.keys()):
            message += (key + self.nodes[key].get_id())
        for e in sorted(self.edges, key=lambda ed: (ed.src, ed.dst)):
            message += e.get_id()
        message_hash = md5(message.encode('utf-8'))
        return message_hash.hexdigest()

    def get_id(self):
        return self._id

    @cached_property
    def _bdd_with_root(self):
        return build_bdd(self)

    def get_bdd_with_root(self):
        return self._bdd_with_root

    @cached_property
    def supplier_groups(self) -> Dict[str, Set[str]]:
        """ Returns {root_node: descendants including self} """

        # Every valid supplier graph is a set of rooted, directed graphs where each node is a supplier.
        # A supplier group is a set of nodes reachable from a root in the supplier graph.

        supplier_graph = {}
        supplier_set = set(filter(lambda n: "supplier" in self.nodes[n].tags, self.nodes))
        for e in self.edges:
            if e.src in supplier_set and e.dst in supplier_set:
                supplier_graph[e.src] = supplier_graph.get(e.src, []) + [e.dst]

        in_degrees = {}
        for node, adjs in supplier_graph.items():
            for adj in adjs:
                in_degrees[adj] = in_degrees.get(adj, 0) + 1
        roots = [r for r in filter(lambda n: in_degrees.get(n, 0) == 0, supplier_set)]
        if not roots:
            return {}
        groups = {r: set() for r in roots}

        for r in roots:
            queue = collections.deque([r])
            visited = set()
            while queue:
                u = queue.pop()
                if u in visited:
                    return {}
                visited.add(u)
                queue.extend(supplier_graph.get(u, []))
            groups[r] = visited

        return groups

    def with_suppliers(self, new_edges: List[Edge]):
        """ Returns a copy of this graph but using the provided suppliers. """
        # Nodes: All nodes, with "potential" added to tags of nodes with a potential out-edge
        # Edges: All component srced edges are unchanged
        #        All supplier-supplier edges are unchanged
        #        S-C edges in new_edges are included with no tags
        #        S-C edges in self but not in new_edges are included with tag "potential"
        edges = set(new_edges)
        chosen_suppliers = set()
        for e in edges:
            if e.src in self.suppliers:
                chosen_suppliers.add(e.src)

        # @TODO: graph search for all paths to supplier; this affects tagging these intermediaries as not potential
        # simple addition of involved group leaders
        for group, members in self.supplier_groups.items():
            for member in members:
                if member in chosen_suppliers:
                    chosen_suppliers.add(group)

        potential_suppliers = set(self.suppliers) - chosen_suppliers
        for e in self.edges:
            if e.src in self.components:
                edges.add(e)
            elif e.src in chosen_suppliers and e.dst in chosen_suppliers:
                edges.add(Edge(src=e.src, dst=e.dst))
            elif Edge(src=e.src, dst=e.dst) not in edges:
                edges.add(Edge(src=e.src, dst=e.dst, tags=frozenset(["potential"])))

        new_nodes = self.nodes.copy()

        for n_id in potential_suppliers:
            n = self.nodes[n_id]
            new_node = Node(logic=n.logic, tags=frozenset(list(n.tags) + ["potential"]))
            new_nodes[n_id] = new_node

        for n_id in chosen_suppliers:
            n = self.nodes[n_id]
            tags = set(n.tags)
            if "potential" in tags:
                tags.remove("potential")
            new_node = Node(logic=n.logic, tags=tags)
            new_nodes[n_id] = new_node

        return SystemGraph(nodes=new_nodes, edges=edges)


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


