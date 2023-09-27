# Code modified fom the code given at https://github.com/levii/dataclass-type-validator
import dataclasses
import typing
import functools
import sys
import collections
from typing import \
    Any, Callable, cast, Dict, ForwardRef, FrozenSet, get_type_hints, Iterable, List, Literal, \
    Optional, Protocol, runtime_checkable, Self, Set, Tuple, Type, TypedDict, TypeVar

GlobalNS_T = dict[str, Any]
_U = TypeVar("_U")

_CallableTypeReal = type(lambda a: a)

if typing.TYPE_CHECKING:
    class _UnionType(Protocol):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

    class _OptionalType(Protocol):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

    class _LiteralType(Protocol):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

    @runtime_checkable
    class _CallableType(Protocol):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

    @runtime_checkable
    class _GenericType(Protocol):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

        @property
        def __name__(self) -> str:
            pass

        @property
        def __origin__(self) -> type:
            pass

    @runtime_checkable
    class _GenericAlias(Protocol):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

        @property
        def __name__(self) -> str:
            pass

        @property
        def __origin__(self) -> type:
            pass

    class _Ellipsis(Protocol):
        pass

    class _CallableTypeFormal(Protocol):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

else:
    _UnionType = type(str | int)
    _OptionalType = type(Optional[int])
    _LiteralType = type(Literal[True])
    _GenericType = type(list[str])
    _GenericAlias = type(List[str])
    _Ellipsis = tuple[Any, ...].__args__[-1]
    _CallableTypeFormal = type(Callable[[], Any])


class TypeValidationError(Exception):
    """Exception raised on type validation errors.
    """

    def __init__(self: Self, *args: Any, target: _U, errors: dict[str, list[str]]) -> None:
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


def _validate_type(expected_type: type[Any], value: Any) -> list[str]:
    if expected_type is Any or isinstance(value, expected_type):
        return []
    return [f"must be an instance of type {expected_type}, but received {type(value)}"]


def _flatten(data: list[list[_U]]) -> list[_U]:
    d: list[_U] = []
    for p in data:
        d += p
    return d


def _validate_typing_iterable(field_name: str, expected_type: _GenericType, value: Any, globalns: GlobalNS_T) -> list[str]:
    if len(expected_type.__args__) != 1:
        raise TypeError(f"bad parameters for {expected_type}")

    if not isinstance(value, expected_type.__origin__):
        return [f"must be an instance of iterable type {expected_type.__origin__.__name__}, but received {type(value)}"]

    assert isinstance(value, Iterable)

    expected_item_type = expected_type.__args__[0]
    errors: list[str] = _flatten([_validate_types(field_name = field_name, expected_type = expected_item_type, value = v, globalns = globalns) for v in value])

    return errors


def _item_multiply(element: _U, times: int) -> list[_U]:
    return [element for x in range(0, times)]


def _validate_typing_tuple(field_name: str, expected_type: _GenericType, value: Any, globalns: GlobalNS_T) -> list[str]:
    if not isinstance(value, tuple):
        return [f"must be an instance of tuple, but received {type(value)}"]

    tvalue: tuple[Any, ...] = value

    types: list[type[Any]] = _type_resolve_all(expected_type.__args__, globalns)

    if len(types) == 2 and types[1] == _Ellipsis:
        types = _item_multiply(types[0], len(tvalue))

    elif len(tvalue) != len(types):
        return [f"must be an instance of {expected_type} with {len(types)} element{'s' if len(types) > 1 else ''}, but there {'are' if len(types) > 1 else 'is'} {len(types)} element{'s' if len(types) > 1 else ''}"]

    errors = []
    for k in range(0, len(types)):
        t: type[Any] = types[k]
        v: Any = value[k]
        z: list[str] = _validate_types(field_name = field_name, expected_type = types[k], value = value[k], globalns = globalns)
        errors.extend(z)

    return errors


def _validate_typing_dict_error_message(expected_type: _GenericType, key_errors: list[str], val_errors: list[str]) -> list[str]:
    if len(key_errors) > 0 and len(val_errors) > 0:
        return [f"must be an instance of {expected_type}, but there are some errors in keys and values. " \
            + f"key errors: {key_errors}, value errors: {val_errors}"]
    if len(key_errors) > 0:
        return [f"must be an instance of {expected_type}, but there are some errors in keys: {key_errors}"]
    if len(val_errors) > 0:
        return [f"must be an instance of {expected_type}, but there are some errors in values: {val_errors}"]
    return []


