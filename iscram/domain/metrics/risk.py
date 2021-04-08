from iscram.domain.model import SystemGraph

from iscram.domain.metrics.cutset import (
    find_minimal_cutsets, probability_any_cutset
)

from iscram.domain.metrics.bdd_functions import (
    bdd_prob, build_bdd
)


def collect_x(sg: SystemGraph):
    x = {c.identifier: c.risk for c in sg.components}
    x.update({s.identifier: 1 - s.trust for s in sg.suppliers})
    x["indicator"] = 0  # indicator always manually zero
    return x


def risk_by_bdd(sg: SystemGraph, x=None, bdd_with_root=None):
    if x is None:
        x = collect_x(sg)

    if bdd_with_root is None:
        bdd, root = build_bdd(sg)
    else:
        bdd, root = bdd_with_root

    r = bdd_prob(bdd, root, x, dict())
    return r


def risk_by_cutsets(sg: SystemGraph, x=None, cutsets=None, ignore_suppliers=True):
    if x is None:
        x = collect_x(sg)

    if cutsets is None:
        cutsets = find_minimal_cutsets(sg, ignore_suppliers)

    return probability_any_cutset(cutsets, x)
