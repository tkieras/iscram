from iscram.domain.model import Component


def test_invalid_component():
    c = Component("", "or", 1.0, 30)

    assert not c.valid_values()

    c = Component("test", "f", 1.0, 30)

    assert not c.valid_values()

    c = Component("test", "or", 2.0, 30)

    assert not c.valid_values()

    c = Component("test", "or", -1.0, 30)

    assert not c.valid_values()

    c = Component("test", "or", 1.0, -5)

    assert not c.valid_values()


def test_valid_component():
    c = Component("test", "or", 0.0, 30)

    assert c.valid_values()

    c = Component("test", "and", 1.0, 30)

    assert c.valid_values()

    c = Component("test", "and", 1.0, 0)

    assert c.valid_values()