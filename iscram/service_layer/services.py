from collections import namedtuple

from iscram.domain.model import SystemGraph
from iscram.adapters.repository import AbstractRepository
from iscram.domain.metrics.risk import risk_by_bdd
from iscram.domain.metrics.bdd_functions import build_bdd
from iscram.domain.metrics.importance import (
    birnbaum_importance, birnbaum_structural_importance, fractional_importance_traits
)
from iscram.domain.metrics.scale import apply_scaling

selector = namedtuple("selector", ["key", "value"])

DEFAULT_PREFERENCES = {
    "SCALE_METRICS": "MIN_MAX",
    "RISK_SOURCE": "KNOWN"
}


def apply_prefs(user):
    prefs = DEFAULT_PREFERENCES.copy()
    prefs.update(user)
    return prefs


def get_bdd(sg: SystemGraph, repo: AbstractRepository):
    bdd_with_root = repo.get(sg, "bdd_with_root")
    if bdd_with_root is None:
        bdd_with_root = build_bdd(sg)
        repo.put(sg, "bdd_with_root", bdd_with_root)

    return bdd_with_root


def get_risk(sg: SystemGraph, repo: AbstractRepository, prefs={}):
    result = repo.get(sg, "risk")
    if result is not None:
        return result

    bdd_with_root = get_bdd(sg, repo)

    risk = risk_by_bdd(sg, bdd_with_root=bdd_with_root)
    repo.put(sg, "risk", risk)
    return risk


def get_birnbaum_structural_importances(sg: SystemGraph, repo: AbstractRepository, prefs={}):
    prefs = apply_prefs(prefs)

    result = repo.get(sg, "birnbaum_structural_importances")

    if result is None:
        bdd_with_root = get_bdd(sg, repo)
        result = birnbaum_structural_importance(sg, bdd_with_root=bdd_with_root)
        repo.put(sg, "birnbaum_structural_importances", result)

    result = apply_scaling(result, prefs["SCALE_METRICS"])

    return result


def get_birnbaum_importances(sg: SystemGraph, repo: AbstractRepository, prefs={}):
    prefs = apply_prefs(prefs)

    result = repo.get(sg, "birnbaum_importances")

    if result is None:
        bdd_with_root = get_bdd(sg, repo)
        result = birnbaum_importance(sg, bdd_with_root=bdd_with_root)
        repo.put(sg, "birnbaum_importances", result)

    result = apply_scaling(result, prefs["SCALE_METRICS"])

    return result


def get_birnbaum_importances_select(sg: SystemGraph, selector, repo: AbstractRepository, prefs={}):
    prefs = apply_prefs(prefs)

    select = []

    for n in sg.suppliers:
        attributes = {a.key: a.value for a in n.traits}
        if selector.key in attributes and attributes[selector.key] == selector.value:
            select.append(n.identifier)

    bdd_with_root = get_bdd(sg, repo)
    result = birnbaum_importance(sg, bdd_with_root=bdd_with_root, select=select)

    name = "birnbaum_importances_select_{}_{}".format(selector.key, selector.value)

    return {name: result["select"]}


def get_birnbaum_structural_importances_select(sg: SystemGraph, selector, repo: AbstractRepository, prefs={}):
    prefs = apply_prefs(prefs)

    select = []

    for n in sg.suppliers:
        attributes = {a.key: a.value for a in n.traits}
        if selector.key in attributes and attributes[selector.key] == selector.value:
            select.append(n.identifier)

    bdd_with_root = get_bdd(sg, repo)
    result = birnbaum_structural_importance(sg, bdd_with_root=bdd_with_root, select=select)

    name = "birnbaum_structural_importances_select_{}_{}".format(selector.key, selector.value)

    return {name: result["select"]}


def get_fractional_importance_traits(sg: SystemGraph, prefs={}):
    prefs = apply_prefs(prefs)

    result = fractional_importance_traits(sg)

    result = apply_scaling(result, prefs["SCALE_METRICS"])

    return  result