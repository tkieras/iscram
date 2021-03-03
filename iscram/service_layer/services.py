from iscram.domain.model import SystemGraph
from iscram.adapters.repository import (
    AbstractRepository
)
from iscram.domain.metrics.risk import risk_by_cutsets
from iscram.domain.metrics.cutset import find_minimal_cutsets
from iscram.domain.metrics.importance import (
    birnbaum_importance, birnbaum_structural_importance
)


def get_cutsets(sg: SystemGraph, repo: AbstractRepository):
    cutsets = repo.get(sg, "cutsets")

    if cutsets is None:
        cutsets = find_minimal_cutsets(sg, ignore_suppliers=False)
        repo.put(sg, "cutsets", cutsets)

    return cutsets


def get_risk(sg: SystemGraph, repo: AbstractRepository):

    result = repo.get(sg, "risk")

    if result is not None:
        return result

    cutsets = get_cutsets(sg, repo)
    risk = risk_by_cutsets(sg, cutsets=cutsets)
    repo.put(sg, "risk", risk)
    return risk


def get_birnbaum_structural_importances(sg: SystemGraph, repo: AbstractRepository):

    result = repo.get(sg, "birnbaum_structural_importances")

    if result is None:
        result = birnbaum_structural_importance(sg)
        repo.put(sg, "birnbaum_structural_importances", result)

    return result


def get_birnbaum_importances(sg: SystemGraph, repo: AbstractRepository):

    result = repo.get(sg, "birnbaum_importances")

    if result is None:
        result = birnbaum_importance(sg)
        repo.put(sg, "birnbaum_importances", result)

    return result
