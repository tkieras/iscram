import math
from itertools import combinations

from iscram.domain.model import SystemGraph


fmt_logic = {"lambda": "lambda x: {}",
             "and": "all",
             "or": "any",
             "begin": "([",
             "end": "])",
             "x": "x[\"{}\"]",
             "sep": ", "}

fmt_prob = {"lambda": "lambda x: {}",
            "and": "math.prod",
            "or": "probability_union",
            "begin": "([",
            "end": "])",
            "x": "x[\"{}\"]",
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


def prep_for_mocus(sg: SystemGraph, ignore_suppliers):
    # note, test cases all pass after combining the "@main" node with the basic event node.
    # original @main code in comments

    logic = {"indicator": sg.indicator.logic_function}

    sg_suppliers = set([s.identifier for s in sg.suppliers])

    for c in sg.components:
        logic["@deps_"+c.identifier] = c.logic_function
        logic[c.identifier] = "or"
        #logic["@main_"+c.identifier] = "or"
        #logic[c.identifier] = "and"

    #graph = {"indicator": set(["@main_"+d.risk_src_id for d in sg.indicator.dependencies])}
    graph = {"indicator": set([d.risk_src_id for d in sg.indicator.dependencies])}

    for d in sg.security_dependencies:
        src_is_supplier = d.risk_src_id in sg_suppliers
        dst_is_supplier = d.risk_dst_id in sg_suppliers

        if dst_is_supplier:
            dst_name = d.risk_dst_id
        else:
            dst_name = "@deps_" + d.risk_dst_id

        if src_is_supplier:
            src_name = d.risk_src_id
        else:
            src_name = d.risk_src_id
            #src_name = "@main_" + d.risk_src_id

        if src_is_supplier and not dst_is_supplier:
            #dst_name = "@main_" + d.risk_dst_id
            dst_name = d.risk_dst_id

        if ignore_suppliers and (src_is_supplier or dst_is_supplier):
            pass
        else:
            adj = graph.get(dst_name, set())
            adj.add(src_name)
            graph[dst_name] = adj

    for c in sg.components:
       # adj = graph.get("@main_"+c.identifier, set())
        adj = graph.get(c.identifier, set())
        #adj.add(c.identifier)
        adj.add("@deps_"+c.identifier)
        #graph["@main_"+c.identifier] = adj
        graph[c.identifier] = adj

    if not ignore_suppliers:
        for s in sg.suppliers:
            logic[s.identifier] = "and"

    return graph, logic


def enumerate_all_combinations(x):
    n = len(x)

    for i in range(n+1):
        yield from combinations(x, i)
