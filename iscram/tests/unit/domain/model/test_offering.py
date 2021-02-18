from iscram.domain.model import Offering


def test_invalid_offering():
    o = Offering(0, 0, 0.5, 30)

    assert not o.validate()

    o = Offering(0, 1, -1.0, 30)

    assert not o.validate()

    o = Offering(0, 1, 1.001, 30)

    assert not o.validate()

    o = Offering(0, 1, 0.5, -3)

    assert not o.validate()