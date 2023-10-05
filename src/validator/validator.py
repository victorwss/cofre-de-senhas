# Code modified fom the code given at https://github.com/levii/dataclass-type-validator
import functools
import sys
import collections
import dataclasses
from abc import ABC, abstractmethod
from .typezoo import *
from .errorset import *
from typing import Any, Callable, cast, ForwardRef, Generic, get_type_hints, Iterable, override, TypeVar


GlobalNS_T = dict[str, Any]
_U = TypeVar("_U")


class TypeValidationError(TypeError):
    """Exception raised on type validation errors.
    """

    def __init__(self, *args: Any, target: _U, errors: ErrorSet) -> None:
        super(TypeValidationError, self).__init__(*args)
        self.class_: type[Any] = target.__class__
        self.errors: ErrorSet = errors

    @override
    def __repr__(self) -> str:
        cls: type[Any] = self.class_
        cls_name: str = f"{cls.__module__}.{cls.__name__}" if cls.__module__ != "__main__" else cls.__name__
        attrs: str = ", ".join([repr(v) for v in self.args])
        return f"{cls_name}({attrs}, errors={repr(self.errors)})"

    @override
    def __str__(self) -> str:
        cls: type[Any] = self.class_
        cls_name: str = f"{cls.__module__}.{cls.__name__}" if cls.__module__ != "__main__" else cls.__name__
        s: str = cls_name
        return f"{s} (errors = {self.errors})"


def _validate_simple_type(expected_type: type[Any], value: Any, globalns: GlobalNS_T) -> ErrorSet:
    if expected_type is Any or isinstance(value, expected_type):
        return no_error
    return make_errors(f"must be an instance of type {expected_type}, but received {type(value)}")


def _validate_typing_iterable(expected_type: GenericType, value: Any, globalns: GlobalNS_T) -> ErrorSet:
    if len(expected_type.__args__) != 1:
        return make_errors(f"bad parameters for {expected_type}")

    if not isinstance(value, expected_type.__origin__):
        return make_errors(f"must be an instance of iterable type {expected_type.__origin__.__name__}, but received {type(value)}")

    assert isinstance(value, Iterable)

    expected_item_type = expected_type.__args__[0]
    return make_errors([_validate_types(expected_item_type, v, globalns) for v in value])


def _item_multiply(element: _U, times: int) -> list[_U]:
    return [element for x in range(0, times)]


def _to_error(what: type[Any] | ErrorSet) -> ErrorSet:
    if what is EllipsisType:
        return bad_ellipsis
    if isinstance(what, ErrorSet):
        return what
    return no_error


def _split_errors(entering: list[type[Any] | ErrorSet]) -> ErrorSet:
    return make_errors([_to_error(t) for t in entering])


def _split_valids(entering: list[type[Any] | ErrorSet]) -> list[type[Any]]:
    return [t for t in entering if not isinstance(t, ErrorSet) and not isinstance(t, EllipsisType)]


def _validate_typing_tuple(expected_type: GenericType, value: Any, globalns: GlobalNS_T) -> ErrorSet:
    if not isinstance(value, tuple):
        return make_errors(f"must be an instance of tuple, but received {type(value)}")

    tvalue: tuple[Any, ...] = value

    types: list[type[Any] | ErrorSet] = _type_resolve_all(expected_type.__args__, globalns)

    if len(types) == 2 and types[1] is EllipsisType:
        types = _item_multiply(types[0], len(tvalue))

    error_types: ErrorSet = _split_errors(types)
    if not error_types.empty:
        return error_types

    types2: list[type[Any]] = _split_valids(types)
    assert len(types2) == len(types)

    if len(tvalue) != len(types2):
        return make_errors(f"must be an instance of {expected_type} with {len(types2)} element{'s' if len(types2) > 1 else ''}, but there {'are' if len(types2) > 1 else 'is'} {len(types2)} element{'s' if len(types2) > 1 else ''}")

    errors: list[ErrorSet] = [_validate_types(types2[k], tvalue[k], globalns) for k in range(0, len(types2))]
    return make_errors(errors)


def _validate_typing_typed_dict(expected_type: TypedDictType, value: Any, globalns: GlobalNS_T) -> ErrorSet:
    if not isinstance(value, dict):
        return make_errors(f"must be an instance of TypedDict, but received {type(value)}")

    fields: dict[str, type] = get_type_hints(expected_type)
    errors: dict[str, ErrorSet] = {}

    common_fields    : set[str] = set(fields.keys()).intersection(set(value .keys()))
    missing_fields   : set[str] = set(fields.keys()).difference  (set(value .keys()))
    unexpected_fields: set[str] = set(value .keys()).difference  (set(fields.keys()))

    for f in missing_fields:
        errors[f] = make_errors(f"field is missing in {expected_type}")

    for f in unexpected_fields:
        errors[f] = make_errors(f"field is unexpected in {expected_type}")

    for f in common_fields:
        errors[f] = _validate_types(fields[f], value[f], globalns)

    return make_errors(errors)


