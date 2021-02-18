from iscram.domain.model import Indicator, RiskRelation


def test_invalid_indicator():
    i = Indicator("xor", frozenset())

    assert not i.validate()

    i = Indicator("and", frozenset({RiskRelation(5, 5), RiskRelation(3, -1)}))

    assert not i.validate()


def test_valid_indicator():

    i = Indicator("and", frozenset({RiskRelation(5, -1), RiskRelation(3, -1), RiskRelation(4, -1)}))

    assert i.validate()

