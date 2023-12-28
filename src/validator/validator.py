# Code modified fom the code given at https://github.com/levii/dataclass-type-validator
import functools
import sys
import collections
import dataclasses
from dataclasses import dataclass
from .typezoo import (
    TT1, TT2, TT3, UnionType, OptionalType, LiteralType, GenericType,
    GenericAlias, EllipsisType, CallableTypeFormal, TypedDictType,
    CallableTypeRealUserDefined, CallableTypeRealBuiltIn
)
from .errorset import ErrorSet, SignalingErrorSet, make_error, make_errors, no_error, bad_ellipsis, to_error, split_errors, split_valids
from typing import (
    Any, Callable, cast, ForwardRef, get_type_hints, Iterable,
    override, TYPE_CHECKING
)
from typing import Generic, TypeVar  # Delete when PEP 695 is ready.

if TYPE_CHECKING:  # pragma: no cover
    from _typeshed import DataclassInstance
    _D = TypeVar("_D", bound = DataclassInstance)
else:
    _D = TypeVar("_D")

NS_T = dict[str, Any]
_U = TypeVar("_U")  # Delete when PEP 695 is ready.
_T = TypeVar("_T", bound = TT2, covariant = True)  # Delete when PEP 695 is ready.


class TypeValidationError(TypeError):
    """Exception raised on type validation errors.
    """

    def __init__(self, *args: Any, target: Any, errors: SignalingErrorSet) -> None:
        super(TypeValidationError, self).__init__(*args)

        cls: type[Any] = target.__class__
        cls_name: str = f"{cls.__module__}.{cls.__name__}" if cls.__module__ != "__main__" else cls.__name__
        attrs: str = ", ".join([repr(v) for v in self.args])

        self.__target_class: type[Any] = cls
        self.__errors: SignalingErrorSet = errors
        self.__r = f"{cls_name}({attrs}, errors={repr(errors)})"
        self.__s = f"{cls_name} (errors = {errors})"

    @property
    def errors(self) -> SignalingErrorSet:
        return self.__errors

    @property
    def target_class(self) -> type[Any]:
        return self.__target_class

    @override
    def __repr__(self) -> str:
        return self.__r

    @override
    def __str__(self) -> str:
        return self.__s


def _validate_simple_type(expected_type: type[Any], value: Any, globalns: NS_T) -> ErrorSet:
    if expected_type is Any or isinstance(value, expected_type):
        return no_error
    return make_error(f"must be an instance of type {expected_type}, but received {type(value)}")


def _validate_typing_iterable_without_values(expected_type: GenericType, globalns: NS_T) -> ErrorSet:
    if len(expected_type.__args__) != 1:
        return make_error(f"bad parameters for {expected_type}")

    expected_item_type = expected_type.__args__[0]
    return _validate_types_without_values(expected_item_type, globalns)


def _validate_typing_iterable_with_values(expected_type: GenericType, value: Any, globalns: NS_T) -> ErrorSet:
    es: ErrorSet = _validate_typing_iterable_without_values(expected_type, globalns)

    if isinstance(es, SignalingErrorSet):
        return es

    if len(expected_type.__args__) != 1:
        return make_error(f"bad parameters for {expected_type}")

    if not isinstance(value, expected_type.__origin__):
        return make_error(f"must be an instance of iterable type {expected_type.__origin__.__name__}, but received {type(value)}")

    assert isinstance(value, Iterable)

    expected_item_type = expected_type.__args__[0]
    return make_errors([_validate_types_with_values(expected_item_type, v, globalns) for v in value])


# def _item_multiply[U](element: U, times: int) -> list[U]: # PEP 695
def _item_multiply(element: _U, times: int) -> list[_U]:
    return [element for x in range(0, times)]


def _validate_join_without_values(types2: list[TT2], globalns: NS_T) -> list[ErrorSet]:
    return [_validate_types_without_values(types2[k], globalns) for k in range(0, len(types2))]


def _validate_join_with_values(types2: list[TT2], tvalue: tuple[Any, ...], globalns: NS_T) -> list[ErrorSet]:
    return [_validate_types_with_values(types2[k], tvalue[k], globalns) for k in range(0, len(types2))]


