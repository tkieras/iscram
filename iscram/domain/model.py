from dataclasses import dataclass, field
from typing import FrozenSet


def validate_name(name: str) -> bool:
    return len(name) > 0


def validate_logic_function(logic_function: str) -> bool:
    return logic_function in ["and", "or"]


def validate_risk(risk: float) -> bool:
    return 0.0 <= risk <= 1.0


def validate_cost(cost: int) -> bool:
    return cost >= 0


@dataclass(frozen=True)
class Component:
    identifier: int
    name: str
    logic_function: str = "and"
    risk: float = 0.0
    cost: int = 0

    def validate(self):
        return all([validate_name(self.name),
                    validate_logic_function(self.logic_function),
                    validate_risk(self.risk),
                    validate_cost(self.cost)])


@dataclass(frozen=True)
class Supplier:
    identifier: int
    name: str
    trust: float = 1.0

    def validate(self):
        return all([validate_name(self.name),
                    validate_risk(self.trust)])


@dataclass(frozen=True)
class Offering:
    supplier_id: int
    component_id: int
    risk: float
    cost: int

    def validate(self):
        return all([self.supplier_id != self.component_id,
                    validate_risk(self.risk),
                    validate_cost(self.cost)])


@dataclass(frozen=True)
class RiskRelation:
    risk_src_id: int
    risk_dst_id: int


@dataclass(frozen=True)
class Indicator:
    logic_function: str
    dependencies: FrozenSet[RiskRelation] = field(default_factory=set)

    def validate(self):
        return all([all([d.risk_dst_id == -1 for d in self.dependencies]),
                    validate_logic_function(self.logic_function)])


@dataclass(frozen=True)
class SystemGraph:
    name: str
    components: FrozenSet[Component]
    suppliers: FrozenSet[Supplier]
    security_dependencies: FrozenSet[RiskRelation]
    offerings: FrozenSet[Offering]
    indicator: Indicator

    def validate(self):
        parts = all([validate_name(self.name),
                     all([c.validate() for c in self.components]),
                     all([s.validate() for s in self.suppliers]),
                     all([o.validate() for o in self.offerings]),
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
