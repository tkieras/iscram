from iscram.domain.model import SystemGraph

from iscram.domain.metrics.cutset import (
    find_minimal_cutsets, probability_any_cutset
)

from iscram.domain.metrics.bdd_functions import (
    bdd_prob, build_bdd
)


def risk_by_bdd(sg: SystemGraph, p, bdd_with_root=None):
    if bdd_with_root is None:
        bdd, root = build_bdd(sg)
    else:
        bdd, root = bdd_with_root

    r = bdd_prob(bdd, root, p, dict())
    return r


def risk_by_cutsets(sg: SystemGraph, p, cutsets=None, ignore_suppliers=True):
    if cutsets is None:
        cutsets = find_minimal_cutsets(sg, ignore_suppliers)

    return probability_any_cutset(cutsets, p)
