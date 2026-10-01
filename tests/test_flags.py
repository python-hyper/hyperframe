import operator

from hyperframe.frame import (
    Flags, Flag,
)
import pytest


class TestFlags:
    def test_add(self):
        flags = Flags([Flag("VALID_FLAG", 0x00)])
        assert not flags

        flags.add("VALID_FLAG")
        flags.add("VALID_FLAG")
        assert "VALID_FLAG" in flags
        assert list(flags) == ["VALID_FLAG"]
        assert len(flags) == 1

    def test_remove(self):
        flags = Flags([Flag("VALID_FLAG", 0x00)])
        flags.add("VALID_FLAG")

        flags.discard("VALID_FLAG")
        assert "VALID_FLAG" not in flags
        assert list(flags) == []
        assert len(flags) == 0

        # discarding elements not in the set should not throw an exception
        flags.discard("END_STREAM")

    def test_validation(self):
        flags = Flags([Flag("VALID_FLAG", 0x00)])
        flags.add("VALID_FLAG")
        with pytest.raises(ValueError):
            flags.add("INVALID_FLAG")

    def test_repr(self):
        flags = Flags([Flag("VALID_FLAG", 0x00), Flag("OTHER_FLAG", 0x01)])
        assert repr(flags) == "[]"
        flags.add("VALID_FLAG")
        assert repr(flags) == "['VALID_FLAG']"
        flags.add("OTHER_FLAG")
        assert repr(flags) == "['OTHER_FLAG', 'VALID_FLAG']"


@pytest.mark.parametrize("operation, expected", [
    (operator.and_, {"FIRST"}),
    (operator.or_, {"FIRST", "SECOND", "OTHER"}),
    (operator.sub, {"SECOND"}),
    (operator.xor, {"SECOND", "OTHER"}),
])
@pytest.mark.parametrize("reflected", [False, True])
def test_set_operations(operation, expected, reflected):
    flags = Flags([Flag("FIRST", 0x01), Flag("SECOND", 0x02)])
    flags |= {"FIRST", "SECOND"}
    other = {"FIRST", "OTHER"}

    if reflected:
        result = operation(other, flags)
        if operation is operator.sub:
            expected = {"OTHER"}
    else:
        result = operation(flags, other)

    assert result == expected
    assert isinstance(result, set)
    assert flags == {"FIRST", "SECOND"}


@pytest.mark.parametrize("operation, expected", [
    (operator.iand, {"FIRST"}),
    (operator.isub, {"SECOND"}),
    (operator.ixor, {"SECOND"}),
    (operator.ior, {"FIRST", "SECOND"}),
])
def test_in_place_set_operations(operation, expected):
    flags = Flags([Flag("FIRST", 0x01), Flag("SECOND", 0x02)])
    flags |= {"FIRST", "SECOND"}

    result = operation(flags, {"FIRST"})

    assert result is flags
    assert flags == expected
    with pytest.raises(ValueError):
        flags.add("OTHER")


@pytest.mark.parametrize("operation", [operator.ior, operator.ixor])
def test_in_place_operations_reject_unknown_flags(operation):
    flags = Flags([Flag("FIRST", 0x01)])
    with pytest.raises(ValueError):
        operation(flags, {"OTHER"})


def test_empty_set_operation():
    flags = Flags([Flag("FIRST", 0x01)])
    result = flags & {"FIRST"}
    assert result == set()
    assert isinstance(result, set)
