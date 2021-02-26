from iscram.domain.model import SystemGraph
from iscram.adapters.repository import (
    AbstractRepository, RepositoryError
)
from iscram.domain.metrics.risk import risk_by_cutsets
from iscram.domain.metrics.importance import (
    birnbaum_importance, birnbaum_structural_importance
)


def get_risk(sg: SystemGraph, repo: AbstractRepository):
    try:
        result = repo.get(sg, "risk")
    except RepositoryError:
        result = risk_by_cutsets(sg)
        repo.put(sg, "risk", result)

    return result


def get_birnbaum_structural_importances(sg: SystemGraph, repo: AbstractRepository):
    try:
        result = repo.get(sg, "birnbaum_structural_importances")
    except RepositoryError:
        result = birnbaum_structural_importance(sg)
        repo.put(sg, "birnbaum_structural_importances", result)

    return result


def get_birnbaum_importances(sg: SystemGraph, repo: AbstractRepository):
    try:
        result = repo.get(sg, "birnbaum_importances")
    except RepositoryError:
        result = birnbaum_importance(sg)
        repo.put(sg, "birnbaum_importances", result)

    return result
