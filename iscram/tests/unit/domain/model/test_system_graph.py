from iscram.domain.model import (
    Component, Supplier, Indicator, RiskRelation,
    Offering, SystemGraph, apply_singular_offerings
)


def test_empty_sg():
    sg = SystemGraph("test", frozenset(), frozenset(), frozenset(), frozenset(), Indicator("and", frozenset()))

    assert sg.valid_values()


def test_full_sg(full_example: SystemGraph):
    assert full_example.valid_values()


def test_mismatched_indicator():
    components = frozenset([Component("x" + str(i)) for i in range(10)])

    suppliers = frozenset([Supplier("x" + str(i)) for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation("x" + str(i), "indicator") for i in {10, 15, 35}]))

    offerings = frozenset({Offering("x15", "x5", 0.5, 30), Offering("x16", "x5", 0.5, 30), Offering("x17", "x3", 0.5, 30)})

    deps = frozenset({RiskRelation("x1", "x3"), RiskRelation("x2", "x3"), RiskRelation("x5", "x6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    assert not sg.valid_values()


def test_mismatched_offerings():
    components = frozenset([Component("x" + str(i)) for i in range(10)])

    suppliers = frozenset([Supplier("x" + str(i)) for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation("x" + str(i), "indicator") for i in {1, 2, 3}]))

    offerings = frozenset({Offering("x15", "x300", 0.5, 30), Offering("x413", "x5", 0.5, 30), Offering("x17", "x3", 0.5, 30)})

    deps = frozenset({RiskRelation("x1", "x3"), RiskRelation("x2", "x3"), RiskRelation("x5", "x6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    assert not sg.valid_values()


def test_mismatched_deps():
    components = frozenset([Component("x" + str(i)) for i in range(10)])

    suppliers = frozenset([Supplier("x" + str(i)) for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation("x" + str(i), "indicator") for i in {1, 2, 3}]))

    offerings = frozenset({Offering("x15", "x5", 0.5, 30), Offering("x16", "x5", 0.5, 30), Offering("x17", "x3", 0.5, 30)})

    deps = frozenset({RiskRelation("x100", "x3"), RiskRelation("x23", "x3"), RiskRelation("x5", "x6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    assert not sg.valid_values()


def test_overlapping_ids():
    components = frozenset([Component("x" + str(i)) for i in range(10)])

    suppliers = frozenset([Supplier("x" + str(i)) for i in range(15)])

    indicator = Indicator("and", frozenset([RiskRelation("x" + str(i), "indicator") for i in {1, 2, 3}]))

    offerings = frozenset({Offering("x15", "x5", 0.5, 30), Offering("x16", "x5", 0.5, 30), Offering("x17", "x3", 0.5, 30)})

    deps = frozenset({RiskRelation("x1", "x3"), RiskRelation("x2", "x3"), RiskRelation("x5", "x6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    assert not sg.valid_values()


def test_internally_overlapping_ids():
    components = set([Component("x" + str(i)) for i in range(10)])

    components.add(Component("x3", risk=0.4342))

    components = frozenset(components)

    suppliers = frozenset([Supplier("x" + str(i)) for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation("x" + str(i), "indicator") for i in {1, 2, 3}]))

    offerings = frozenset({Offering("x15", "x5", 0.5, 30), Offering("x16", "x5", 0.5, 30), Offering("x17", "x3", 0.5, 30)})

    deps = frozenset({RiskRelation("x1", "x3"), RiskRelation("x2", "x3"), RiskRelation("x5", "x6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    assert not sg.valid_values()


def test_hash_equal():
    components = frozenset([Component("x" + str(i)) for i in range(10)])

    suppliers = frozenset([Supplier("x" + str(i)) for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation("x" + str(i), "indicator") for i in {1, 2, 3}]))

    offerings = frozenset({Offering("x15", "x5", 0.5, 30), Offering("x16", "x5", 0.5, 30), Offering("x17", "x3", 0.5, 30)})

    deps = frozenset({RiskRelation("x1", "x3"), RiskRelation("x2", "x3"), RiskRelation("x5", "x6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    components_2 = frozenset([Component("x" + str(i)) for i in range(10)])

    suppliers_2 = frozenset([Supplier("x" + str(i)) for i in range(10, 20)])

    indicator_2 = Indicator("and", frozenset([RiskRelation("x" + str(i), "indicator") for i in {1, 2, 3}]))

    offerings_2 = frozenset({Offering("x15", "x5", 0.5, 30), Offering("x16", "x5", 0.5, 30), Offering("x17", "x3", 0.5, 30)})

    deps_2 = frozenset({RiskRelation("x1", "x3"), RiskRelation("x2", "x3"), RiskRelation("x5", "x6")})

    sg_2 = SystemGraph("test", components_2, suppliers_2, deps_2, offerings_2, indicator_2)

    assert id(sg) != id(sg_2)
    assert hash(sg) == hash(sg_2)


def test_hash_not_equal():
    components = frozenset([Component("x" + str(i)) for i in range(10)])

    suppliers = frozenset([Supplier("x" + str(i)) for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation("x" + str(i), "indicator") for i in {1, 2, 3}]))

    offerings = frozenset({Offering("x15", "x5", 0.5, 30), Offering("x16", "x5", 0.5, 30), Offering("x17", "x3", 0.5, 30)})

    deps = frozenset({RiskRelation("x1", "x3"), RiskRelation("x2", "x3"), RiskRelation("x5", "x6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    components_2 = frozenset([Component("x" + str(i)) for i in range(10)])

    suppliers_2 = frozenset([Supplier("x" + str(i)) for i in range(10, 20)])

    indicator_2 = Indicator("and", frozenset([RiskRelation("x" + str(i), "indicator") for i in {1, 2, 3}]))

    offerings_2 = frozenset({Offering("x15", "x5", 0.49, 30), Offering("x16", "x5", 0.5, 30), Offering("x17", "x3", 0.5, 30)})

    deps_2 = frozenset({RiskRelation("x1", "x3"), RiskRelation("x2", "x3"), RiskRelation("x5", "x6")})

    sg_2 = SystemGraph("test", components_2, suppliers_2, deps_2, offerings_2, indicator_2)

    assert id(sg) != id(sg_2)
    assert hash(sg) != hash(sg_2)


def test_structure_equal():
    components = frozenset([Component("x" + str(i)) for i in range(10)])

    suppliers = frozenset([Supplier("x" + str(i)) for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation("x" + str(i), "indicator") for i in {1, 2, 3}]))

    offerings = frozenset({Offering("x15", "x5", 0.5, 30), Offering("x16", "x5", 0.5, 30), Offering("x17", "x3", 0.5, 30)})

    deps = frozenset({RiskRelation("x1", "x3"), RiskRelation("x2", "x3"), RiskRelation("x5", "x6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    components_2 = frozenset([Component("x" + str(i)) for i in range(10)])

    suppliers_2 = frozenset([Supplier("x" + str(i)) for i in range(10, 20)])

    indicator_2 = Indicator("and", frozenset([RiskRelation("x" + str(i), "indicator") for i in {1, 2, 3}]))

    offerings_2 = frozenset({Offering("x15", "x5", 0.49, 30), Offering("x16", "x5", 0.5, 30), Offering("x17", "x3", 0.5, 30)})

    deps_2 = frozenset({RiskRelation("x1", "x3"), RiskRelation("x2", "x3"), RiskRelation("x5", "x6")})

    sg_2 = SystemGraph("test", components_2, suppliers_2, deps_2, offerings_2, indicator_2)

    assert id(sg) != id(sg_2)
    assert sg != sg_2
    assert hash(sg) != hash(sg_2)
    assert sg.structure() == sg_2.structure()


def test_structure_unequal():
    components = frozenset([Component("x" + str(i)) for i in range(10)])

    suppliers = frozenset([Supplier("x" + str(i)) for i in range(10, 20)])

    indicator = Indicator("and", frozenset([RiskRelation("x" + str(i), "indicator") for i in {1, 2, 3}]))

    offerings = frozenset({Offering("x15", "x5", 0.5, 30), Offering("x16", "x5", 0.5, 30), Offering("x17", "x3", 0.5, 30)})

    deps = frozenset({RiskRelation("x1", "x3"), RiskRelation("x2", "x3"), RiskRelation("x5", "x6")})

    sg = SystemGraph("test", components, suppliers, deps, offerings, indicator)

    components_2 = frozenset([Component("x" + str(i)) for i in range(10)])

    suppliers_2 = frozenset([Supplier("x" + str(i)) for i in range(10, 20)])

    indicator_2 = Indicator("and", frozenset([RiskRelation("x" + str(i), "indicator") for i in {1, 2, 3}]))

    offerings_2 = frozenset({Offering("x15", "x5", 0.5, 30), Offering("x16", "x5", 0.5, 30), Offering("x17", "x3", 0.5, 30)})

    deps_2 = frozenset({RiskRelation("x1", "x3"), RiskRelation("x2", "x3"), RiskRelation("x5", "x6"), RiskRelation("x15", "x3")})

    sg_2 = SystemGraph("test", components_2, suppliers_2, deps_2, offerings_2, indicator_2)

    assert id(sg) != id(sg_2)
    assert sg != sg_2
    assert hash(sg) != hash(sg_2)
    assert sg.structure() != sg_2.structure()


def test_apply_singular_offerings_basic(simple_and_suppliers: SystemGraph):
    assert simple_and_suppliers.valid_values()

    dep_count = len(simple_and_suppliers.security_dependencies)

    updated = apply_singular_offerings(simple_and_suppliers)

    assert updated.valid_values()

    updated_dep_count = len(updated.security_dependencies)

    assert dep_count + 3 == updated_dep_count

    c_1 = list(filter(lambda c: c.identifier == "one", updated.components))[0]

    assert c_1.risk == 0.25