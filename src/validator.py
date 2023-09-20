# Code modified fom the code given at https://github.com/levii/dataclass-type-validator
import dataclasses
import typing
import functools
import sys
from typing import Any, Callable, cast, ForwardRef, Literal, Optional, Protocol, runtime_checkable, Self, Type, TypeVar

GlobalNS_T = dict[str, Any]
_U = TypeVar("_U")

_CallableTypeReal = type(lambda a: a)
_NoneType = type(None)

if typing.TYPE_CHECKING:
    class _UnionType(Protocol):
        @property
        def __args__(self) -> list[type[Any]]:
            pass

    class _OptionalType(Protocol):
        @property
        def __args__(self) -> list[type[Any]]:
            pass

    class _LiteralType(Protocol):
        @property
        def __args__(self) -> list[type[Any]]:
            pass

    @runtime_checkable
    class _CallableType(Protocol):
        @property
        def __args__(self) -> list[type[Any]]:
            pass

    @runtime_checkable
    class _GenericType(Protocol):
        @property
        def __args__(self) -> list[type[Any]]:
            pass

    class _Ellipsis(Protocol):
        pass

    class _CallableTypeFormal(Protocol):
        @property
        def __args__(self) -> list[type[Any]]:
            pass

else:
    _UnionType = type(str | int)
    _OptionalType = type(Optional[int])
    _LiteralType = type(Literal[True])
    _GenericType = type(list[str])
    _Ellipsis = tuple[Any, ...].__args__[-1]
    _CallableTypeFormal = type(Callable[[], Any])

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


def _validate_type(expected_type: type[Any], value: Any) -> str | None:
    if expected_type is Any or isinstance(value, expected_type):
        return None
    return f"must be an instance of {expected_type}, but received {type(value)}"


def _validate_iterable_items(expected_type: _GenericType, value: Any, globalns: GlobalNS_T) -> str | None:
    if len(expected_type.__args__) != 1:
        return f"bad parameters for {expected_type}"
    expected_item_type = expected_type.__args__[0]
    errors = _filter_nones_out([_validate_types(expected_type = expected_item_type, value = v, globalns = globalns) for v in value])
    if len(errors) == 0:
        return None
    return f"must be an instance of {expected_type}, but there are some errors: {errors}"


def _validate_typing_list(expected_type: _GenericType, value: Any, globalns: GlobalNS_T) -> str | None:
    if not isinstance(value, list):
        return f"must be an instance of list, but received {type(value)}"
    return _validate_iterable_items(expected_type, value, globalns)


def _validate_typing_tuple(expected_type: _GenericType, value: Any, globalns: GlobalNS_T) -> str | None:
    if not isinstance(value, tuple):
        return f"must be an instance of tuple, but received {type(value)}"

    types: list[type[Any]] = list(expected_type.__args__[:])

    if len(types) == 2 and types[1] == _Ellipsis:
        if len(value) == 0:
            return None
        types.pop()
        while len(types) < len(value):
            types.append(types[0])

    elif len(value) != len(types):
        return f"must be an instance of {expected_type}, but there aren't enough elements"

    errors = []
    for k in range(0, len(types)):
        t = types[k]
        v = value[k]
        z = _validate_types(expected_type = types[k], value = value[k], globalns = globalns)
        if z: errors.append(z)

    if len(errors) == 0: return None
    return f"must be an instance of {expected_type}, but there are some errors: {errors}"


def _validate_typing_frozenset(expected_type: _GenericType, value: Any, globalns: GlobalNS_T) -> str | None:
    if not isinstance(value, frozenset): return f"must be an instance of frozenset, but received {type(value)}"
    return _validate_iterable_items(expected_type, value, globalns)


def _filter_nones_out(some_list: list[_U | None]) -> list[_U]:
    return [v for v in some_list if v]


def _validate_typing_dict(expected_type: _GenericType, value: Any, globalns: GlobalNS_T) -> str | None:
    if not isinstance(value, dict):
        return f"must be an instance of dict, but received {type(value)}"
    if len(expected_type.__args__) != 2:
        return f"bad parameters for {expected_type}"

    expected_key_type  : type[Any] = expected_type.__args__[0]
    expected_value_type: type[Any] = expected_type.__args__[1]

    key_errors: list[str] = _filter_nones_out([_validate_types(expected_type = expected_key_type, value = k, globalns = globalns) for k in value.keys()])
    val_errors: list[str] = _filter_nones_out([_validate_types(expected_type = expected_value_type, value = v, globalns = globalns) for v in value.values()])

    if len(key_errors) > 0 and len(val_errors) > 0:
        return f"must be an instance of {expected_type}, but there are some errors in keys and values. "\
            f"key errors: {key_errors}, value errors: {val_errors}"
    if len(key_errors) > 0:
        return f"must be an instance of {expected_type}, but there are some errors in keys: {key_errors}"
    if len(val_errors) > 0:
        return f"must be an instance of {expected_type}, but there are some errors in values: {val_errors}"
    return None