def _validate_typing_tuple_without_values_in(expected_type: GenericType, globalns: NS_T) -> SignalingErrorSet | tuple[list[TT2], bool]:
    types: list[SignalingErrorSet | TT2] = _type_resolve_all(expected_type.__args__, globalns)

    is_ellipsis = len(types) == 2 and types[1] is EllipsisType
    if is_ellipsis:
        types = [types[0]]

    error_types: ErrorSet = split_errors(types)
    if isinstance(error_types, SignalingErrorSet):
        return error_types

    types2: list[TT2] = split_valids(types)
    assert len(types2) == len(types)

    errors: list[ErrorSet] = _validate_join_without_values(types2, globalns)
    es: ErrorSet = make_errors(errors)
    if isinstance(es, SignalingErrorSet):
        return es

    return (types2, is_ellipsis)


def _validate_typing_tuple_without_values(expected_type: GenericType, globalns: NS_T) -> ErrorSet:
    x: SignalingErrorSet | tuple[list[TT2], bool] = _validate_typing_tuple_without_values_in(expected_type, globalns)
    if isinstance(x, SignalingErrorSet):
        return x
    return no_error


def _validate_typing_tuple_with_values(expected_type: GenericType, value: Any, globalns: NS_T) -> ErrorSet:
    typecheck: SignalingErrorSet | tuple[list[TT2], bool] = _validate_typing_tuple_without_values_in(expected_type, globalns)
    if isinstance(typecheck, SignalingErrorSet):
        return typecheck

    if not isinstance(value, tuple):
        return make_error(f"must be an instance of tuple, but received {type(value)}")

    tvalue: tuple[Any, ...] = value

    types: list[TT2] = typecheck[0]
    if typecheck[1]:
        types = _item_multiply(types[0], len(tvalue))

    if len(tvalue) != len(types):
        s: str = "s" if len(types) > 1 else ""
        r: str = "are" if len(types) > 1 else "is"
        return make_error(f"must be an instance of {expected_type} with {len(types)} element{s}, but there {r} {len(types)} element{s}")

    errors: list[ErrorSet] = _validate_join_with_values(types, value, globalns)
    return make_errors(errors)


def _validate_typing_typed_dict_without_values_in(expected_type: TypedDictType, globalns: NS_T) -> SignalingErrorSet | dict[str, type]:
    fields: dict[str, type]

    try:
        fields = get_type_hints(expected_type)
    except NameError as xxx:
        return make_error(f"{xxx.name} couldn't be understood in {expected_type}")

    errors: dict[str, ErrorSet] = {f: _validate_types_without_values(fields[f], globalns) for f in fields}

    es: ErrorSet = make_errors(errors)
    if isinstance(es, SignalingErrorSet):
        return es
    return fields


def _validate_typing_typed_dict_without_values(expected_type: TypedDictType, globalns: NS_T) -> ErrorSet:
    part: SignalingErrorSet | dict[str, type] = _validate_typing_typed_dict_without_values_in(expected_type, globalns)
    if isinstance(part, SignalingErrorSet):
        return part
    return no_error


def _validate_typing_typed_dict_with_values(expected_type: TypedDictType, value: Any, globalns: NS_T) -> ErrorSet:
    part: SignalingErrorSet | dict[str, type] = _validate_typing_typed_dict_without_values_in(expected_type, globalns)

    if isinstance(part, ErrorSet):
        return part

    if not isinstance(value, dict):
        return make_error(f"must be an instance of TypedDict, but received {type(value)}")

    fields: dict[str, type] = part
    errors: dict[str, ErrorSet] = {}

    common_fields    : set[str] = set(fields.keys()).intersection(set(value .keys()))  # noqa: E202,E203,E211
    missing_fields   : set[str] = set(fields.keys()).difference  (set(value .keys()))  # noqa: E202,E203,E211
    unexpected_fields: set[str] = set(value .keys()).difference  (set(fields.keys()))  # noqa: E202,E203,E211

    for f in missing_fields:
        errors[f] = make_error(f"field {f} is missing in {expected_type}")

    for f in unexpected_fields:
        errors[f] = make_error(f"field {f} is unexpected in {expected_type}")

    for f in common_fields:
        errors[f] = _validate_types_with_values(fields[f], value[f], globalns)

    return make_errors(errors)


def _validate_typing_dict_without_values_in(expected_type: GenericType, globalns: NS_T) -> SignalingErrorSet | tuple[TT2, TT2]:
    if len(expected_type.__args__) != 2:
        return make_error(f"bad parameters for {expected_type}")

    expected_key_type  : SignalingErrorSet | TT2 = _type_resolve(expected_type.__args__[0], globalns)  # noqa: E203
    expected_value_type: SignalingErrorSet | TT2 = _type_resolve(expected_type.__args__[1], globalns)  # noqa: E203

    bad: dict[str, ErrorSet] = {
        "key": to_error(expected_key_type),
        "value": to_error(expected_value_type)
    }
    bad2: ErrorSet = make_errors(bad)
    if isinstance(bad2, SignalingErrorSet):
        return bad2

    assert not isinstance(expected_key_type, ErrorSet)
    assert not isinstance(expected_value_type, ErrorSet)
    assert expected_key_type != EllipsisType
    assert expected_value_type != EllipsisType

    return (expected_key_type, expected_value_type)


