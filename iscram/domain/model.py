from dataclasses import field
from typing import FrozenSet
from collections import defaultdict

from pydantic.dataclasses import dataclass

RESTRICTED_IDENTIFIER_CHARS = {"!", "@", "#", "$", "%", "^", "&", "*"}


def validate_identifier(identifier: str) -> bool:
    if len(identifier) == 0:
        return False
    if identifier == "indicator":
        return False
    return not identifier[0] in RESTRICTED_IDENTIFIER_CHARS


def validate_logic_function(logic_function: str) -> bool:
    return logic_function in ["and", "or"]


def validate_risk(risk: float) -> bool:
    return 0.0 <= risk <= 1.0


def validate_cost(cost: int) -> bool:
    return cost >= 0


@dataclass(frozen=True)
class Component:
    identifier: str
    logic_function: str = "and"
    risk: float = 0.0
    cost: int = 0

    def valid_values(self):
        return all([validate_identifier(self.identifier),
                    validate_logic_function(self.logic_function),
                    validate_risk(self.risk),
                    validate_cost(self.cost)])


@dataclass(frozen=True)
class Trait:
    key: str
    value: bool


@dataclass(frozen=True)
class Supplier:
    identifier: str
    trust: float = 1.0
    traits: FrozenSet[Trait] = field(default_factory=set)

    def valid_values(self):
        return all([validate_identifier(self.identifier),
                    validate_risk(self.trust)])


@dataclass(frozen=True)
class Offering:
    supplier_id: str
    component_id: str
    risk: float
    cost: int

    def valid_values(self):
        return all([self.supplier_id != self.component_id,
                    validate_risk(self.risk),
                    validate_cost(self.cost)])


@dataclass(frozen=True)
class RiskRelation:
    risk_src_id: str
    risk_dst_id: str


@dataclass(frozen=True)
class Indicator:
    logic_function: str
    dependencies: FrozenSet[RiskRelation] = field(default_factory=set)

    def valid_values(self):
        return all([all([d.risk_dst_id == "indicator" for d in self.dependencies]),
                    validate_logic_function(self.logic_function)])


@dataclass(frozen=True)
class SystemGraph:
    name: str
    components: FrozenSet[Component]
    suppliers: FrozenSet[Supplier]
    security_dependencies: FrozenSet[RiskRelation]
    offerings: FrozenSet[Offering]
    indicator: Indicator

    def valid_values(self) -> bool:
        parts = all([all([c.valid_values() for c in self.components]),
                     all([s.valid_values() for s in self.suppliers]),
                     all([o.valid_values() for o in self.offerings]),
                     ])

        valid_supplier_ids = set([s.identifier for s in self.suppliers])
        valid_component_ids = set([c.identifier for c in self.components])
        all_ids = valid_component_ids.union(valid_supplier_ids)

        valid_ids = all([len(self.components) == len(valid_component_ids),
                         len(self.suppliers) == len(valid_supplier_ids),
                         len(all_ids) == len(valid_component_ids) + len(valid_supplier_ids)])

        whole = all([all([o.supplier_id in valid_supplier_ids for o in self.offerings]),
                     all([o.component_id in valid_component_ids for o in self.offerings]),
                     all([d.risk_src_id in all_ids for d in self.security_dependencies]),
                     all([d.risk_dst_id in all_ids for d in self.security_dependencies]),
                     all([d.risk_src_id in all_ids for d in self.indicator.dependencies])
                     ])

        return parts and whole and valid_ids

    def structure(self) -> int:
        graph = defaultdict(list)
        for c in self.components:
            graph[c].append(c.identifier)
            graph[c].append(c.logic_function)

        for s in self.suppliers:
            graph[s].append(s.identifier)

        for e in self.security_dependencies:
            graph[e.risk_dst_id].append(e.risk_src_id)

        structure = frozenset([tuple(entry) for entry in graph.values()])

        return hash(structure)


def apply_singular_offerings(original: SystemGraph) -> SystemGraph:
    offering_map = {}
    for o in original.offerings:
        offerings_for_component = offering_map.get(o.component_id, [])
        offerings_for_component.append(o)
        offering_map[o.component_id] = offerings_for_component

    component_map = {}
    for c in original.components:
        component_map[c.identifier] = c

    updated_dependencies = []
    updated_components = []
    old_components = set(original.components)

    for component, offerings in offering_map.items():
        if len(offerings) == 1:
            offering = offerings[0]
            old_component = component_map[component]
            new_component = Component(component,
                                      old_component.logic_function,
                                      offering.risk,
                                      offering.cost)
            updated_components.append(new_component)
            updated_dependencies.append(RiskRelation(offering.supplier_id, component))
            old_components.remove(old_component)

    # transfer unchanged components
    for old_component in old_components:
        updated_components.append(old_component)

    updated_dependencies.extend(original.security_dependencies)

    new_sg = SystemGraph(
        original.name,
        frozenset(updated_components),
        original.suppliers,
        frozenset(updated_dependencies),
        original.offerings,
        original.indicator
    )

    return new_sg
