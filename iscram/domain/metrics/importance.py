from collections import Counter

from iscram.domain.model import (
    SystemGraph, DataValidationError
)
from iscram.domain.metrics.risk import risk_by_bdd
from iscram.domain.metrics.probability_providers import provide_p_unknown_data


def birnbaum_structural_importance(sg: SystemGraph, bdd_with_root=None, select=None):
    return birnbaum_importance(sg, provide_p_unknown_data(sg), bdd_with_root, select)


def birnbaum_importance(sg: SystemGraph, p, bdd_with_root=None, select=None):
    b_imps = {}

    if select is not None:
        for i in select:
            p[i] = 1.0
        risk_top = risk_by_bdd(sg, p, bdd_with_root)

        for i in select:
            p[i] = 0.0
        risk_bottom = risk_by_bdd(sg, p, bdd_with_root)

        b_imps["select"] = risk_top-risk_bottom
        return b_imps

    for i in sg.nodes:
        saved = p[i]
        p[i] = 1.0
        risk_top = risk_by_bdd(sg, p, bdd_with_root)
        p[i] = 0.0
        risk_bottom = risk_by_bdd(sg, p, bdd_with_root)
        b_imps[i] = risk_top - risk_bottom
        p[i] = saved  # restore to initial state

    del b_imps["indicator"]
    return b_imps


def fractional_importance_of_attributes(sg: SystemGraph, data, error_on_missing_data=False):
    all_attributes = []

    try:
        for node in sg.nodes:
            if node in data["nodes"]:
                if "attributes" in data["nodes"][node]:
                    for key, value in data["nodes"][node]["attributes"].items():
                        all_attributes.append((key, value))
            elif error_on_missing_data:
                raise DataValidationError("Missing attribute data for node: {}".format(node))
    except KeyError:
        if error_on_missing_data:
            raise DataValidationError("Invalid data for attribute importance calculation.")

    counts = Counter(all_attributes)
    total = sum(counts.values())
    f_imps = {a: (counts[a] / total) for a in all_attributes}

    return f_imps
