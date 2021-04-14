import pytest

from iscram.domain.metrics.cutset import (
    mocus, probability_union, minimize_cutsets, brute_force_bdd_cutsets
)

from iscram.domain.model import SystemGraph


@pytest.mark.parametrize("x,expected", (
                         ((0.3, 0.245), 0.4715),
                         ((0.5, 0.5, 0.5), 0.875),
                         ((0.01, 0.93, 0.24, 0.56), 0.976826)
                         ))
def test_probability_union(x, expected):
    assert pytest.approx(probability_union(x) == expected)


def test_mocus_success_minimal(minimal: SystemGraph):
    expected = frozenset([frozenset(["x1", "x2"]), frozenset(["x3"])])
    cutsets = mocus(minimal)
    assert cutsets == expected


def test_mocus_diamond(diamond: SystemGraph):
    expected = frozenset([frozenset(["x1"]), frozenset(["x2"]), frozenset(["x3"])])
    assert mocus(diamond) == expected


def test_mocus_canonical(canonical: SystemGraph):
    expected = frozenset([frozenset(["x1"]),
                         frozenset(["x2", "x5"]),
                         frozenset(["x3", "x5"]),
                         frozenset(["x4", "x5"]),
                         frozenset(["x8", "x9", "x5"]),
                         frozenset(["x2", "x6"]),
                         frozenset(["x3", "x6"]),
                         frozenset(["x4", "x6"]),
                         frozenset(["x8", "x9", "x6"]),
                         frozenset(["x2", "x7"]),
                         frozenset(["x3", "x7"]),
                         frozenset(["x4", "x7"]),
                         frozenset(["x8", "x9", "x7"])])

    cutsets = mocus(canonical)
    assert cutsets == expected


def test_minimize_cutsets():
    non_minimal = [
        frozenset(["a", "b", "c"]),
        frozenset(["b", "a"]),
        frozenset(["c"])
    ]

    expected = frozenset([
        frozenset(["c"]),
        frozenset(["b", "a"])
    ])

    assert minimize_cutsets(non_minimal) == expected


def test_brute_force_bdd_cutsets(canonical: SystemGraph):
    expected = frozenset([frozenset(["x1"]),
                          frozenset(["x2", "x5"]),
                          frozenset(["x3", "x5"]),
                          frozenset(["x4", "x5"]),
                          frozenset(["x8", "x9", "x5"]),
                          frozenset(["x2", "x6"]),
                          frozenset(["x3", "x6"]),
                          frozenset(["x4", "x6"]),
                          frozenset(["x8", "x9", "x6"]),
                          frozenset(["x2", "x7"]),
                          frozenset(["x3", "x7"]),
                          frozenset(["x4", "x7"]),
                          frozenset(["x8", "x9", "x7"])])

    assert brute_force_bdd_cutsets(canonical) == expected