def _validate_typing_dict_without_values(expected_type: GenericType, globalns: NS_T) -> ErrorSet:
    x: SignalingErrorSet | tuple[TT2, TT2] = _validate_typing_dict_without_values_in(expected_type, globalns)
    if isinstance(x, SignalingErrorSet):
        return x
    return no_error


def _validate_typing_dict_with_values(expected_type: GenericType, value: Any, globalns: NS_T) -> ErrorSet:
    es: SignalingErrorSet | tuple[TT2, TT2] = _validate_typing_dict_without_values_in(expected_type, globalns)

    if isinstance(es, SignalingErrorSet):
        return es

    expected_key_type: TT2 = es[0]
    expected_value_type: TT2 = es[1]

    if not isinstance(value, dict):
        return make_error(f"must be an instance of dict, but received {type(value)}")

    errors: dict[str, ErrorSet] = {}

    keys: list[Any] = list(value.keys())
    for idx in range(0, len(keys)):
        key: Any = keys[idx]
        errors[f"key {key} ({idx})"] = _validate_types_with_values(expected_key_type, key, globalns)

    for k in value.keys():
        vkey: Any = keys[idx]
        value2: Any = value[keys[idx]]
        errors[f"value {value2} for {vkey} ({idx})"] = _validate_types_with_values(expected_value_type, value2, globalns)

    return make_errors(errors)


def _validate_parameter(real: TT2, formal: TT2, check_any: bool) -> ErrorSet:
    if (not check_any or formal != Any) and formal != real:
        return make_error(f"expected {formal} but was {real}")
    return no_error


def _validate_parameters(names: list[str], reals: list[TT2], formals: list[TT2], is_ellipsis: bool) -> ErrorSet:
    errors: dict[str, ErrorSet] = {}

    if not is_ellipsis:
        for k in range(0, len(reals) - 1):
            errors[names[k]] = _validate_parameter(reals[k], formals[k], False)
    errors[names[-1]] = _validate_parameter(reals[-1], formals[-1], True)

    return make_errors(errors)


def _validate_typing_callable_without_values_in(expected_type: CallableTypeFormal, globalns: NS_T) -> SignalingErrorSet | tuple[list[TT2], bool]:
    formals: list[SignalingErrorSet | TT2] = _type_resolve_all(expected_type.__args__, globalns)
    is_ellipsis: bool = len(formals) == 2 and formals[0] is EllipsisType

    if is_ellipsis:
        formals[0] = cast(Any, type)

    formal_error: ErrorSet = split_errors(formals)
    if isinstance(formal_error, SignalingErrorSet):
        return formal_error

    return (split_valids(formals), is_ellipsis)


def _validate_typing_callable_without_values(expected_type: CallableTypeFormal, globalns: NS_T) -> ErrorSet:
    x: SignalingErrorSet | tuple[list[TT2], bool] = _validate_typing_callable_without_values_in(expected_type, globalns)
    if isinstance(x, SignalingErrorSet):
        return x
    return no_error


def _validate_typing_callable_with_values(expected_type: CallableTypeFormal, value: Any, globalns: NS_T) -> ErrorSet:
    inner: SignalingErrorSet | tuple[list[TT2], bool] = _validate_typing_callable_without_values_in(expected_type, globalns)

    if isinstance(inner, SignalingErrorSet):
        return inner

    if not isinstance(value, CallableTypeRealUserDefined) and not isinstance(value, CallableTypeRealBuiltIn):
        return make_error(f"must be an instance of {expected_type.__str__()}, but received {type(value)}")

    names: list[str] = list(value.__annotations__.keys())
    reals: list[SignalingErrorSet | TT2] = _type_resolve_all(value.__annotations__.values(), globalns)
    formals: list[TT2] = inner[0]
    is_ellipsis: bool = inner[1]

    if is_ellipsis:
        t: type[Any] = cast(Any, type)
        r: TT2 = formals[1]
        formals = _item_multiply(t, len(reals) - 1)
        formals.append(r)

    real_error: ErrorSet = split_errors(reals)
    if isinstance(real_error, SignalingErrorSet):
        return real_error

    reals2: list[TT2] = split_valids(reals)

    if not is_ellipsis and len(reals2) != len(formals):
        return make_error(f"bad parameters - should have {len(formals)} [{formals}] but there are {len(reals2)} [{reals2}]")

    return _validate_parameters(names, reals2, formals, is_ellipsis)


