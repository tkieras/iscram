from pytest import approx

from importlib.resources import read_text
from iscram.adapters.json import load_system_graph_json_str

from iscram.domain.model import (
    Component, Indicator, RiskRelation, SystemGraph
)
from iscram.domain.metrics.risk import (
    risk_by_cutsets, collect_x, risk_by_bdd, probability_any_cutset
)


def test_collect_x(simple_and: SystemGraph):

    expected = {"indicator": 0, "one": 0.0, "two": 0.0, "three": 0.0}

    assert (collect_x(simple_and) == expected)


def test_risk_by_cutsets_simple_and(simple_and: SystemGraph):

    sg = simple_and

    x = {"indicator": 0, "one": 0, "two": 0, "three": 0}
    assert (risk_by_cutsets(sg, x) == 0)

    x = {"indicator": 0, "one": 0, "two": 0, "three": 1}
    assert (risk_by_cutsets(sg, x) == 1)

    x = {"indicator": 0, "one": 0, "two": 1, "three": 0}
    assert (risk_by_cutsets(sg, x) == 0)

    x = {"indicator": 0, "one": 1, "two": 0, "three": 0}
    assert (risk_by_cutsets(sg, x) == 0)

    x = {"indicator": 0, "one": 1, "two": 1, "three": 0}
    assert (risk_by_cutsets(sg, x) == 1)

    x = {"indicator": 0, "one": 0.5, "two": 0.5, "three": 0}
    assert (risk_by_cutsets(sg, x) == 0.25)

    x = {"indicator": 0, "one": 0, "two": 0, "three": 0.5}
    assert (risk_by_cutsets(sg, x) == 0.5)


def test_risk_by_cutset_canonical(canonical: SystemGraph):
    x = {k.identifier: 0.5 for k in canonical.components}

    assert approx(risk_by_cutsets(canonical, x) == 0.9748495630919933)


def test_manual_risk_cutsets_canonical(canonical: SystemGraph):
    x = {k.identifier: 0.5 for k in canonical.components}

    cutsets = frozenset([frozenset(["one"]),
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

    risk = probability_any_cutset(cutsets, x)

    assert approx(risk == 0.9748495630919933)


def test_risk_by_bdd_canonical(canonical: SystemGraph):
    x = {k.identifier: 0.5 for k in canonical.components}

    assert approx(risk_by_bdd(canonical, x) == 0.9748495630919933)


def test_risk_by_bdd_simple_and(simple_and: SystemGraph):

    sg = simple_and

    x = {"indicator": 0, "one": 0, "two": 0, "three": 0}
    assert (risk_by_bdd(sg, x) == 0)

    x = {"indicator": 0, "one": 0, "two": 0, "three": 1}
    assert (risk_by_bdd(sg, x) == 1)

    x = {"indicator": 0, "one": 0, "two": 1, "three": 0}
    assert (risk_by_bdd(sg, x) == 0)

    x = {"indicator": 0, "one": 1, "two": 0, "three": 0}
    assert (risk_by_bdd(sg, x) == 0)

    x = {"indicator": 0, "one": 1, "two": 1, "three": 0}
    assert (risk_by_bdd(sg, x) == 1)

    x = {"indicator": 0, "one": 0.5, "two": 0.5, "three": 0}
    assert (risk_by_bdd(sg, x) == 0.25)

    x = {"indicator": 0, "one": 0, "two": 0, "three": 0.5}
    assert (risk_by_bdd(sg, x) == 0.5)


def test_bdd_complex_non_tree():
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
    x = {u.identifier: 0.5 for u in sg.components}

    cutset_risk = probability_any_cutset(expected, x)

    bdd_risk = risk_by_bdd(sg, x)

    assert approx(cutset_risk == bdd_risk)


def test_speed_rand_tree_100():
    json_str = read_text("iscram.tests.system_graph_test_data", "random_tree_100.json")
    sg = load_system_graph_json_str(json_str)
    risk = risk_by_bdd(sg)
    assert risk > 0


def test_speed_rand_tree_75():
    json_str = read_text("iscram.tests.system_graph_test_data", "random_tree_75.json")
    sg = load_system_graph_json_str(json_str)
    risk = risk_by_bdd(sg)
    assert risk > 0


def test_speed_rand_tree_50():
    json_str = read_text("iscram.tests.system_graph_test_data", "random_tree_50.json")
    sg = load_system_graph_json_str(json_str)
    risk = risk_by_bdd(sg)
    assert risk > 0


def test_speed_rand_tree_25():
    json_str = read_text("iscram.tests.system_graph_test_data", "random_tree_25.json")
    sg = load_system_graph_json_str(json_str)
    risk = risk_by_bdd(sg)
    assert risk > 0