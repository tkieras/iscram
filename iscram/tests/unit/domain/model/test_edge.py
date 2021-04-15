import pytest
from pydantic.dataclasses import ValidationError
from iscram.domain.model import (
    Node, Edge, SystemGraph, validate_data
)



def test_valid_edge():
    e = Edge(src="x1", dst="x2")


def test_invalid_edge():
    with pytest.raises(ValidationError):
        e = Edge(src="1s", dst="x2")