def _validate_typing_dict(expected_type: GenericType, value: Any, globalns: GlobalNS_T) -> ErrorSet:
    if len(expected_type.__args__) != 2:
        return make_errors(f"bad parameters for {expected_type}")

    if not isinstance(value, dict):
        return make_errors(f"must be an instance of dict, but received {type(value)}")

    expected_key_type  : type[Any] | ErrorSet = _type_resolve(expected_type.__args__[0], globalns)
    expected_value_type: type[Any] | ErrorSet = _type_resolve(expected_type.__args__[1], globalns)

    bad: dict[str, ErrorSet] = {
        "key": _to_error(expected_key_type),
        "value": _to_error(expected_value_type)
    }
    bad2: ErrorSet = make_errors(bad)
    if not bad2.empty:
        return bad2

    assert not isinstance(expected_key_type, ErrorSet)
    assert not isinstance(expected_value_type, ErrorSet)
    assert expected_key_type != EllipsisType
    assert expected_value_type != EllipsisType

    keys: list[Any] = list(value.keys())

    errors: dict[str, ErrorSet] = {}

    for idx in range(0, len(keys)):
        key: Any = keys[idx]
        errors[f"key {key} ({idx})"] = _validate_types(expected_key_type, key, globalns)

    for k in value.keys():
        vkey: Any = keys[idx]
        value2: Any = value[keys[idx]]
        errors[f"value {value2} for {vkey} ({idx})"] = _validate_types(expected_value_type, value2, globalns)

    return make_errors(errors)


def _validate_parameter(real: type[Any], formal: type[Any], check_any: bool) -> ErrorSet:
    if (not check_any or formal != Any) and formal != real:
        return make_errors(f"expected {formal} but was {real}")
    return no_error


def _validate_parameters(names: list[str], reals: list[type[Any]], formals: list[type[Any]], is_ellipsis: bool) -> ErrorSet:
    errors: dict[str, ErrorSet] = {}

    if not is_ellipsis:
        for k in range(0, len(reals) - 1):
            errors[names[k]] = _validate_parameter(reals[k], formals[k], False)
    errors[names[-1]] = _validate_parameter(reals[-1], formals[-1], True)

    return make_errors(errors)


def _validate_typing_callable(expected_type: CallableTypeFormal, value: Any, globalns: GlobalNS_T) -> ErrorSet:
    if not isinstance(value, CallableTypeReal1) and not isinstance(value, CallableTypeReal2):
        return make_errors(f"must be an instance of {expected_type.__str__()}, but received {type(value)}")

    names  : list[str]                   = list(value.__annotations__.keys())
    reals  : list[type[Any] | ErrorSet] = _type_resolve_all(value.__annotations__.values(), globalns)
    formals: list[type[Any] | ErrorSet] = _type_resolve_all(expected_type.__args__, globalns)
    is_ellipsis: bool = len(formals) == 2 and formals[0] is EllipsisType

    if is_ellipsis:
        t: type[Any] | ErrorSet = cast(Any, type)
        r: type[Any] | ErrorSet = formals[1]
        formals = _item_multiply(t, len(formals) - 1)
        formals.append(r)

    real_error  : ErrorSet = _split_errors(reals  )
    formal_error: ErrorSet = _split_errors(formals)
    bad: dict[str, ErrorSet] = {
        "real": real_error,
        "formal": formal_error
    }
    bad2: ErrorSet = make_errors(bad)
    if not bad2.empty:
        return bad2

    reals2  : list[type[Any]] = _split_valids(reals  )
    formals2: list[type[Any]] = _split_valids(formals)

    if not is_ellipsis and len(reals2) != len(formals2):
        return make_errors(f"bad parameters - should have {len(formals2)} but there are {len(reals2)}")

    return _validate_parameters(names, reals2, formals2, is_ellipsis)


def _validate_typing_literal(expected_type: LiteralType, value: Any, globalns: GlobalNS_T) -> ErrorSet:
    if value in expected_type.__args__:
        return no_error
    return make_errors(f"must be one of [{', '.join([x.__str__() for x in expected_type.__args__])}] but received {value}")


def _validate_union_types(expected_type: UnionType | OptionalType, value: Any, globalns: GlobalNS_T) -> ErrorSet:
    is_valid: bool = any(_validate_types(t, value, globalns).empty for t in expected_type.__args__)
    if not is_valid:
        return make_errors(f"must be an instance of {expected_type}, but received {value}")
    return no_error


_dict_values: type = type({}.values())
_dict_keys  : type = type({}.keys())


