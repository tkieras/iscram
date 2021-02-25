from iscram.domain.model import SystemGraph

from iscram.adapters.repository import FakeRepository

from iscram.service_layer import services


def test_get_birnbaum_structural_importance(simple_and: SystemGraph):

    repo = FakeRepository()
    bst_imps = services.get_birnbaum_structural_importances(simple_and, repo)

    assert len(bst_imps) != 0


def test_get_birnbaum_importance(simple_and: SystemGraph):

    repo = FakeRepository()
    b_imps = services.get_birnbaum_importances(simple_and, repo)

    assert len(b_imps) != 0
