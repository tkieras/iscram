import pytest

from iscram.domain.model import SystemGraph, Edge
from iscram.domain.optimization import SupplierChoiceProblem, OptimizationError
from iscram.domain.metrics.risk import risk_by_bdd
from iscram.domain.metrics.probability_providers import provide_p_direct_from_data


def test_init_supplier_choice_problem(full_with_supplier_choices: SystemGraph, full_with_supplier_choices_data):
    prob = SupplierChoiceProblem(full_with_supplier_choices, full_with_supplier_choices_data)
    assert prob is not None


def test_init_supplier_choice_solve(full_with_supplier_choices: SystemGraph, full_with_supplier_choices_data):
    prob = SupplierChoiceProblem(full_with_supplier_choices, full_with_supplier_choices_data)
    results = prob.solve({"alpha": 0.01, "budget": 500})
    assert results is not None


def test_supplier_choice_solve_bad_budget(full_with_supplier_choices: SystemGraph, full_with_supplier_choices_data):
    prob = SupplierChoiceProblem(full_with_supplier_choices, full_with_supplier_choices_data)
    with pytest.raises(OptimizationError):
        results = prob.solve({"alpha": 0.01, "budget": 1})


def test_e2e_supplier_choice_solve(full_with_supplier_choices: SystemGraph, full_with_supplier_choices_data):
    prob = SupplierChoiceProblem(full_with_supplier_choices, full_with_supplier_choices_data)
    results = prob.solve({"alpha": 0.01, "budget": 500})
    updated = full_with_supplier_choices.with_suppliers(results[0])
    assert updated is not None


def test_e2e_supplier_choice_solve_bad_supplier(full_with_supplier_choices: SystemGraph, full_with_supplier_choices_data):
    bad = full_with_supplier_choices_data["edges"][0]
    bad["risk"] = 0.99
    prob = SupplierChoiceProblem(full_with_supplier_choices, full_with_supplier_choices_data)
    results = prob.solve({"alpha": 0.01, "budget": 500})
    updated = full_with_supplier_choices.with_suppliers(results[0])
    assert Edge(src=bad["src"], dst=bad["dst"]) not in updated.edges


def test_e2e_supplier_choice_solve_bad_supplier_risk(full_with_supplier_choices: SystemGraph, full_with_supplier_choices_data):
    bad = full_with_supplier_choices_data["edges"][0]
    bad["risk"] = 0.99
    before = risk_by_bdd(full_with_supplier_choices, provide_p_direct_from_data(full_with_supplier_choices, full_with_supplier_choices_data))
    prob = SupplierChoiceProblem(full_with_supplier_choices, full_with_supplier_choices_data)
    results = prob.solve({"alpha": 0.01, "budget": 500})
    updated = full_with_supplier_choices.with_suppliers(results[0])
    assert Edge(src=bad["src"], dst=bad["dst"]) not in updated.edges
    after = risk_by_bdd(updated, provide_p_direct_from_data(updated, full_with_supplier_choices_data))
    assert before > after
