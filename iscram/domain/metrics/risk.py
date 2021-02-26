import math

from iscram.domain.model import SystemGraph
from iscram.domain.metrics.cutset import find_minimal_cutsets
from iscram.domain.metrics.graph_functions import (
    probability_union, get_tree_boolean_function_lambda, fmt_prob, get_graph_dicts_from_system_graph
)


def collect_x(sg: SystemGraph):
    x = {c.identifier: c.risk for c in sg.components}
    x.update({s.identifier: 1 - s.trust for s in sg.suppliers})
    x[-1] = 0  # indicator always manually zero

    return x


def probability_any_cutset(cutsets, x):
    probability_each_cutset = map(lambda ct: math.prod([x[i] for i in ct]), cutsets)

    return probability_union(probability_each_cutset)


def risk_by_cutsets(sg: SystemGraph, x=None, ignore_suppliers=True):
    if x is None:
        x = collect_x(sg)

    cutsets = find_minimal_cutsets(sg, ignore_suppliers)

    return probability_any_cutset(cutsets, x)


def risk_by_function(sg: SystemGraph, x=None, ignore_suppliers=True):
    if x is None:
        x = collect_x(sg)

    graph, logic = get_graph_dicts_from_system_graph(sg, ignore_suppliers)
    fn = get_tree_boolean_function_lambda(-1, graph, logic, fmt_prob)

    return fn(x)