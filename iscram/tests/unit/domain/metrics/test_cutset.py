import pytest

from iscram.domain.metrics.cutset import (
    MOCUSError, mocus, brute_force_find_cutsets
)

from iscram.domain.model import (
    Component, Supplier, Indicator, RiskRelation,
    Offering, SystemGraph
)


def test_mocus_ignore_supplier_check_failure():
    components = set([Component(i, "name") for i in range(10)])

    suppliers = set([Supplier(i, "name") for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation(i, -1) for i in {1, 2, 3}]))

    offerings = {Offering(15, 5, 0.5, 30), Offering(16, 5, 0.5, 30), Offering(17, 3, 0.5, 30)}

    deps = {RiskRelation(1, 3), RiskRelation(2, 3), RiskRelation(5, 6)}

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    with pytest.raises(MOCUSError):
        cutsets = mocus(sg, ignore_suppliers=False)


def test_mocus_ignore_supplier_check_success():
    components = set([Component(i, "name") for i in range(10)])

    suppliers = set([Supplier(i, "name") for i in range(10, 20)])

    indicator = Indicator("and", {RiskRelation(3, -1)})

    offerings = {Offering(15, 5, 0.5, 30), Offering(16, 3, 0.5, 30), Offering(17, 2, 0.5, 30)}

    deps = {RiskRelation(1, 3), RiskRelation(2, 3), RiskRelation(5, 3)}

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    # No error should be thrown
    cutsets = mocus(sg, ignore_suppliers=False)


def test_mocus_success_simple_and():
    components = {Component(1, "one", "and"), Component(2, "two", "and"), Component(3, "three", "and")}

    indicator = Indicator("and", {RiskRelation(3, -1)})

    deps = {RiskRelation(1, 3), RiskRelation(2, 3)}

    sg = SystemGraph("simple", components, set(), deps, set(), indicator)

    expected = frozenset([frozenset([1, 2]), frozenset([3])])

    cutsets = mocus(sg)

    assert cutsets == expected


def test_mocus_success_simple_or():
    components = {Component(1, "one", "and"), Component(2, "two", "and"), Component(3, "three", "or")}

    indicator = Indicator("and", {RiskRelation(3, -1)})

    deps = {RiskRelation(1, 3), RiskRelation(2, 3)}

    sg = SystemGraph("simple", components, set(), deps, set(), indicator)

    expected = frozenset([frozenset([1]), frozenset([2]), frozenset([3])])

    cutsets = mocus(sg)

    assert cutsets == expected


def test_mocus_simple_supplier_success():
    components = {Component(1, "one", "and"), Component(2, "two", "and"), Component(3, "three", "and")}

    indicator = Indicator("and", {RiskRelation(3, -1)})

    deps = {RiskRelation(1, 3), RiskRelation(2, 3)}

    suppliers = {Supplier(11, "eleven"), Supplier(12, "twelve"), Supplier(13, "thirteen")}

    offerings = {Offering(11, 1, 1.0, 30), Offering(12, 2, 1.0, 30), Offering(13, 3, 1.0, 30)}

    sg = SystemGraph("simple", components, suppliers, deps, offerings, indicator)

    expected = frozenset([frozenset([3]),
                          frozenset([1, 13, 2]),
                          frozenset([11, 13, 2]),
                          frozenset([1, 13, 12]),
                          frozenset([1, 13, 12]),
                          frozenset([11, 13, 12])
                        ])
    cutsets = mocus(sg, ignore_suppliers=False)

    assert cutsets == expected


