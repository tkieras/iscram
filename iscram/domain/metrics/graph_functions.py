import math
from itertools import combinations

from iscram.domain.model import SystemGraph


fmt_logic = {"lambda": "lambda x: {}",
             "and": "all",
             "or": "any",
             "begin": "([",
             "end": "])",
             "x": "x[{}]",
             "sep": ", "}

fmt_prob = {"lambda": "lambda x: {}",
            "and": "math.prod",
            "or": "probability_union",
            "begin": "([",
            "end": "])",
            "x": "x[{}]",
            "sep": ", "}


class TreeError(RuntimeError):
    pass


def probability_union(x):
    return 1 - math.prod(map(lambda z: 1 - z, x))


def recursive_build_tree_boolean_function_string(n, graph, logic, fmt):
    base = (fmt["or"] + fmt["begin"] + fmt["x"]).format(n)

    children = graph.get(n, [])

    if len(children) == 0:
        return base + fmt["end"]

    child_str = fmt[logic[n]] + fmt["begin"]

    for child in children:
        child_str += recursive_build_tree_boolean_function_string(child, graph, logic, fmt)
        child_str += fmt["sep"]

    child_str += fmt["end"]

    return base + fmt["sep"] + child_str + fmt["end"]


def get_tree_boolean_function_lambda(n, graph, logic, fmt=None):
    if fmt is None:
        fmt = fmt_logic
    fn_str = (fmt["lambda"]).format(recursive_build_tree_boolean_function_string(n, graph, logic, fmt))
    return eval(fn_str)


def is_tree(graph, root) -> bool:
    nodes = set()
    edges = set()

    for node in graph:
        nodes.add(node)
        children = graph.get(node, [])
        for child in children:
            nodes.add(child)
            edges.add((node, child))

    if len(nodes) != len(edges) + 1:
        return False

    visited = set()
    queue = [root]

    while queue:
        v = queue.pop(0)
        visited.add(v)
        children = graph.get(v, [])
        for child in children:
            queue.append(child)

    return len(visited) == len(nodes)


def convert_system_graph_to_tree(sg: SystemGraph, ignore_suppliers):
    logic = {-1: sg.indicator.logic_function}

    for c in sg.components:
        logic[c.identifier] = c.logic_function

    graph = {-1: set([d.risk_src_id for d in sg.indicator.dependencies])}

    for d in sg.security_dependencies:
        # all dependencies can be added b/c without 'offerings' as links to suppliers,
        # recursion will not reach to supplier nodes.
        adj = graph.get(d.risk_dst_id, set())
        adj.add(d.risk_src_id)
        graph[d.risk_dst_id] = adj

    if not ignore_suppliers:
        for s in sg.suppliers:
            logic[s.identifier] = "and"

        for o in sg.offerings:
            adj = graph.get(o.component_id, set())
            adj.add(o.supplier_id)
            graph[o.component_id] = adj

    if not is_tree(graph, -1):
        raise TreeError

    return graph, logic


def enumerate_all_combinations(x):
    n = len(x)

    for i in range(n+1):
        yield from combinations(x, i)
