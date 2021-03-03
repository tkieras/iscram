from iscram.domain.model import Offering


def test_invalid_offering():
    o = Offering("one", "one", 0.5, 30)

    assert not o.valid_values()

    o = Offering("zero", "one", -1.0, 30)

    assert not o.valid_values()

    o = Offering("zero", "one", 1.001, 30)

    assert not o.valid_values()

    o = Offering("zero", "one", 0.5, -3)

    assert not o.valid_values()