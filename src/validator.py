# Code modified fom the code given at https://github.com/levii/dataclass-type-validator
import dataclasses
import typing
import functools
import sys
from typing import Any, Callable, cast, ForwardRef, Self, Type, TypeVar

GlobalNS_T = dict[str, Any]
_U = TypeVar("_U")

class TypeValidationError(Exception):
    """Exception raised on type validation errors.
    """

    def __init__(self: Self, *args: Any, target: _U, errors: dict[str, str]) -> None:
        super(TypeValidationError, self).__init__(*args)
        self.class_ = target.__class__
        self.errors = errors

    def __repr__(self: Self) -> str:
        cls = self.class_
        cls_name = (
            f"{cls.__module__}.{cls.__name__}"
            if cls.__module__ != "__main__"
            else cls.__name__
        )
        attrs = ", ".join([repr(v) for v in self.args])
        return f"{cls_name}({attrs}, errors={repr(self.errors)})"

    def __str__(self: Self) -> str:
        cls = self.class_
        cls_name = (
            f"{cls.__module__}.{cls.__name__}"
            if cls.__module__ != "__main__"
            else cls.__name__
        )
        s = cls_name
        return f"{s} (errors = {self.errors})"


def _validate_type(expected_type: Type[Any], value: Any) -> str | None:
    if isinstance(value, expected_type): return None
    return f"must be an instance of {expected_type}, but received {type(value)}"


def _validate_iterable_items(expected_type: Type[Any], value: Any, globalns: GlobalNS_T) -> str | None:
    expected_item_type = expected_type.__args__[0]
    errors = [_validate_types(expected_type = expected_item_type, value = v, globalns = globalns)
              for v in value]
    errors = [x for x in errors if x]
    if len(errors) == 0: return None
    return f"must be an instance of {expected_type}, but there are some errors: {errors}"


def _validate_typing_list(expected_type: Type[Any], value: Any, globalns: GlobalNS_T) -> str | None:
    if not isinstance(value, list): return f"must be an instance of list, but received {type(value)}"
    return _validate_iterable_items(expected_type, value, globalns)


def _validate_typing_tuple(expected_type: Type[Any], value: Any, globalns: GlobalNS_T) -> str | None:
    if not isinstance(value, tuple): return f"must be an instance of tuple, but received {type(value)}"
    return _validate_iterable_items(expected_type, value, globalns)


def _validate_typing_frozenset(expected_type: Type[Any], value: Any, globalns: GlobalNS_T) -> str | None:
    if not isinstance(value, frozenset): return f"must be an instance of frozenset, but received {type(value)}"
    return _validate_iterable_items(expected_type, value, globalns)


def _validate_typing_dict(expected_type: Type[Any], value: Any, globalns: GlobalNS_T) -> str | None:
    if not isinstance(value, dict): return f"must be an instance of dict, but received {type(value)}"

    expected_key_type = expected_type.__args__[0]
    expected_value_type = expected_type.__args__[1]

    key_errors = [_validate_types(expected_type = expected_key_type, value = k, globalns = globalns)
                  for k in value.keys()]
    key_errors = [k for k in key_errors if k]

    val_errors = [_validate_types(expected_type = expected_value_type, value = v, globalns = globalns)
                  for v in value.values()]
    val_errors = [v for v in val_errors if v]

    if len(key_errors) > 0 and len(val_errors) > 0:
        return f"must be an instance of {expected_type}, but there are some errors in keys and values. "\
            f"key errors: {key_errors}, value errors: {val_errors}"
    if len(key_errors) > 0:
        return f"must be an instance of {expected_type}, but there are some errors in keys: {key_errors}"
    if len(val_errors) > 0:
        return f"must be an instance of {expected_type}, but there are some errors in values: {val_errors}"
    return None


def _validate_typing_callable(expected_type: Type[Any], value: Any, globalns: GlobalNS_T) -> str | None:
    if isinstance(value, type(lambda a: a)): return None
    return f"must be an instance of {expected_type._name}, but received {type(value)}"


