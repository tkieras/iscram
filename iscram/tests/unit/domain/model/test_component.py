from iscram.domain.model import Component


def test_invalid_component():
    c = Component(0, "", "or", 1.0, 30)

    assert not c.validate()

    c = Component(0, "test", "f", 1.0, 30)

    assert not c.validate()

    c = Component(0, "test", "or", 2.0, 30)

    assert not c.validate()

    c = Component(0, "test", "or", -1.0, 30)

    assert not c.validate()

    c = Component(0, "test", "or", 1.0, -5)

    assert not c.validate()


def test_valid_component():
    c = Component(0, "test", "or", 0.0, 30)

    assert c.validate()

    c = Component(0, "test", "and", 1.0, 30)

    assert c.validate()

    c = Component(0, "test", "and", 1.0, 0)

    assert c.validate()