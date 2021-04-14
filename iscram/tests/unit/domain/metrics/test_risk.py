from pytest import approx

from iscram.domain.model import SystemGraph

from iscram.domain.metrics.probability_providers import (
    provide_p_unknown_data
)

from iscram.domain.metrics.risk import (
    risk_by_cutsets, risk_by_bdd, probability_any_cutset
)


def test_risk_by_cutsets_minimal(minimal: SystemGraph):
    assert (risk_by_cutsets(minimal, {"indicator": 0, "x1": 0, "x2": 0, "x3": 0}) == 0)
    assert (risk_by_cutsets(minimal, {"indicator": 0, "x1": 0, "x2": 0, "x3": 1}) == 1)
    assert (risk_by_cutsets(minimal, {"indicator": 0, "x1": 0, "x2": 1, "x3": 0}) == 0)
    assert (risk_by_cutsets(minimal, {"indicator": 0, "x1": 1, "x2": 0, "x3": 0}) == 0)
    assert (risk_by_cutsets(minimal, {"indicator": 0, "x1": 1, "x2": 1, "x3": 0}) == 1)
    assert (risk_by_cutsets(minimal, {"indicator": 0, "x1": 1, "x2": 1, "x3": 1}) == 1)
    assert (risk_by_cutsets(minimal, {"indicator": 0, "x1": 0, "x2": 0, "x3": 0}) == 0)
    assert (risk_by_cutsets(minimal, {"indicator": 0, "x1": .5, "x2": .5, "x3": 0}) == .25)
    assert (risk_by_cutsets(minimal, {"indicator": 0, "x1": 0, "x2": 0, "x3": .25}) == .25)


def test_risk_by_bdd_minimal(minimal: SystemGraph):
    assert (risk_by_bdd(minimal, {"indicator": 0, "x1": 0, "x2": 0, "x3": 0}) == 0)
    assert (risk_by_bdd(minimal, {"indicator": 0, "x1": 0, "x2": 0, "x3": 1}) == 1)
    assert (risk_by_bdd(minimal, {"indicator": 0, "x1": 0, "x2": 1, "x3": 0}) == 0)
    assert (risk_by_bdd(minimal, {"indicator": 0, "x1": 1, "x2": 0, "x3": 0}) == 0)
    assert (risk_by_bdd(minimal, {"indicator": 0, "x1": 1, "x2": 1, "x3": 0}) == 1)
    assert (risk_by_bdd(minimal, {"indicator": 0, "x1": 1, "x2": 1, "x3": 1}) == 1)
    assert (risk_by_bdd(minimal, {"indicator": 0, "x1": 0, "x2": 0, "x3": 0}) == 0)
    assert (risk_by_bdd(minimal, {"indicator": 0, "x1": .5, "x2": .5, "x3": 0}) == .25)
    assert (risk_by_bdd(minimal, {"indicator": 0, "x1": 0, "x2": 0, "x3": .25}) == .25)


def test_risk_by_cutset_canonical(canonical: SystemGraph):
    assert approx(risk_by_cutsets(canonical, provide_p_unknown_data(canonical)) == 0.9748495630919933)


def test_risk_by_bdd_canonical(canonical: SystemGraph):
    assert approx(risk_by_bdd(canonical, provide_p_unknown_data(canonical)) == 0.9748495630919933)


def test_risk_by_bdd_diamond(diamond: SystemGraph):
    assert approx(risk_by_bdd(diamond, provide_p_unknown_data(diamond)) == 0.625)


def test_manual_risk_cutsets_canonical():
    cutsets = frozenset([frozenset(["x1"]),
                         frozenset(["x2", "x5"]),
                         frozenset(["x3", "x5"]),
                         frozenset(["x4", "x5"]),
                         frozenset(["x8", "x9", "x4"]),
                         frozenset(["x2", "x6"]),
                         frozenset(["x3", "x6"]),
                         frozenset(["x4", "x6"]),
                         frozenset(["x8", "x9", "x6"]),
                         frozenset(["x2", "x7"]),
                         frozenset(["x3", "x7"]),
                         frozenset(["x4", "x7"]),
                         frozenset(["x8", "x9", "x7"])])

    p = {"x1": 0.5, "x2": 0.5, "x3": 0.5, "x4": 0.5, "x5": 0.5, "x6": 0.5, "x7": 0.5, "x8": 0.5, "x9": 0.5}
    assert approx(probability_any_cutset(cutsets, p) == 0.9748495630919933)

