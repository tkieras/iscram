import pytest

from iscram.domain.metrics.cutset import (
    MOCUSError, mocus, brute_force_find_cutsets, minimize_cutsets
)

from iscram.domain.model import (
    Component, Supplier, Indicator, RiskRelation,
    Offering, SystemGraph
)

#
# def test_mocus_ignore_supplier_check_failure():
#     components = set([Component(str(i)) for i in range(10)])
#
#     suppliers = set([Supplier(str(i)) for i in range(10, 20)])
#
#     indicator = Indicator("and", frozenset([RiskRelation(str(i), "indicator") for i in {1, 2, 3}]))
#
#     offerings = {Offering("15", "5", 0.5, 30), Offering("16", "5", 0.5, 30), Offering("17", "3", 0.5, 30)}
#
#     deps = {RiskRelation("1", "3"), RiskRelation("2", "3"), RiskRelation("5", "6")}
#
#     sg = SystemGraph("test", frozenset(components), frozenset(suppliers), frozenset(deps),
#                      frozenset(offerings), indicator)
#
#     with pytest.raises(MOCUSError):
#         cutsets = mocus(sg, ignore_suppliers=False)
#
#
# def test_mocus_ignore_supplier_check_success():
#     components = set([Component(str(i)) for i in range(10)])
#
#     suppliers = set([Supplier(str(i)) for i in range(10, 20)])
#
#     indicator = Indicator("and", frozenset([RiskRelation(str(i), "indicator") for i in {1, 2, 3}]))
#
#     offerings = {Offering("15", "5", 0.5, 30), Offering("16", "3", 0.5, 30), Offering("17", "2", 0.5, 30)}
#
#     deps = {RiskRelation("1", "3"), RiskRelation("2", "3"), RiskRelation("5", "6")}
#
#     sg = SystemGraph("test", frozenset(components), frozenset(suppliers), frozenset(deps),
#                      frozenset(offerings), indicator)
#     # No error should be thrown
#     cutsets = mocus(sg, ignore_suppliers=False)


def test_mocus_success_simple_and(simple_and: SystemGraph):
    expected = frozenset([frozenset(["one", "two"]), frozenset(["three"])])
    cutsets = mocus(simple_and)

    assert cutsets == expected


def test_mocus_success_simple_or(simple_or: SystemGraph):
    expected = frozenset([frozenset(["one"]), frozenset(["two"]), frozenset(["three"])])
    cutsets = mocus(simple_or)

    assert cutsets == expected


def test_mocus_simple_supplier_success():
    components = frozenset({Component("one", "and"), Component("two", "and"), Component("three", "and")})

    indicator = Indicator("and", frozenset({RiskRelation("three", "indicator")}))

    deps = frozenset({RiskRelation("one", "three"), RiskRelation("two", "three"),
                      RiskRelation("eleven", "one"),
                      RiskRelation("twelve", "two"),
                      RiskRelation("thirteen", "three")})

    suppliers = frozenset({Supplier("eleven"), Supplier("twelve"), Supplier("thirteen")})

    offerings = frozenset()

    sg = SystemGraph("simple", components, suppliers, deps, offerings, indicator)

    expected = frozenset([
                    frozenset(["three"]), frozenset(["one", "two"]), frozenset(["thirteen"]),
                    frozenset(["one", "twelve"]), frozenset(["two", "eleven"]), frozenset(["eleven", "twelve"])
    ])
    cutsets = mocus(sg, ignore_suppliers=False)

    assert cutsets == expected


def test_mocus_canonical(canonical: SystemGraph):
    expected = frozenset([frozenset(["one"]),
                          frozenset(["two", "five"]),
                          frozenset(["three", "five"]),
                          frozenset(["four", "five"]),
                          frozenset(["eight", "nine", "five"]),
                          frozenset(["two", "six"]),
                          frozenset(["three", "six"]),
                          frozenset(["four", "six"]),
                          frozenset(["eight", "nine", "six"]),
                          frozenset(["two", "seven"]),
                          frozenset(["three", "seven"]),
                          frozenset(["four", "seven"]),
                          frozenset(["eight", "nine", "seven"])])

    cutsets = mocus(canonical)
    assert cutsets == expected