def _validate_typing_literal(expected_type: LiteralType, value: Any, globalns: NS_T) -> ErrorSet:
    if value in expected_type.__args__:
        return no_error
    return make_error(f"must be one of [{', '.join([x.__str__() for x in expected_type.__args__])}] but received {value}")


def _blindly_accept(expected_type: Any, globalns: NS_T) -> ErrorSet:
    return no_error


def _validate_union_types_without_values(expected_type: UnionType | OptionalType, globalns: NS_T) -> ErrorSet:
    is_valid: bool = any(_validate_types_without_values(t, globalns).empty for t in expected_type.__args__)
    if not is_valid:
        return make_error(f"The type {expected_type} is not valid")
    return no_error


def _validate_union_types_with_values(expected_type: UnionType | OptionalType, value: Any, globalns: NS_T) -> ErrorSet:
    is_valid: bool = any(_validate_types_with_values(t, value, globalns).empty for t in expected_type.__args__)
    if not is_valid:
        return make_error(f"must be an instance of {expected_type}, but received {value}")
    return no_error


_dict_values: type = type({}.values())
_dict_keys: type = type({}.keys())


_validate_typing_mappings: dict[type, tuple[Callable[[GenericType, Any, NS_T], ErrorSet], Callable[[GenericType, NS_T], ErrorSet]]] = {
    tuple                   : (_validate_typing_tuple_with_values   , _validate_typing_tuple_without_values   ),  # noqa: E202,E203
    dict                    : (_validate_typing_dict_with_values    , _validate_typing_dict_without_values    ),  # noqa: E202,E203
    list                    : (_validate_typing_iterable_with_values, _validate_typing_iterable_without_values),  # noqa: E202,E203
    frozenset               : (_validate_typing_iterable_with_values, _validate_typing_iterable_without_values),  # noqa: E202,E203
    set                     : (_validate_typing_iterable_with_values, _validate_typing_iterable_without_values),  # noqa: E202,E203
    _dict_keys              : (_validate_typing_iterable_with_values, _validate_typing_iterable_without_values),  # noqa: E202,E203
    _dict_values            : (_validate_typing_iterable_with_values, _validate_typing_iterable_without_values),  # noqa: E202,E203
    collections.abc.Sequence: (_validate_typing_iterable_with_values, _validate_typing_iterable_without_values),  # noqa: E202,E203
    collections.abc.Iterable: (_validate_typing_iterable_with_values, _validate_typing_iterable_without_values)   # noqa: E202,E203
}


_default_mapping: tuple[Callable[[GenericType, Any, NS_T], ErrorSet], Callable[[GenericType, NS_T], ErrorSet]] = (_validate_simple_type, _blindly_accept)


def _validate_generic_type_with_values(expected_type: GenericType, value: Any, globalns: NS_T) -> ErrorSet:
    c: Callable[[GenericType, Any, NS_T], ErrorSet] = _validate_typing_mappings.get(expected_type.__origin__, _default_mapping)[0]
    return c(expected_type, value, globalns)


def _validate_generic_type_without_values(expected_type: GenericType, globalns: NS_T) -> ErrorSet:
    c: Callable[[GenericType, NS_T], ErrorSet] = _validate_typing_mappings.get(expected_type.__origin__, _default_mapping)[1]
    return c(expected_type, globalns)


@dataclass(frozen = True)
# class CallWrapper[_T]: # PEP 695
class CallWrapper(Generic[_T]):  # Delete when PEP 695 is ready.
    with_values: Callable[[_T, Any, NS_T], ErrorSet]
    without_values: Callable[[_T, NS_T], ErrorSet]


_default_wrapper: CallWrapper[Any] = CallWrapper(_validate_simple_type, _blindly_accept)


