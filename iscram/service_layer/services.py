from typing import Dict

from iscram.domain.model import SystemGraph, validate_data
from iscram.domain.optimization import SupplierChoiceProblem
from iscram.adapters.repository import AbstractRepository
from iscram.domain.metrics.risk import risk_by_bdd
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


def get_system_graph(sg_id: str, repo: AbstractRepository) -> SystemGraph:
    return repo.get(sg_id)


def put_system_graph(sg: SystemGraph, repo: AbstractRepository):
    repo.put(sg)


def get_risk(sg: SystemGraph, data: Dict, prefs=None) -> Dict[str, float]:
    bdd_with_root = sg.get_bdd_with_root()
    validate_data(sg, data)
    p = provide_p_direct_from_data(sg, data)
    risk = risk_by_bdd(sg, p, bdd_with_root=bdd_with_root)
    return {"system" : risk}


def get_birnbaum_structural_importances(sg: SystemGraph, data=None, prefs=None) -> Dict[str, float]:
    prefs = apply_prefs(prefs)
    bdd_with_root = sg.get_bdd_with_root()
    result = birnbaum_structural_importance(sg, bdd_with_root=bdd_with_root)
    return apply_scaling(result, prefs["SCALE_METRICS"])


def get_birnbaum_importances(sg: SystemGraph, data: Dict, data_src: str, prefs=None) -> Dict[str, float]:
    prefs = apply_prefs(prefs)
    bdd_with_root = sg.get_bdd_with_root()
    if data_src == "data":
        p = provide_p_direct_from_data(sg, data)
    else:
        p = provide_p_unknown_data(sg)

    result = birnbaum_importance(sg, p, bdd_with_root=bdd_with_root)
    return apply_scaling(result, prefs["SCALE_METRICS"])


def get_birnbaum_importances_select(sg: SystemGraph, data: Dict, selector: Dict, data_src: str, prefs=None) -> Dict[str, Dict[bool, float]]:
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

    bdd_with_root = sg.get_bdd_with_root()
    if data_src == "data":
        p = provide_p_direct_from_data(sg, data)
    else:
        p = provide_p_unknown_data(sg)
    result = birnbaum_importance(sg, p, bdd_with_root=bdd_with_root, select=select)

    return {select_key: {select_value: result["select"]}}


def get_attribute_sensitivity(sg: SystemGraph, data: Dict, data_src: str, prefs: Dict=None) -> Dict[str, Dict[bool, float]]:
    all_attrs = set()
    for node, nodeData in data["nodes"].items():
        if "attributes" in nodeData:
            all_attrs.update(nodeData["attributes"])
    results = {a: {} for a in all_attrs}
    for attr in all_attrs:
        for value in (True, False):
            results[attr].update(get_birnbaum_importances_select(sg, data, {attr: value}, data_src, prefs)[attr])

    return results


def get_fractional_importance_traits(sg: SystemGraph, data: Dict, prefs=None) -> Dict[str, Dict[bool, float]]:
    prefs = apply_prefs(prefs)
    return fractional_importance_of_attributes(sg, data)


def get_system_graph_optimized_suppliers(sg: SystemGraph, data: Dict, params: Dict) -> SystemGraph:
    problem = SupplierChoiceProblem(sg, data)
    chosen_suppliers, metadata = problem.solve(params)
    return sg.with_suppliers(chosen_suppliers)