_validate_typing_mappings: dict[type, Callable[[GenericType, Any, GlobalNS_T], ErrorSet]] = {
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


def _validate_generic_type(expected_type: GenericType, value: Any, globalns: GlobalNS_T) -> ErrorSet:
    return _validate_typing_mappings.get(expected_type.__origin__, _validate_simple_type)(expected_type, value, globalns)


class _TypeMapper:
    def __init__(self) -> None:
        self.__mappeds: dict[Any, Callable[..., ErrorSet]] = {}

    def put(self, key: type[_U], value: Callable[[_U, Any, GlobalNS_T], ErrorSet]) -> None:
        self.__mappeds[key] = value

    def call(self, key: type[_U], value: Any, globalns: GlobalNS_T) -> ErrorSet:
        return self.__mappeds.get(type(key), _validate_simple_type)(key, value, globalns)


_TM = _TypeMapper()
_TM.put(TypedDictType     , _validate_typing_typed_dict)
_TM.put(UnionType         , _validate_union_types      )
_TM.put(OptionalType      , _validate_union_types      )
_TM.put(LiteralType       , _validate_typing_literal   )
_TM.put(CallableTypeFormal, _validate_typing_callable  )
_TM.put(GenericType       , _validate_generic_type     )


def _type_resolve(expected_type: TT1 | TT2, globalns: GlobalNS_T) -> TT2 | ErrorSet:
    reworked_type: Any = expected_type

    if type(expected_type) is str:
        try:
            reworked_type = eval(reworked_type, globalns)
        except Exception as x:
            return make_errors(f'Could not evaluate "{expected_type}" as a valid type')

    if type(reworked_type) is GenericAlias:
        result: type[Any] | ErrorSet = _reduce_alias(reworked_type, globalns)
        if isinstance(result, ErrorSet):
            return result
        reworked_type = result

    if isinstance(reworked_type, ForwardRef):
        reworked_type = _evaluate_forward_reference(reworked_type, globalns)

    if reworked_type is None:
        return type(None)

    if reworked_type is ...:
        return EllipsisType

    if not any(isinstance(reworked_type, x) for x in TT3):
        return make_errors(f"{reworked_type} is not a valid type")

    return cast(TT2, reworked_type)


def _type_resolve_all(types: Iterable[TT1 | TT2], globalns: GlobalNS_T) -> list[TT2 | ErrorSet]:
    return [_type_resolve(x, globalns) for x in types]


def _reduce_alias(alias: GenericAlias, globalns: GlobalNS_T) -> type[Any] | ErrorSet:
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

    found: list[type[Any] | ErrorSet] = _type_resolve_all(alias.__args__, new_globalns)
    errors: ErrorSet = _split_errors(found)
    if not errors.empty:
        return errors

    ok_found: list[Any] = _split_valids(found)

    names: str = ",".join(x.__name__ for x in ok_found)
    new_name: str = full_name + "[" + names + "]"
    try:
        return _evaluate_forward_reference(ForwardRef(new_name), new_globalns)
    except Exception as x:
        return make_errors(f'Could not evaluate "{new_name}" as a valid type')


def _validate_types(expected_type: TT1 | TT2, value: Any, globalns: GlobalNS_T) -> ErrorSet:
    reworked_type: TT2 | ErrorSet = _type_resolve(expected_type, globalns)
    if reworked_type is EllipsisType:
        return bad_ellipsis
    if isinstance(reworked_type, ErrorSet):
        return reworked_type
    return _TM.call(reworked_type, value, globalns)


def _evaluate_forward_reference(ref_type: ForwardRef, globalns: GlobalNS_T) -> type[Any]:
    """ Support evaluating ForwardRef types on both Python 3.8 and 3.9. """
    return cast(type[Any], ref_type._evaluate(globalns, None, frozenset()))


def dataclass_type_validator(target: Any) -> None:
    fields: tuple[dataclasses.Field[Any], ...] = dataclasses.fields(target)
    globalns: GlobalNS_T = sys.modules[target.__module__].__dict__.copy()

    errors: dict[str, ErrorSet] = {}
    for field in fields:
        field_name: str = field.name
        expected_type: Any = field.type
        value = getattr(target, field_name)
        errors[field_name] = _validate_types(expected_type, value, globalns)

    es: ErrorSet = make_errors(errors)
    if not es.empty:
        raise TypeValidationError("Dataclass Type Validation Error", target = target, errors = es)


def dataclass_validate(cls: type[_U] | None = None) -> type[_U] | Callable[[type[_U]], type[_U]]:
    """Dataclass decorator to automatically add validation to a dataclass.
    So you don't have to add a __post_init__ method, or if you have one, you don't have
    to remember to add the dataclass_type_validator(self) call to it; just decorate your
    dataclass with this instead.
    """
    if cls is None: return _dataclass_full_validate
    return _dataclass_full_validate(cls)


def _dataclass_full_validate(cls: type[_U]) -> type[_U]:

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