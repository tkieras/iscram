import pytest

from iscram.domain.metrics.cutset import (
    mocus, probability_union, minimize_cutsets, brute_force_bdd_cutsets
)

from iscram.domain.model import (
    Component, Supplier, Indicator, RiskRelation, SystemGraph
)


@pytest.mark.parametrize("x,expected", (
                         ((0.3, 0.245), 0.4715),
                         ((0.5, 0.5, 0.5), 0.875),
                         ((0.01, 0.93, 0.24, 0.56), 0.976826)
                         ))
def test_probability_union(x, expected):
    assert pytest.approx(probability_union(x) == expected)


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

    assert brute_force_bdd_cutsets(canonical) == expected


def test_brute_force_bdd_complex_non_tree():
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

    cutsets = brute_force_bdd_cutsets(sg)
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
