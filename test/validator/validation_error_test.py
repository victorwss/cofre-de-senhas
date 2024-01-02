from validator.errorset import SignalingErrorSet, make_error
from validator import TypeValidationError
from dataclasses import dataclass


@dataclass(frozen = True)
class Dummy:
    pass


def test_validation_error_basic_properties() -> None:
    e: SignalingErrorSet = make_error("bla")
    t: TypeValidationError = TypeValidationError("x", "y", "z", target = Dummy, errors = e)
    assert t.errors is e
    assert t.target_class is Dummy


def test_validation_error_basic_properties_with_instance() -> None:
    e: SignalingErrorSet = make_error("bla")
    t: TypeValidationError = TypeValidationError("x", "y", "z", target = Dummy(), errors = e)
    assert t.errors is e
    assert t.target_class is Dummy


def test_validation_error_str_repr() -> None:
    e: SignalingErrorSet = make_error("bla")
    t: TypeValidationError = TypeValidationError("x", "y", "z", target = Dummy, errors = e)
    assert f"{t}" == "test.validator.validation_error_test.Dummy (errors = : bla)"
    assert repr(t) == "test.validator.validation_error_test.Dummy('x', 'y', 'z', errors=_ErrorSetLeaf(error='bla'))"
