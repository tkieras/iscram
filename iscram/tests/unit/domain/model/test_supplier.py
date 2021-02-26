from iscram.domain.model import Supplier


def test_invalid_supplier():
    s = Supplier(0, "", 1.0)

    assert not s.valid_values()

    s = Supplier(0, "test", -1.0)

    assert not s.valid_values()

    s = Supplier(0, "test", 2.0)

    assert not s.valid_values()
