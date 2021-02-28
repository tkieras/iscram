from iscram.domain.model import Indicator, RiskRelation


def test_invalid_indicator():
    i = Indicator("xor", frozenset())

    assert not i.valid_values()

    i = Indicator("and", frozenset({RiskRelation("five", "five"), RiskRelation("three", "indicator")}))

    assert not i.valid_values()


def test_valid_indicator():

    i = Indicator("and", frozenset({RiskRelation("five", "indicator"),
                                    RiskRelation("three", "indicator"),
                                    RiskRelation("four", "indicator")}))

    assert i.valid_values()