"""
def _validate_typing_typed_dict(expected_type: type[Any], value: Any) -> list[str]:
    if not isinstance(value, dict):
        return [f"must be an instance of dict, but received {type(value)}"]

    fields: dict[str, type] = get_type_hints(expected_type)
    common_fields : set[str] = set(fields.keys()).intersection(set(value.keys()))
    missing_fields: set[str] = set(fields.keys()).difference(set(value.keys()))
    extra_fields  : set[str] = set(value.keys()).difference(set(fields.keys()))

    return []
"""


def _validate_typing_dict(field_name: str, expected_type: _GenericType, value: Any, globalns: GlobalNS_T) -> list[str]:
    if len(expected_type.__args__) != 2:
        raise TypeError(f"bad parameters for {expected_type}")

    if not isinstance(value, dict):
        return [f"must be an instance of dict, but received {type(value)}"]

    expected_key_type  : type[Any] = _type_resolve(expected_type.__args__[0], globalns)
    expected_value_type: type[Any] = _type_resolve(expected_type.__args__[1], globalns)

    key_errors: list[str] = _flatten([_validate_types(field_name = field_name, expected_type = expected_key_type, value = k, globalns = globalns) for k in value.keys()])
    val_errors: list[str] = _flatten([_validate_types(field_name = field_name, expected_type = expected_value_type, value = v, globalns = globalns) for v in value.values()])

    return _validate_typing_dict_error_message(expected_type, key_errors, val_errors)


def _validate_parameters(names: list[str], reals: list[type[Any]], formals: list[type[Any]]) -> list[str]:
    errors: list[str] = []

    for k in range(0, len(reals) - 1):
        if formals[k] != reals[k]:
            errors.append(f"incompatible value for {names[k]}: expected {formals[k]} but was {reals[k]}")

    if formals[-1] != Any and formals[-1] != reals[-1]:
        errors.append(f"incompatible value for {names[-1]}: expected {formals[-1]} but was {reals[-1]}")

    return errors


def _validate_typing_callable(expected_type: _CallableTypeFormal, value: Any, globalns: GlobalNS_T) -> list[str]:
    if not isinstance(value, _CallableTypeReal):
        return [f"must be an instance of {expected_type.__str__()}, but received {type(value)}"]

    names  : list[str]       = list(value.__annotations__.keys())
    reals  : list[type[Any]] = _type_resolve_all(value.__annotations__.values(), globalns)
    formals: list[type[Any]] = _type_resolve_all(expected_type.__args__, globalns)

    if formals[0] == _Ellipsis:
        if formals[-1] == Any or formals[-1] == reals[-1]:
            return []

        error: str = f"incompatible value for {names[-1]}: expected {formals[-1]} but was {reals[-1]}"
        return [f"must be an instance of {expected_type}, but there are some errors in parameters or return types: {error}"]

    if len(reals) != len(formals):
        return [f"bad parameters - should be {formals} but are {reals}"]

    errors: list[str] = _validate_parameters(names, reals, formals)

    if errors:
        return [f"must be an instance of {expected_type}, but there are some errors in parameters or return types: {errors}"]

    return []


def _validate_typing_literal(expected_type: _LiteralType, value: Any) -> list[str]:
    if value in expected_type.__args__: return []
    return [f"must be one of [{', '.join([x.__str__() for x in expected_type.__args__])}] but received {value}"]


def _validate_union_types(field_name: str, expected_type: _UnionType | _OptionalType, value: Any, globalns: GlobalNS_T) -> list[str]:
    is_valid = any(_validate_types(field_name = field_name, expected_type = t, value = value, globalns = globalns) == [] for t in expected_type.__args__)
    if not is_valid:
        return [f"must be an instance of {expected_type}, but received {value}"]
    return []


_dict_values: type = type({}.values())
_dict_keys  : type = type({}.keys())


_validate_typing_mappings: dict[type, Callable[[str, _GenericType, Any, GlobalNS_T], list[str]]] = {
    tuple                   : _validate_typing_tuple,
    dict                    : _validate_typing_dict,
    list                    : _validate_typing_iterable,
    frozenset               : _validate_typing_iterable,
    set                     : _validate_typing_iterable,
    _dict_keys              : _validate_typing_iterable,
    _dict_values            : _validate_typing_iterable,
    collections.abc.Sequence: _validate_typing_iterable,
    collections.abc.Iterable: _validate_typing_iterable
}


