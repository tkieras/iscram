from typing import FrozenSet, List, Set, Dict
from collections import deque

import math

from iscram.domain.model import SystemGraph
from iscram.domain.metrics.bdd_functions import build_bdd


def prep_for_mocus(sg: SystemGraph, ignore_suppliers):
    """ Combines parts of a SystemGraph into a unified graph with added gate nodes needed for the MOCUS algorithm.
    The added gate nodes are marked with @deps. Each node becomes an or gate with an added gate as a child. The
    resulting graph must have component children pointing to @deps, and each node's supplier pointing to itself. """

    logic = {"indicator": sg.nodes["indicator"].logic["component"]}

    sg_suppliers = set()
    sg_components = set()
    for node, data in sg.nodes.items():
        if "supplier" in data.tags:
            sg_suppliers.add(node)
        elif "component" in data.tags:
            sg_components.add(node)

    for c in sg_components:
        logic["@deps_" + c] = sg.nodes[c].logic["component"]
        logic[c] = "or"

    graph = {"indicator": set(map(lambda edge: edge.src, filter(lambda edge: edge.dst == "indicator", sg.edges)))}

    for e in sg.edges:
        if "potential" in e.tags:
            continue
        src_is_supplier = e.src in sg_suppliers
        dst_is_supplier = e.dst in sg_suppliers

        if dst_is_supplier:
            dst_name = e.dst
        else:
            dst_name = "@deps_" + e.dst

        if src_is_supplier:
            src_name = e.src
        else:
            src_name = e.src

        if src_is_supplier and not dst_is_supplier:
            dst_name = e.dst

        if ignore_suppliers and (src_is_supplier or dst_is_supplier):
            pass
        else:
            adj = graph.get(dst_name, set())
            adj.add(src_name)
            graph[dst_name] = adj

    for c in sg_components:
        adj = graph.get(c, set())
        adj.add("@deps_" + c)
        graph[c] = adj

    if not ignore_suppliers:
        for s in sg_suppliers:
            logic[s] = "and"

    return graph, logic


def find_minimal_cutsets(sg: SystemGraph, ignore_suppliers=False) -> FrozenSet[FrozenSet[str]]:
    return mocus(sg, ignore_suppliers)


def mocus(sg: SystemGraph, ignore_suppliers=False) -> FrozenSet[FrozenSet[str]]:
    """ Inefficient implementation of MOCUS.
    Gates are added to connect suppliers and components and their dependencies.
    Minimal cutsets including these gates can safely be deleted since the probability of gate failure is zero.
    This function and the use of cutsets in general is deprecated in favor of BDD based functions.
    """

    graph, logic = prep_for_mocus(sg, ignore_suppliers)

    working_result = iterative_mocus("indicator", graph, logic)

    working_result = minimize_cutsets([frozenset(cutset) for cutset in working_result])

    working_result = remove_fictive_gate_cutsets(working_result)

    return frozenset(working_result)


def iterative_mocus(n: str, graph: Dict, logic: Dict) -> List[Set]:
    queue = deque([n])
    root_cutset = {"indicator"}
    cutsets = [root_cutset]

    while queue:
        v = queue.pop()
        children = graph.get(v, None)

        if not children or len(children) == 0:
            continue

        v_involved = list(filter(lambda ct: v in ct, cutsets))
        tmp = []

        if logic[v] == "and":
            for cutset in v_involved:
                new_cutset = cutset.copy()
                new_cutset.remove(v)
                for c in children:
                    new_cutset.add(c)
                tmp.append(new_cutset)
        elif logic[v] == "or":
            for cutset in v_involved:
                for c in children:
                    new_cutset = cutset.copy()
                    new_cutset.remove(v)
                    new_cutset.add(c)
                    tmp.append(new_cutset)

        cutsets.extend(tmp)

        for c in children:
            queue.appendleft(c)

    cutsets.remove({"indicator"})
    return cutsets


def is_fictive(node):
    return node[0] == "@"


def remove_fictive_gate_cutsets(cutsets: Set[FrozenSet]) -> Set[FrozenSet]:
    def no_fictive(cutset):
        return not any([is_fictive(node) for node in cutset])

    return set(filter(no_fictive, cutsets))


def probability_union(x):
    return 1 - math.prod(map(lambda z: 1 - z, x))


def probability_any_cutset(cutsets, x):
    probability_each_cutset = map(lambda ct: math.prod([x[i] for i in ct]), cutsets)
    return probability_union(probability_each_cutset)


def minimize_cutsets(cutsets: List[FrozenSet]):
    """ Inefficient method used for testing. Assumes all in cutsets are valid but some are not minimal."""

    cutsets.sort(key=lambda c: len(c))
    results = set()

    for c in cutsets:
        minimal = True
        for x in results:
            if x.issubset(c):
                minimal = False
                break
        if minimal:
            results.add(c)

    return results


def brute_force_bdd_cutsets(sg: SystemGraph):
    """ Using a BDD all solutions are returned. Then they are minimized.
    This is very inefficient even on small graphs and used only for testing other algorithms.
    """
    bdd, root = build_bdd(sg)
    cutsets = list()

    for s in bdd.pick_iter(root):
        cutsets.append(frozenset(filter(lambda u: s[u] is True, s.keys())))

    min_cutsets = minimize_cutsets(cutsets)
    min_cutsets.remove(frozenset(["indicator"]))
    return frozenset(min_cutsets)