def _validate_typing_literal(expected_type: Type[Any], value: Any) -> str | None:
    if value in expected_type.__args__: return None
    return f"must be one of [{', '.join(expected_type.__args__)}] but received {value}"


_validate_typing_mappings = {
    "List": _validate_typing_list,
    "list": _validate_typing_list,
    "Tuple": _validate_typing_tuple,
    "FrozenSet": _validate_typing_frozenset,
    "Dict": _validate_typing_dict,
    "dict": _validate_typing_dict,
    "Callable": _validate_typing_callable,
}


def _validate_sequential_types(expected_type: Type[Any], value: Any, globalns: GlobalNS_T) -> str | None:
    validate_func = _validate_typing_mappings.get(expected_type._name)
    if validate_func is not None:
        return validate_func(expected_type, value, globalns)

    if str(expected_type).startswith("typing.Literal"):
        return _validate_typing_literal(expected_type, value)

    if str(expected_type).startswith("typing.Union") or str(expected_type).startswith("typing.Optional"):
        is_valid = any(_validate_types(expected_type = t, value = value, globalns = globalns) is None
                       for t in expected_type.__args__)
        if not is_valid:
            return f"must be an instance of {expected_type}, but received {value}"
        return None

    raise RuntimeError(f"Unknown type of {expected_type} (_name = {expected_type._name})")


def _validate_types(expected_type: Type[Any], value: Any, globalns: GlobalNS_T) -> str | None:
    if isinstance(expected_type, type):
        return _validate_type(expected_type = expected_type, value = value)

    if isinstance(expected_type, typing._GenericAlias):
        return _validate_sequential_types(expected_type = expected_type, value = value, globalns = globalns)

    if isinstance(expected_type, ForwardRef):
        referenced_type = _evaluate_forward_reference(expected_type, globalns)
        return _validate_type(expected_type = referenced_type, value = value)

    return None


def _evaluate_forward_reference(ref_type: ForwardRef, globalns: GlobalNS_T) -> Type[Any]:
    """ Support evaluating ForwardRef types on both Python 3.8 and 3.9. """
    return cast(Type[Any], ref_type._evaluate(globalns, None, frozenset()))


def dataclass_type_validator(target: Any) -> None:
    fields = dataclasses.fields(target)
    globalns = sys.modules[target.__module__].__dict__.copy()

    errors = {}
    for field in fields:
        field_name = field.name
        expected_type = field.type
        value = getattr(target, field_name)

        err = _validate_types(expected_type = expected_type, value = value, globalns = globalns)
        if err is not None:
            errors[field_name] = err

    if len(errors) > 0:
        raise TypeValidationError(
            "Dataclass Type Validation Error", target = target, errors = errors
        )


def dataclass_validate(cls: Type[_U] | None = None) -> Type[_U] | Callable[[Type[_U]], Type[_U]]:
    """Dataclass decorator to automatically add validation to a dataclass.
    So you don't have to add a __post_init__ method, or if you have one, you don't have
    to remember to add the dataclass_type_validator(self) call to it; just decorate your
    dataclass with this instead.
    """
    if cls is None: return _dataclass_full_validate
    return _dataclass_full_validate(cls)


def _dataclass_full_validate(cls: Type[_U]) -> Type[_U]:

    if not hasattr(cls, "__post_init__"):
        # No post-init method, so no processing.  Wrap the constructor instead.
        wrapped_method_name = "__init__"
    else:
        # Make validation take place at the end of __post_init__
        wrapped_method_name = "__post_init__"

    call_post_type_validate = hasattr(cls, "__post_type_validate__")

    orig_method = getattr(cls, wrapped_method_name)

    # Normal case - call validator at the end of __init__ or __post_init__.
    @functools.wraps(orig_method)
    def method_wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        x = orig_method(self, *args, **kwargs)
        dataclass_type_validator(self)
        if call_post_type_validate: self.__post_type_validate__()
        return x

    setattr(cls, "__init__", method_wrapper)

    return cls