def _validate_parameters(names: list[str], reals: list[type[Any]], formals: list[type[Any] | None]) -> list[str]:
    errors: list[str] = []

    for k in range(0, len(reals) - 1):
        if formals[k] != reals[k]:
            errors.append(f"incompatible value for {names[k]}: expected {formals[k]} but was {reals[k]}")

    if formals[-1] != Any and formals[-1] != reals[-1]:
        errors.append(f"incompatible value for {names[-1]}: expected {formals[-1]} but was {reals[-1]}")

    return errors


def _validate_typing_callable(expected_type: _CallableTypeFormal, value: Any, globalns: GlobalNS_T) -> str | None:
    if not isinstance(value, _CallableTypeReal):
        return f"must be an instance of {expected_type.__str__()}, but received {type(value)}"

    names  : list[str]              = list(value.__annotations__.keys())
    reals  : list[type[Any]]        = list(value.__annotations__.values())
    formals: list[type[Any] | None] = [None if k == _NoneType else k for k in expected_type.__args__] # type: ignore [comparison-overlap]

    if formals[0] == _Ellipsis:
        if formals[-1] == Any or formals[-1] == reals[-1]:
            return None

        error: str = f"incompatible value for {names[-1]}: expected {formals[-1]} but was {reals[-1]}"
        return f"must be an instance of {expected_type}, but there are some errors in parameters or return types: {error}"

    if len(reals) != len(formals):
        return f"bad parameters - should be {formals} but are {reals}"

    errors: list[str] = _validate_parameters(names, reals, formals)

    if errors:
        return f"must be an instance of {expected_type}, but there are some errors in parameters or return types: {errors}"

    return None


def _validate_typing_literal(expected_type: _LiteralType, value: Any) -> str | None:
    if value in expected_type.__args__: return None
    return f"must be one of [{', '.join([x.__str__() for x in expected_type.__args__])}] but received {value}"


def _validate_union_types(expected_type: _UnionType | _OptionalType, value: Any, globalns: GlobalNS_T) -> str | None:
    is_valid = any(_validate_types(expected_type = t, value = value, globalns = globalns) is None for t in expected_type.__args__)
    if not is_valid:
        return f"must be an instance of {expected_type}, but received {value}"
    return None


_validate_typing_mappings: dict[str, Callable[[_GenericType, Any, GlobalNS_T], str | None]] = {
    "List": _validate_typing_list,
    "list": _validate_typing_list,
    "Tuple": _validate_typing_tuple,
    "tuple": _validate_typing_tuple,
    "FrozenSet": _validate_typing_frozenset,
    "frozenset": _validate_typing_frozenset,
    "Dict": _validate_typing_dict,
    "dict": _validate_typing_dict
}


def _validate_types(expected_type: type[Any] | _GenericType | _UnionType | _OptionalType | _LiteralType | _CallableTypeFormal | ForwardRef, value: Any, globalns: GlobalNS_T) -> str | None:
    name: str = f"{expected_type}"
    if "[" in name:
        name = name[0 : name.index("[")]

    if type(expected_type) is _UnionType or type(expected_type) is _OptionalType:
        return _validate_union_types(expected_type = expected_type, value = value, globalns = globalns)

    if type(expected_type) is _LiteralType:
        return _validate_typing_literal(expected_type = expected_type, value = value)

    if isinstance(expected_type, ForwardRef):
        referenced_type = _evaluate_forward_reference(expected_type, globalns)
        return _validate_type(expected_type = referenced_type, value = value)

    if type(expected_type) is _CallableTypeFormal:
        return _validate_typing_callable(expected_type = expected_type, value = value, globalns = globalns)

    if isinstance(expected_type, type):
        return _validate_type(expected_type = expected_type, value = value)

    if type(expected_type) is _GenericType:
        _g = _validate_typing_mappings.get(name)
        if _g is not None:
            return _g(expected_type, value, globalns)

    return f"Can't validate {expected_type} of {expected_type.__class__} with {value} - {type(value)}"


def _evaluate_forward_reference(ref_type: ForwardRef, globalns: GlobalNS_T) -> Type[Any]:
    """ Support evaluating ForwardRef types on both Python 3.8 and 3.9. """
    return cast(Type[Any], ref_type._evaluate(globalns, None, frozenset()))


def dataclass_type_validator(target: Any) -> None:
    fields = dataclasses.fields(target)
    globalns = sys.modules[target.__module__].__dict__.copy()

    errors: dict[str, str] = {}
    for field in fields:
        field_name: str = field.name
        expected_type: Any = field.type
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