def test_mocus_canonical():
    components = {Component(1, "one", "and"),
                  Component(2, "two", "or"),
                  Component(3, "three", "and"),
                  Component(4, "four", "and"),
                  Component(5, "five", "or"),
                  Component(6, "six", "and"),
                  Component(7, "seven", "and"),
                  Component(8, "eight", "and"),
                  Component(9, "nine", "and")}

    indicator = Indicator("and", {RiskRelation(1, -1)})

    deps = {RiskRelation(2, 1),
            RiskRelation(5, 1),
            RiskRelation(3, 2),
            RiskRelation(4, 2),
            RiskRelation(6, 5),
            RiskRelation(7, 5),
            RiskRelation(8, 4),
            RiskRelation(9, 4)}

    sg = SystemGraph("simple", components, set(), deps, set(), indicator)

    expected = frozenset([frozenset([1]),
                          frozenset([2, 5]),
                          frozenset([3, 5]),
                          frozenset([4, 5]),
                          frozenset([8, 9, 5]),
                          frozenset([2, 6]),
                          frozenset([3, 6]),
                          frozenset([4, 6]),
                          frozenset([8, 9, 6]),
                          frozenset([2, 7]),
                          frozenset([3, 7]),
                          frozenset([4, 7]),
                          frozenset([8, 9, 7])])

    cutsets = mocus(sg)

    assert cutsets == expected


def test_mocus_all_or():
    pass


def test_mocus_all_and():
    pass


def test_mocus_gigantic_mixed():
    pass


def test_mocus_non_tree(non_tree_simple_and: SystemGraph):
    with pytest.raises(MOCUSError):
        cutsets = mocus(non_tree_simple_and)


def test_brute_force_cutsets_simple_and():
    components = frozenset({Component(1, "one", "and"),
                            Component(2, "two", "and"),
                            Component(3, "three", "and")})

    indicator = Indicator("and", frozenset({RiskRelation(3, -1)}))

    deps = frozenset({RiskRelation(1, 3), RiskRelation(2, 3)})

    sg = SystemGraph("simple", components, frozenset(), deps, frozenset(), indicator)

    expected = frozenset([frozenset([1, 2]), frozenset([3])])

    cutsets = brute_force_find_cutsets(sg)

    assert cutsets == expected


def test_brute_force_empty():
    sg = SystemGraph("none", frozenset(), frozenset(), frozenset(), frozenset(), Indicator("and", frozenset()))

    assert(len(brute_force_find_cutsets(sg)) == 0)


def test_brute_force_cutsets_simple_or():
    components = {Component(1, "one", "and"), Component(2, "two", "and"), Component(3, "three", "or")}

    indicator = Indicator("and", {RiskRelation(3, -1)})

    deps = {RiskRelation(1, 3), RiskRelation(2, 3)}

    sg = SystemGraph("simple", components, set(), deps, set(), indicator)

    expected = frozenset([frozenset([1]), frozenset([2]), frozenset([3])])

    cutsets = brute_force_find_cutsets(sg)

    assert cutsets == expected


def test_brute_force_cutsets_canonical():
    components = {Component(1, "one", "and"),
                  Component(2, "two", "or"),
                  Component(3, "three", "and"),
                  Component(4, "four", "and"),
                  Component(5, "five", "or"),
                  Component(6, "six", "and"),
                  Component(7, "seven", "and"),
                  Component(8, "eight", "and"),
                  Component(9, "nine", "and")}

    indicator = Indicator("and", {RiskRelation(1, -1)})

    deps = {RiskRelation(2, 1),
            RiskRelation(5, 1),
            RiskRelation(3, 2),
            RiskRelation(4, 2),
            RiskRelation(6, 5),
            RiskRelation(7, 5),
            RiskRelation(8, 4),
            RiskRelation(9, 4)}

    sg = SystemGraph("simple", components, set(), deps, set(), indicator)

    expected = frozenset([frozenset([1]),
                          frozenset([2, 5]),
                          frozenset([3, 5]),
                          frozenset([4, 5]),
                          frozenset([8, 9, 5]),
                          frozenset([2, 6]),
                          frozenset([3, 6]),
                          frozenset([4, 6]),
                          frozenset([8, 9, 6]),
                          frozenset([2, 7]),
                          frozenset([3, 7]),
                          frozenset([4, 7]),
                          frozenset([8, 9, 7])])

    cutsets = brute_force_find_cutsets(sg)

    assert cutsets == expected