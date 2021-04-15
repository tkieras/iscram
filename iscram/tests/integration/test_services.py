from typing import Dict
from pytest import approx

from iscram.domain.model import SystemGraph
from iscram.adapters.repository import FakeRepository
from iscram.service_layer import services
from iscram.tests.conftest import get_sg_from_file


def test_get_birnbaum_structural_importance(minimal: SystemGraph):
    repo = FakeRepository()
    bst_imps = services.get_birnbaum_structural_importances(minimal, repo, {"SCALE_METRICS": "NONE"})
    assert len(bst_imps) != 0


def test_get_birnbaum_importance(minimal: SystemGraph):
    repo = FakeRepository()
    data = {
        "nodes": {
            "x1": {"risk": 0.5},
            "x2": {"risk": 0.5},
            "x3": {"risk": 0.5}
        }
    }
    b_imps = services.get_birnbaum_importances(minimal, repo, data, data_src="data")
    assert len(b_imps) != 0


def test_select_attribute_no_suppliers(minimal: SystemGraph):
    repo = FakeRepository()
    data = {"nodes": {}}
    result = services.get_birnbaum_importances_select(minimal, repo, data, {"domestic": False}, "data")
    assert "birnbaum_importances_select_domestic_False" in result


def test_select_attribute_suppliers(diamond_suppliers: SystemGraph):
    repo = FakeRepository()
    data = {"nodes": {}}
    result = services.get_birnbaum_importances_select(diamond_suppliers, repo, data, {"domestic": False}, "data")
    assert "birnbaum_importances_select_domestic_False" in result
    assert result["birnbaum_importances_select_domestic_False"] == 0


def test_service_birnbaum_structural_importance_with_scaling(full_example_system: SystemGraph):
    repo = FakeRepository()
    b_imps = services.get_birnbaum_structural_importances(full_example_system, repo, {"SCALE_METRICS": "PROPORTIONAL"})
    assert len(b_imps) != 0
    assert approx(sum(b_imps.values()) == 1)


def test_service_birnbaum_structural_importance_with_no_scaling(full_example_system: SystemGraph):
    repo = FakeRepository()
    b_imps = services.get_birnbaum_structural_importances(full_example_system, repo, {"SCALE_METRICS": "NONE"})
    assert len(b_imps) != 0
    assert approx(sum(b_imps.values()) == 1)


def test_service_birnbaum_importance_with_scaling(full_example_system: SystemGraph, full_example_data_1: Dict):
    repo = FakeRepository()
    b_imps = services.get_birnbaum_importances(full_example_system, repo, full_example_data_1, "data", {"SCALE_METRICS": "PROPORTIONAL"})
    assert len(b_imps) != 0
    assert approx(sum(b_imps.values()) == 1)


def test_service_birnbaum_importance_with_no_scaling(full_example_system: SystemGraph, full_example_data_1: Dict):
    repo = FakeRepository()
    b_imps = services.get_birnbaum_importances(full_example_system, repo, full_example_data_1, "data", {"SCALE_METRICS": "NONE"})
    assert len(b_imps) != 0
    assert approx(sum(b_imps.values()) < 1)


def test_service_birnbaum_importance_default_scaling(full_example_system: SystemGraph, full_example_data_1: Dict):
    repo = FakeRepository()
    b_imps = services.get_birnbaum_importances(full_example_system, repo, full_example_data_1, "data")
    assert len(b_imps) != 0
    assert approx(max(b_imps.values()) == 1)
    assert approx(min(b_imps.values()) == 0)


def test_service_fractional_importance_traits_with_scaling(full_example_system: SystemGraph, full_example_data_1: Dict):
    f_imps = services.get_fractional_importance_traits(full_example_system, full_example_data_1, {"SCALE_METRICS": "PROPORTIONAL"})
    assert len(f_imps) != 0
    assert approx(sum(f_imps.values()) == 1)


def test_speed_importances_rand_tree_500():
    sg = get_sg_from_file("rand_system_graph_tree_500.json")
    repo = FakeRepository()
    assert services.get_birnbaum_structural_importances(sg, repo) is not None


def test_speed_importances_rand_tree_100():
    sg = get_sg_from_file("rand_system_graph_tree_100.json")
    repo = FakeRepository()
    assert services.get_birnbaum_structural_importances(sg, repo) is not None


def test_speed_importances_rand_tree_50():
    sg = get_sg_from_file("rand_system_graph_tree_50.json")
    repo = FakeRepository()
    assert services.get_birnbaum_structural_importances(sg, repo) is not None
