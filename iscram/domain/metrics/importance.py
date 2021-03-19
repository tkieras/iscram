from iscram.domain.model import SystemGraph
from iscram.domain.metrics.cutset import find_minimal_cutsets
from iscram.domain.metrics.risk import (
    probability_any_cutset, collect_x
)


def birnbaum_structural_importance(sg: SystemGraph, ignore_suppliers=False):
    all_ids = {c.identifier for c in sg.components}
    all_ids.update({s.identifier for s in sg.suppliers})

    x = {i: 0.5 for i in all_ids}
    x["indicator"] = 0  # indicator, manual, should always be zero

    return birnbaum_importance(sg, x, ignore_suppliers)


def birnbaum_importance(sg: SystemGraph, x=None, ignore_suppliers=False):
    b_imps = {}
    cutsets = find_minimal_cutsets(sg, ignore_suppliers)
    all_ids = {c.identifier for c in sg.components}
    all_ids.update({s.identifier for s in sg.suppliers})

    if x is None:
        x = collect_x(sg)

    for i in all_ids:
        saved = x[i]
        x[i] = 1.0
        risk_top = probability_any_cutset(cutsets, x)
        x[i] = 0.0
        risk_bottom = probability_any_cutset(cutsets, x)
        b_imps[i] = risk_top - risk_bottom
        x[i] = saved  # restore to initial state

    return b_imps
