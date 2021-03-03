import math
from collections import defaultdict

from iscram.domain.model import SystemGraph
from iscram.domain.metrics.cutset import find_minimal_cutsets
from iscram.domain.metrics.graph_functions import (
    probability_union, get_tree_boolean_function_lambda, fmt_prob, prep_for_mocus
)


def collect_x(sg: SystemGraph):
    x = {c.identifier: c.risk for c in sg.components}
    x.update({s.identifier: 1 - s.trust for s in sg.suppliers})
    x["indicator"] = 0  # indicator always manually zero

    return x


def probability_any_cutset(cutsets, x):
    probability_each_cutset = map(lambda ct: math.prod([x[i] for i in ct]), cutsets)

    return probability_union(probability_each_cutset)


def risk_by_cutsets(sg: SystemGraph, x=None, cutsets=None, ignore_suppliers=True):
    if x is None:
        x = collect_x(sg)

    if cutsets is None:
        cutsets = find_minimal_cutsets(sg, ignore_suppliers)

    return probability_any_cutset(cutsets, x)


def risk_by_function(sg: SystemGraph, x=None, ignore_suppliers=True):
    if x is None:
        x = defaultdict(lambda: False)
        y = collect_x(sg)
        x.update(y)

    graph, logic = prep_for_mocus(sg, ignore_suppliers)
    fn = get_tree_boolean_function_lambda("indicator", graph, logic, fmt_prob)

    return fn(x)