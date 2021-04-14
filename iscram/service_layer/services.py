from typing import Dict

from iscram.domain.model import SystemGraph
from iscram.adapters.repository import AbstractRepository
from iscram.domain.metrics.risk import risk_by_bdd
from iscram.domain.metrics.bdd_functions import build_bdd
from iscram.domain.metrics.importance import (
    birnbaum_importance, birnbaum_structural_importance, fractional_importance_of_attributes
)
from iscram.domain.metrics.probability_providers import (
    provide_p_unknown_data, provide_p_direct_from_data
)
from iscram.domain.metrics.scale import apply_scaling


DEFAULT_PREFERENCES = {
    "SCALE_METRICS": "MIN_MAX",
    "RISK_SOURCE": "KNOWN"
}


def apply_prefs(user_prefs):
    prefs = DEFAULT_PREFERENCES.copy()
    if user_prefs is None:
        return prefs
    else:
        prefs.update(user_prefs)
    return prefs


def get_bdd(sg: SystemGraph, repo: AbstractRepository):
    bdd_with_root = repo.get(sg, "bdd_with_root")
    if bdd_with_root is None:
        bdd_with_root = build_bdd(sg)
        repo.put(sg, "bdd_with_root", bdd_with_root)

    return bdd_with_root


def get_risk(sg: SystemGraph, repo: AbstractRepository, data: Dict, prefs=None) -> float:
    bdd_with_root = get_bdd(sg, repo)
    p = provide_p_direct_from_data(sg, data)
    risk = risk_by_bdd(sg, p, bdd_with_root=bdd_with_root)
    return risk


def get_birnbaum_structural_importances(sg: SystemGraph, repo: AbstractRepository, data=None, prefs=None) -> Dict[str, float]:
    prefs = apply_prefs(prefs)
    bdd_with_root = get_bdd(sg, repo)
    result = birnbaum_structural_importance(sg, bdd_with_root=bdd_with_root)
    return apply_scaling(result, prefs["SCALE_METRICS"])


def get_birnbaum_importances(sg: SystemGraph, repo: AbstractRepository, data: Dict, prefs=None) -> Dict[str, float]:
    prefs = apply_prefs(prefs)
    bdd_with_root = get_bdd(sg, repo)
    p = provide_p_direct_from_data(sg, data)
    result = birnbaum_importance(sg, p, bdd_with_root=bdd_with_root)
    return apply_scaling(result, prefs["SCALE_METRICS"])


def get_birnbaum_importances_select(sg: SystemGraph, selector: Dict, repo: AbstractRepository, data: Dict, prefs=None) -> Dict[str, float]:
    prefs = apply_prefs(prefs)

    select_key = list(selector.keys())
    if len(select_key) != 1:
        return {}
    select_key = select_key[0]
    select_value = selector[select_key]
    select = []

    for node, node_data in data["nodes"].items():
        if "attributes" not in node_data:
            continue
        attrs = node_data["attributes"]

        if select_key in attrs and attrs[select_key] == select_value:
            select.append(node)

    bdd_with_root = get_bdd(sg, repo)
    p = provide_p_direct_from_data(sg, data)
    result = birnbaum_importance(sg, p, bdd_with_root=bdd_with_root, select=select)

    name = "birnbaum_importances_select_{}_{}".format(select_key, select_value)

    return {name: result["select"]}


def get_birnbaum_structural_importances_select(sg: SystemGraph, selector, repo: AbstractRepository, data: Dict, prefs=None) -> Dict[str, float]:
    prefs = apply_prefs(prefs)

    select = []

    for node, node_data in data["nodes"].items():
        if "attributes" in node_data:
            attributes = {a.key: a.value for a in node_data["attributes"]}
            if selector.key in attributes and attributes[selector.key] == selector.value:
                select.append(node)

    bdd_with_root = get_bdd(sg, repo)
    result = birnbaum_structural_importance(sg, bdd_with_root=bdd_with_root, select=select)

    name = "birnbaum_importances_select_{}_{}".format(selector.key, selector.value)

    return {name: result["select"]}


def get_fractional_importance_traits(sg: SystemGraph, data: Dict, prefs=None) -> Dict[str, float]:
    prefs = apply_prefs(prefs)
    result = fractional_importance_of_attributes(sg, data)
    result = {"{}_{}".format(key[0], key[1]) : value for key, value in result.items()}
    return apply_scaling(result, prefs["SCALE_METRICS"])