def test_mocus_all_or():
    pass


def test_mocus_all_and():
    pass


def test_mocus_gigantic_mixed():
    pass


def test_mocus_simple_non_tree(non_tree_simple_and: SystemGraph):
    cutsets = mocus(non_tree_simple_and)
    expected = frozenset([frozenset(["three"]), frozenset(["one", "two"]), frozenset(["four"])])

    assert cutsets == expected


def test_mocus_complex_non_tree():
    components = frozenset([
        Component("one", "and"),
        Component("two", "and"),
        Component("three", "and"),
        Component("four", "or"),
        Component("five", "or"),
        Component("six", "or"),
        Component("seven", "or"),
        Component("eight", "or"),
        Component("nine", "or"),
        Component("ten", "or")
    ])

    deps = frozenset([
        RiskRelation("ten", "nine"),
        RiskRelation("ten", "eight"),
        RiskRelation("eight", "four"),
        RiskRelation("eight", "six"),
        RiskRelation("nine", "seven"),
        RiskRelation("nine", "five"),
        RiskRelation("four", "two"),
        RiskRelation("six", "two"),
        RiskRelation("seven", "three"),
        RiskRelation("five", "three"),
        RiskRelation("two", "one"),
        RiskRelation("three", "one")
    ])

    indicator = Indicator("and", frozenset([RiskRelation("one", "indicator")]))
    suppliers = frozenset()
    offerings = frozenset()
    sg = SystemGraph("complex_or_nontree", components, suppliers, deps, offerings, indicator)

    cutsets = mocus(sg)
    expected = frozenset([
        frozenset(["one"]),
        frozenset(["two", "three"]),
        frozenset(["four", "six", "seven", "five"]),
        frozenset(["eight", "nine"]),
        frozenset(["ten"]),
        frozenset(["eight", "three"]),
        frozenset(["nine", "two"]),
        frozenset(["four", "six", "three"]),
        frozenset(["four", "six", "nine"]),
        frozenset(["seven", "five", "eight"]),
        frozenset(["seven", "five", "two"])
    ])
    assert cutsets == expected


def test_brute_force_cutsets_simple_and(simple_and: SystemGraph):
    expected = frozenset([frozenset(["one", "two"]), frozenset(["three"])])
    cutsets = brute_force_find_cutsets(simple_and)

    assert cutsets == expected


def test_brute_force_empty():
    sg = SystemGraph("none", frozenset(), frozenset(), frozenset(), frozenset(), Indicator("and", frozenset()))

    assert (len(brute_force_find_cutsets(sg)) == 0)


def test_brute_force_cutsets_simple_or(simple_or: SystemGraph):
    expected = frozenset([frozenset(["one"]), frozenset(["two"]), frozenset(["three"])])
    cutsets = brute_force_find_cutsets(simple_or)

    assert cutsets == expected


def test_brute_force_cutsets_canonical(canonical: SystemGraph):
    expected = frozenset([frozenset(["one"]),
                          frozenset(["two", "five"]),
                          frozenset(["three", "five"]),
                          frozenset(["four", "five"]),
                          frozenset(["eight", "nine", "five"]),
                          frozenset(["two", "six"]),
                          frozenset(["three", "six"]),
                          frozenset(["four", "six"]),
                          frozenset(["eight", "nine", "six"]),
                          frozenset(["two", "seven"]),
                          frozenset(["three", "seven"]),
                          frozenset(["four", "seven"]),
                          frozenset(["eight", "nine", "seven"])])

    cutsets = brute_force_find_cutsets(canonical)

    assert cutsets == expected


