from pytest import approx

from iscram.domain.metrics.scale import (
    scale_proportionally, apply_scaling, scale_min_max
)


def test_scale_proportionally():
    data = {"1": .1, "2": .01, "3": .3, "4": .05, "5": .5}
    results = scale_proportionally(data)
    assert(sum(results.values()) == 1)

    assert(approx(results["2"] == 0.010417))
    assert(approx(results["5"] == 0.5208))


def test_scale_proportionally_tiny():
    data = {"1": .1, "2": .01}
    results = scale_proportionally(data)
    assert(sum(results.values()) == 1)

    assert(approx(results["1"] == 0.909))
    assert(approx(results["2"] == 0.0909))


def test_scale_min_max():
    data = {"1": .1, "2": .01, "3": .3, "4": .05, "5": .5}
    results = scale_min_max(data)
    assert approx(results["1"] == 0.7959)
    assert approx(results["2"] == 0.0)
    assert approx(results["5"] == 1.0)


def test_apply_scaling():
    data = {"1": .1, "2": .01, "3": .3, "4": .05, "5": .5}
    results = apply_scaling(data, "PROPORTIONAL")

    assert (sum(results.values()) == 1)
    assert (approx(results["2"] == 0.010417))
    assert (approx(results["5"] == 0.5208))

    results = apply_scaling(data, "NONE")
    assert results == data

    results = apply_scaling(data, "MIN_MAX")
    assert approx(results["1"] == 0.7959)
    assert approx(results["2"] == 0.0)
    assert approx(results["5"] == 1.0)