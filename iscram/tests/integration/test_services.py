from importlib.resources import read_text

from pytest import approx

from iscram.domain.model import SystemGraph, Trait

from iscram.adapters.repository import FakeRepository

from iscram.adapters.json import load_system_graph_json_str

from iscram.service_layer import services


def test_get_birnbaum_structural_importance(simple_and: SystemGraph):

    repo = FakeRepository()
    bst_imps = services.get_birnbaum_structural_importances(simple_and, repo, {"SCALE_METRICS": "NONE"})

    assert len(bst_imps) != 0


def test_get_birnbaum_importance(simple_and: SystemGraph):

    repo = FakeRepository()
    b_imps = services.get_birnbaum_importances(simple_and, repo)

    assert len(b_imps) != 0


def test_select_attribute_no_suppliers(full_example: SystemGraph):
    repo = FakeRepository()
    result = services.get_birnbaum_importances_select(full_example, Trait("domestic", False), repo)

    assert "birnbaum_importances_select_domestic_False" in result


def test_select_attribute_suppliers(simple_and_suppliers: SystemGraph):
    repo = FakeRepository()
    result = services.get_birnbaum_importances_select(simple_and_suppliers, Trait("domestic", False), repo)

    assert "birnbaum_importances_select_domestic_False" in result
    assert result["birnbaum_importances_select_domestic_False"] == 0


def test_service_birnbaum_structural_importance_with_scaling(full_example: SystemGraph):
    repo = FakeRepository()
    b_imps = services.get_birnbaum_structural_importances(full_example, repo, {"SCALE_METRICS": "PROPORTIONAL"})

    assert len(b_imps) != 0

    assert approx(sum(b_imps.values()) == 1)


def test_service_birnbaum_structural_importance_with_no_scaling(full_example: SystemGraph):
    repo = FakeRepository()
    b_imps = services.get_birnbaum_structural_importances(full_example, repo, {"SCALE_METRICS": "NONE"})

    assert len(b_imps) != 0

    assert approx(sum(b_imps.values()) == 1)


def test_service_birnbaum_importance_with_scaling(full_example: SystemGraph):
    repo = FakeRepository()
    b_imps = services.get_birnbaum_importances(full_example, repo, {"SCALE_METRICS": "PROPORTIONAL"})

    assert len(b_imps) != 0

    assert approx(sum(b_imps.values()) == 1)


def test_service_birnbaum_importance_with_no_scaling(full_example: SystemGraph):
    repo = FakeRepository()
    b_imps = services.get_birnbaum_importances(full_example, repo, {"SCALE_METRICS": "NONE"})

    assert len(b_imps) != 0

    assert approx(sum(b_imps.values()) < 1)


def test_service_birnbaum_importance_default_scaling(full_example: SystemGraph):
    repo = FakeRepository()
    b_imps = services.get_birnbaum_importances(full_example, repo)

    assert len(b_imps) != 0

    assert approx(max(b_imps.values()) == 1)
    assert approx(min(b_imps.values()) == 0)


def test_service_fractional_importance_traits_with_scaling(full_example: SystemGraph):
    f_imps = services.get_fractional_importance_traits(full_example, {"SCALE_METRICS": "PROPORTIONAL"})

    assert len(f_imps) != 0

    assert approx(sum(f_imps.values()) == 1)


def test_speed_importances_rand_tree_100():
    json_str = read_text("iscram.tests.system_graph_test_data", "random_tree_100.json")

    sg = load_system_graph_json_str(json_str)
    repo = FakeRepository()
    assert services.get_birnbaum_importances(sg, repo) is not None


def test_speed_importances_rand_tree_75():
    json_str = read_text("iscram.tests.system_graph_test_data", "random_tree_75.json")

    sg = load_system_graph_json_str(json_str)
    repo = FakeRepository()
    assert services.get_birnbaum_importances(sg, repo) is not None


def test_speed_importances_rand_tree_50():
    json_str = read_text("iscram.tests.system_graph_test_data", "random_tree_50.json")

    sg = load_system_graph_json_str(json_str)
    repo = FakeRepository()
    assert services.get_birnbaum_importances(sg, repo) is not None


def test_speed_importances_rand_tree_25():
    json_str = read_text("iscram.tests.system_graph_test_data", "random_tree_25.json")

    sg = load_system_graph_json_str(json_str)
    repo = FakeRepository()
    assert services.get_birnbaum_importances(sg, repo) is not None


def test_speed_importances_rand_tree_10():
    json_str = read_text("iscram.tests.system_graph_test_data", "random_tree_10.json")

    sg = load_system_graph_json_str(json_str)
    repo = FakeRepository()
    assert services.get_birnbaum_importances(sg, repo) is not None