class _TypeMapper:
    def __init__(self) -> None:
        self.__mappeds: dict[Any, CallWrapper[Any]] = {}

    # def put[T: TT2](self, key: type[T], with_values: Callable[[T, Any, NS_T], ErrorSet], without_values: Callable[[T, NS_T], ErrorSet]) -> None: # PEP 695
    def put(self, key: type[_T], with_values: Callable[[_T, Any, NS_T], ErrorSet], without_values: Callable[[_T, NS_T], ErrorSet]) -> None:
        self.__mappeds[key] = CallWrapper(with_values, without_values)

    def validate_types_without_values(self, key: TT2, globalns: NS_T) -> ErrorSet:
        w: CallWrapper[Any] = self.__mappeds.get(type(key), _default_wrapper)
        return w.without_values(key, globalns)

    def validate_types_with_values(self, key: TT2, value: Any, globalns: NS_T) -> ErrorSet:
        w: CallWrapper[Any] = self.__mappeds.get(type(key), _default_wrapper)
        return w.with_values(key, value, globalns)


_TM = _TypeMapper()
_TM.put(TypedDictType     , _validate_typing_typed_dict_with_values, _validate_typing_typed_dict_without_values)  # noqa: E202,E203
_TM.put(UnionType         , _validate_union_types_with_values      , _validate_union_types_without_values      )  # noqa: E202,E203
_TM.put(OptionalType      , _validate_union_types_with_values      , _validate_union_types_without_values      )  # noqa: E202,E203
_TM.put(LiteralType       , _validate_typing_literal               , _blindly_accept                           )  # noqa: E202,E203
_TM.put(CallableTypeFormal, _validate_typing_callable_with_values  , _validate_typing_callable_without_values  )  # noqa: E202,E203
_TM.put(GenericType       , _validate_generic_type_with_values     , _validate_generic_type_without_values     )  # noqa: E202,E203


def _is_type_ok(reworked_type: Any) -> bool:
    return any(isinstance(reworked_type, x) for x in TT3)


def _type_resolve(expected_type: TT1 | TT2, globalns: NS_T) -> SignalingErrorSet | TT2:
    reworked_type: Any = expected_type

    if type(reworked_type) is str or isinstance(reworked_type, ForwardRef):
        reworked_type = _evaluate_forward_reference(reworked_type, globalns)

    if type(reworked_type) is GenericAlias:
        reworked_type = _reduce_alias(reworked_type, globalns)

    if reworked_type is None:
        return type(None)

    if reworked_type is ...:
        return EllipsisType

    if isinstance(reworked_type, SignalingErrorSet):
        return reworked_type

    assert not isinstance(reworked_type, ErrorSet)

    if not _is_type_ok(reworked_type):
        print(type(reworked_type))
        return make_error(f"{reworked_type} is not a valid type")

    return cast(TT2, reworked_type)


def _type_resolve_all(types: Iterable[TT1 | TT2], globalns: NS_T) -> list[SignalingErrorSet | TT2]:
    return [_type_resolve(x, globalns) for x in types]


def _temp_name(ns: NS_T) -> str:
    i: int = 1
    while f"temp_{i}" in ns:
        i += 1
    return f"temp_{i}"


def _mangle_module(alias: GenericAlias, globalns: NS_T) -> tuple[str, NS_T]:
    origin: type = alias.__origin__
    module: str = origin.__module__
    short_name: str = origin.__name__
    new_globalns: NS_T = globalns

    full_name: str
    if module == "builtins":
        full_name = short_name
    elif module in new_globalns:
        full_name = module + "." + short_name
    else:
        var_name: str = _temp_name(globalns)
        new_globalns = globalns.copy()
        new_globalns[var_name] = eval(module)
        full_name = var_name + "." + short_name

    return (full_name, new_globalns)


def _reduce_alias(alias: GenericAlias, globalns: NS_T) -> SignalingErrorSet | type[Any]:
    t: tuple[str, NS_T] = _mangle_module(alias, globalns)
    full_name: str = t[0]
    new_globalns: NS_T = t[1]

    found: list[SignalingErrorSet | TT2] = _type_resolve_all(alias.__args__, new_globalns)
    errors: ErrorSet = split_errors(found)
    if isinstance(errors, SignalingErrorSet):
        return errors

    ok_found: list[Any] = split_valids(found)

    names: str = ",".join(x.__name__ for x in ok_found)
    new_name: str = full_name + "[" + names + "]"
    return _evaluate_forward_reference(ForwardRef(new_name), new_globalns)


def _validate_types_without_values(expected_type: TT1 | TT2, globalns: NS_T) -> ErrorSet:
    result: SignalingErrorSet | TT2 = _validate_types_without_values_in(expected_type, globalns)
    if isinstance(result, SignalingErrorSet):
        return result
    return no_error


