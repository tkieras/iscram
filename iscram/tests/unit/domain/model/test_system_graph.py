from iscram.domain.model import (
    Component, Supplier, Indicator, RiskRelation,
    Offering, SystemGraph
)


def test_empty_sg():
    sg = SystemGraph("test", frozenset(), frozenset(), frozenset(), frozenset(), Indicator("and", frozenset()))

    assert sg.valid_values()


def test_full_sg():
    components = frozenset([Component(str(i)) for i in range(10)])

    suppliers = frozenset([Supplier(str(i)) for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation(str(i), "indicator") for i in {1, 2, 3}]))

    offerings = frozenset({Offering("15", "5", 0.5, 30), Offering("16", "5", 0.5, 30), Offering("17", "3", 0.5, 30)})

    deps = frozenset({RiskRelation("1", "3"), RiskRelation("2", "3"), RiskRelation("5", "6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    assert sg.valid_values()


def test_mismatched_indicator():
    components = frozenset([Component(str(i)) for i in range(10)])

    suppliers = frozenset([Supplier(str(i)) for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation(str(i), "indicator") for i in {10, 15, 35}]))

    offerings = frozenset({Offering("15", "5", 0.5, 30), Offering("16", "5", 0.5, 30), Offering("17", "3", 0.5, 30)})

    deps = frozenset({RiskRelation("1", "3"), RiskRelation("2", "3"), RiskRelation("5", "6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    assert not sg.valid_values()


def test_mismatched_offerings():
    components = frozenset([Component(str(i)) for i in range(10)])

    suppliers = frozenset([Supplier(str(i)) for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation(str(i), "indicator") for i in {1, 2, 3}]))

    offerings = frozenset({Offering("15", "300", 0.5, 30), Offering("413", "5", 0.5, 30), Offering("17", "3", 0.5, 30)})

    deps = frozenset({RiskRelation("1", "3"), RiskRelation("2", "3"), RiskRelation("5", "6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    assert not sg.valid_values()


def test_mismatched_deps():
    components = frozenset([Component(str(i)) for i in range(10)])

    suppliers = frozenset([Supplier(str(i)) for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation(str(i), "indicator") for i in {1, 2, 3}]))

    offerings = frozenset({Offering("15", "5", 0.5, 30), Offering("16", "5", 0.5, 30), Offering("17", "3", 0.5, 30)})

    deps = frozenset({RiskRelation("100", "3"), RiskRelation("23", "3"), RiskRelation("5", "6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    assert not sg.valid_values()


def test_overlapping_ids():
    components = frozenset([Component(str(i)) for i in range(10)])

    suppliers = frozenset([Supplier(str(i)) for i in range(15)])

    indicator = Indicator("and", frozenset([RiskRelation(str(i), "indicator") for i in {1, 2, 3}]))

    offerings = frozenset({Offering("15", "5", 0.5, 30), Offering("16", "5", 0.5, 30), Offering("17", "3", 0.5, 30)})

    deps = frozenset({RiskRelation("1", "3"), RiskRelation("2", "3"), RiskRelation("5", "6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    assert not sg.valid_values()


def test_internally_overlapping_ids():
    components = set([Component(str(i)) for i in range(10)])

    components.add(Component(str(3), risk=0.4342))

    components = frozenset(components)

    suppliers = frozenset([Supplier(str(i)) for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation(str(i), "indicator") for i in {1, 2, 3}]))

    offerings = frozenset({Offering("15", "5", 0.5, 30), Offering("16", "5", 0.5, 30), Offering("17", "3", 0.5, 30)})

    deps = frozenset({RiskRelation("1", "3"), RiskRelation("2", "3"), RiskRelation("5", "6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    assert not sg.valid_values()


def test_hash_equal():
    components = frozenset([Component(str(i)) for i in range(10)])

    suppliers = frozenset([Supplier(str(i)) for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation(str(i), "indicator") for i in {1, 2, 3}]))

    offerings = frozenset({Offering("15", "5", 0.5, 30), Offering("16", "5", 0.5, 30), Offering("17", "3", 0.5, 30)})

    deps = frozenset({RiskRelation("1", "3"), RiskRelation("2", "3"), RiskRelation("5", "6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    components_2 = frozenset([Component(str(i)) for i in range(10)])

    suppliers_2 = frozenset([Supplier(str(i)) for i in range(10, 20)])

    indicator_2 = Indicator("and", frozenset([RiskRelation(str(i), "indicator") for i in {1, 2, 3}]))

    offerings_2 = frozenset({Offering("15", "5", 0.5, 30), Offering("16", "5", 0.5, 30), Offering("17", "3", 0.5, 30)})

    deps_2 = frozenset({RiskRelation("1", "3"), RiskRelation("2", "3"), RiskRelation("5", "6")})

    sg_2 = SystemGraph("test", components_2, suppliers_2, deps_2, offerings_2, indicator_2)

    assert id(sg) != id(sg_2)
    assert hash(sg) == hash(sg_2)


def test_hash_not_equal():
    components = frozenset([Component(str(i)) for i in range(10)])

    suppliers = frozenset([Supplier(str(i)) for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation(str(i), "indicator") for i in {1, 2, 3}]))

    offerings = frozenset({Offering("15", "5", 0.5, 30), Offering("16", "5", 0.5, 30), Offering("17", "3", 0.5, 30)})

    deps = frozenset({RiskRelation("1", "3"), RiskRelation("2", "3"), RiskRelation("5", "6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    components_2 = frozenset([Component(str(i)) for i in range(10)])

    suppliers_2 = frozenset([Supplier(str(i)) for i in range(10, 20)])

    indicator_2 = Indicator("and", frozenset([RiskRelation(str(i), "indicator") for i in {1, 2, 3}]))

    offerings_2 = frozenset({Offering("15", "5", 0.49, 30), Offering("16", "5", 0.5, 30), Offering("17", "3", 0.5, 30)})

    deps_2 = frozenset({RiskRelation("1", "3"), RiskRelation("2", "3"), RiskRelation("5", "6")})

    sg_2 = SystemGraph("test", components_2, suppliers_2, deps_2, offerings_2, indicator_2)

    assert id(sg) != id(sg_2)
    assert hash(sg) != hash(sg_2)


def test_structure_equal():
    components = frozenset([Component(str(i)) for i in range(10)])

    suppliers = frozenset([Supplier(str(i)) for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation(str(i), "indicator") for i in {1, 2, 3}]))

    offerings = frozenset({Offering("15", "5", 0.5, 30), Offering("16", "5", 0.5, 30), Offering("17", "3", 0.5, 30)})

    deps = frozenset({RiskRelation("1", "3"), RiskRelation("2", "3"), RiskRelation("5", "6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    components_2 = frozenset([Component(str(i)) for i in range(10)])

    suppliers_2 = frozenset([Supplier(str(i)) for i in range(10, 20)])

    indicator_2 = Indicator("and", frozenset([RiskRelation(str(i), "indicator") for i in {1, 2, 3}]))

    offerings_2 = frozenset({Offering("15", "5", 0.49, 30), Offering("16", "5", 0.5, 30), Offering("17", "3", 0.5, 30)})

    deps_2 = frozenset({RiskRelation("1", "3"), RiskRelation("2", "3"), RiskRelation("5", "6")})

    sg_2 = SystemGraph("test", components_2, suppliers_2, deps_2, offerings_2, indicator_2)

    assert id(sg) != id(sg_2)
    assert sg != sg_2
    assert hash(sg) != hash(sg_2)
    assert sg.structure() == sg_2.structure()


def test_structure_unequal():
    components = frozenset([Component(str(i)) for i in range(10)])

    suppliers = frozenset([Supplier(str(i)) for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation(str(i), "indicator") for i in {1, 2, 3}]))

    offerings = frozenset({Offering("15", "5", 0.5, 30), Offering("16", "5", 0.5, 30), Offering("17", "3", 0.5, 30)})

    deps = frozenset({RiskRelation("1", "3"), RiskRelation("2", "3"), RiskRelation("5", "6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    components_2 = frozenset([Component(str(i)) for i in range(10)])

    suppliers_2 = frozenset([Supplier(str(i)) for i in range(10, 20)])

    indicator_2 = Indicator("and", frozenset([RiskRelation(str(i), "indicator") for i in {1, 2, 3}]))

    offerings_2 = frozenset({Offering("15", "5", 0.5, 30), Offering("16", "5", 0.5, 30), Offering("17", "3", 0.5, 30)})

    deps_2 = frozenset({RiskRelation("1", "3"), RiskRelation("2", "3"), RiskRelation("5", "6"), RiskRelation("15", "3")})

    sg_2 = SystemGraph("test", components_2, suppliers_2, deps_2, offerings_2, indicator_2)

    assert id(sg) != id(sg_2)
    assert sg != sg_2
    assert hash(sg) != hash(sg_2)
    assert sg.structure() != sg_2.structure()