def _type_resolve(x: type[Any] | ForwardRef | None, globalns: GlobalNS_T) -> type[Any]:
    if x is None:
        return type(None)
    if isinstance(x, ForwardRef):
        x = _evaluate_forward_reference(x, globalns)
    return x


def _type_resolve_all(types: Iterable[type[Any] | ForwardRef | None], globalns: GlobalNS_T) -> list[type[Any]]:
    return [_type_resolve(x, globalns) for x in types]


def _type_resolve_name(x: type[Any] | ForwardRef, globalns: GlobalNS_T) -> str:
    if x == type(None):
        return "None"
    if isinstance(x, ForwardRef):
        x = _evaluate_forward_reference(x, globalns)
    return x.__name__


def _type_resolve_all_names(types: Iterable[type[Any] | ForwardRef], globalns: GlobalNS_T) -> list[str]:
    return [_type_resolve_name(x, globalns) for x in types]


def _reduce_alias(alias: _GenericAlias, globalns: GlobalNS_T) -> _GenericType:
    origin: type = alias.__origin__
    module: str = origin.__module__
    short_name: str = origin.__name__
    new_globalns: GlobalNS_T = globalns

    full_name: str
    if module == "builtins":
        full_name = short_name
    elif module in new_globalns:
        full_name = module + "." + short_name
    else:
        new_globalns = globalns.copy()
        i: int = 1
        while f"temp_{i}" in new_globalns:
            i += 1
        var_name: str = f"temp_{i}"
        new_globalns[var_name] = eval(module)
        full_name = var_name + "." + short_name

    names: str = ",".join(_type_resolve_all_names(alias.__args__, new_globalns))
    new_name: str = full_name + "[" + names + "]"
    return cast(_GenericType, eval(new_name, new_globalns))


def _validate_types(field_name: str, expected_type: type[Any] | _GenericType | _GenericAlias | _UnionType | _OptionalType | _LiteralType | _CallableTypeFormal | ForwardRef | str, value: Any, globalns: GlobalNS_T) -> list[str]:

    reworked_type: Any = expected_type
    if type(expected_type) is str:
        reworked_type = eval(expected_type, globalns)

    if type(reworked_type) is _GenericAlias:
        reworked_type = _reduce_alias(reworked_type, globalns)

    if type(reworked_type) is _UnionType or type(reworked_type) is _OptionalType:
        return _validate_union_types(field_name = field_name, expected_type = reworked_type, value = value, globalns = globalns)

    if type(reworked_type) is _LiteralType:
        return _validate_typing_literal(expected_type = reworked_type, value = value)

    if isinstance(reworked_type, ForwardRef):
        referenced_type = _evaluate_forward_reference(reworked_type, globalns)
        return _validate_type(expected_type = referenced_type, value = value)

    if type(reworked_type) is _CallableTypeFormal:
        return _validate_typing_callable(expected_type = reworked_type, value = value, globalns = globalns)

    if isinstance(reworked_type, type):
        #if reworked_type.__origin__ == type(TypedDict):
        #    return _validate_typing_typed_dict(expected_type = reworked_type, value = value)
        return _validate_type(expected_type = reworked_type, value = value)

    if type(reworked_type) is _GenericType:
        raw_type: type = reworked_type.__origin__
        _g = _validate_typing_mappings.get(raw_type)
        if _g is None:
            return [f"Can't validate field {field_name} from {reworked_type} - unknown generic type"]
        return _g(field_name, reworked_type, value, globalns)

    return [f"Can't validate field {field_name} from {reworked_type} (type is {type(reworked_type).__name__}) with {value} (type is {type(value).__name__})"]


def _evaluate_forward_reference(ref_type: ForwardRef, globalns: GlobalNS_T) -> Type[Any]:
    """ Support evaluating ForwardRef types on both Python 3.8 and 3.9. """
    return cast(Type[Any], ref_type._evaluate(globalns, None, frozenset()))


def dataclass_type_validator(target: Any) -> None:
    fields = dataclasses.fields(target)
    globalns = sys.modules[target.__module__].__dict__.copy()

    errors: dict[str, list[str]] = {}
    for field in fields:
        field_name: str = field.name
        expected_type: Any = field.type
        value = getattr(target, field_name)

        field_errors: list[str] = _validate_types(field_name = field_name, expected_type = expected_type, value = value, globalns = globalns)
        if len(field_errors) > 0:
            errors[field_name] = field_errors

    if len(errors) > 0:
        raise TypeValidationError( \
            "Dataclass Type Validation Error", target = target, errors = errors \
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