def _validate_types_without_values_in(expected_type: TT1 | TT2, globalns: NS_T) -> SignalingErrorSet | TT2:
    reworked_type: SignalingErrorSet | TT2 = _type_resolve(expected_type, globalns)
    if reworked_type is EllipsisType:
        return bad_ellipsis
    if isinstance(reworked_type, SignalingErrorSet):
        return reworked_type
    inner: ErrorSet = _TM.validate_types_without_values(reworked_type, globalns)
    if isinstance(inner, SignalingErrorSet):
        return inner
    return reworked_type


def _validate_types_with_values(expected_type: TT1 | TT2, value: Any, globalns: NS_T) -> ErrorSet:
    result: SignalingErrorSet | TT2 = _validate_types_without_values_in(expected_type, globalns)
    if isinstance(result, SignalingErrorSet):
        return result
    return _TM.validate_types_with_values(result, value, globalns)


def _evaluate_forward_reference(ref_type: ForwardRef | str, globalns: NS_T) -> SignalingErrorSet | type[Any]:
    try:
        if isinstance(ref_type, str):
            ref_type = ForwardRef(ref_type)
        return cast(type[Any], ref_type._evaluate(globalns, None, frozenset()))
    except BaseException as x:  # noqa: F841
        return make_error(f'Could not evaluate "{ref_type}" as a valid type')


# def dataclass_type_validator_without_values[D: DataclassInstance](target: type[D], localns: NS_T) -> None: # PEP 695
def dataclass_type_validator_without_values(target: type[_D], localns: NS_T) -> None:
    fields: tuple[dataclasses.Field[Any], ...] = dataclasses.fields(target)
    globalns: NS_T = sys.modules[target.__module__].__dict__.copy()
    globalns.update(localns)

    errors: dict[str, ErrorSet] = {}
    for field in fields:
        field_name: str = field.name
        expected_type: Any = field.type
        errors[field_name] = _validate_types_without_values(expected_type, globalns)

    es: ErrorSet = make_errors(errors)
    if isinstance(es, SignalingErrorSet):
        raise TypeValidationError("Dataclass Type Validation Error", target = target, errors = es)


# def dataclass_type_validator_with_values[D: DataclassInstance](target: D, localns: NS_T) -> None: # PEP 695
def dataclass_type_validator_with_values(target: _D, localns: NS_T) -> None:
    fields: tuple[dataclasses.Field[Any], ...] = dataclasses.fields(target)
    globalns: NS_T = sys.modules[target.__module__].__dict__.copy()
    globalns.update(localns)

    errors: dict[str, ErrorSet] = {}
    for field in fields:
        field_name: str = field.name
        expected_type: Any = field.type
        value = getattr(target, field_name)
        errors[field_name] = _validate_types_with_values(expected_type, value, globalns)

    es: ErrorSet = make_errors(errors)
    if isinstance(es, SignalingErrorSet):
        raise TypeValidationError("Dataclass Type Validation Error", target = target, errors = es)


# def dataclass_validate[D: DataclassInstance](localns: NS_T | None = None, cls: type[U] | None = None) -> type[D] | Callable[[type[D]], type[D]]: # PEP 695
def dataclass_validate_local(localns: NS_T) -> Callable[[type[_D]], type[_D]]:
    """Dataclass decorator to automatically add validation to a dataclass.
    So you don't have to add a __post_init__ method, or if you have one, you don't have
    to remember to add the dataclass_type_validator(self) call to it; just decorate your
    dataclass with this instead.
    """
    def x(cls: type[_D]) -> type[_D]:
        return _dataclass_full_validate(cls, localns)
    return x


# def dataclass_validate[D: DataclassInstance](cls: type[D]) -> type[D]: # PEP 695
def dataclass_validate(cls: type[_D]) -> type[_D]:
    """Dataclass decorator to automatically add validation to a dataclass.
    So you don't have to add a __post_init__ method, or if you have one, you don't have
    to remember to add the dataclass_type_validator(self) call to it; just decorate your
    dataclass with this instead.
    """
    return _dataclass_full_validate(cls, {})


# def _dataclass_full_validate[D: DataclassInstance](cls: type[D]) -> type[D]: # PEP 695
def _dataclass_full_validate(cls: type[_D], localns: NS_T) -> type[_D]:
    localns[cls.__name__] = cls

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
        dataclass_type_validator_with_values(self, localns)
        if call_post_type_validate:
            self.__post_type_validate__()
        return x

    setattr(cls, wrapped_method_name, method_wrapper)

    dataclass_type_validator_without_values(cls, localns)

    return cls
