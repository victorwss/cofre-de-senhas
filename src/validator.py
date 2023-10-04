# Code modified fom the code given at https://github.com/levii/dataclass-type-validator
import dataclasses
import typing
import functools
import sys
import collections
from abc import ABC, abstractmethod
from typing import \
    Any, Callable, cast, Dict, ForwardRef, FrozenSet, Generic, get_type_hints, Iterable, List, Literal, \
    Optional, override, Protocol, runtime_checkable, Self, Set, Tuple, Type, TypedDict, TypeVar

GlobalNS_T = dict[str, Any]
_U = TypeVar("_U")
_SI = TypeVar("_SI", bound = int | str)

_CallableTypeReal1 = type(lambda a: a)
_CallableTypeReal2 = type(print)

if typing.TYPE_CHECKING:

    class _UnionType(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

    class _OptionalType(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

    class _LiteralType(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

    class _GenericType(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

        @property
        def __origin__(self) -> type:
            pass

    class _GenericAlias(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

        @property
        def __origin__(self) -> type:
            pass

    class _Ellipsis(type):
        pass

    class _EllipsisType(type):
        pass

    class _CallableTypeFormal(type):
        @property
        def __args__(self) -> list[type[Any] | ForwardRef]:
            pass

    class _TypedDictType(type):
        pass

else:
    _UnionType          = type(str | int)
    _OptionalType       = type(Optional[int])
    _LiteralType        = type(Literal[True])
    _GenericType        = type(list[str])
    _GenericAlias       = type(List[str])
    _Ellipsis           = ...
    _EllipsisType       = type(...)
    _CallableTypeFormal = type(Callable[[], Any])
    _TypedDictType      = type(TypedDict('X', {'x': int}))


@dataclasses.dataclass
class _FieldChain:
    fields: list[str | int]

    @override
    def __str__(self) -> str:
        x: str = ""
        for k in self.fields:
            x += f"[{k}]"
        return x

    def append(self, other: str | int) -> "_FieldChain":
        return _FieldChain(self.fields + [other])

class _ErrorSet(ABC):

    @property
    def as_list(self) -> list[str]:
        return self.list_all(_FieldChain([]))

    @override
    def __str__(self) -> str:
        return ",".join(self.as_list)

    @abstractmethod
    def list_all(self, fields: _FieldChain) -> list[str]:
        pass

@dataclasses.dataclass
class _ErrorSetLeaf(_ErrorSet):
    error: str

    @override
    def list_all(self, fields: _FieldChain) -> list[str]:
        return [f"{fields}: {self.error}"]

@dataclasses.dataclass
class _ErrorSetDict(_ErrorSet, Generic[_SI]):
    errors: dict[_SI, _ErrorSet]

    @override
    def list_all(self, fields: _FieldChain) -> list[str]:
        return _flatten([self.errors[k].list_all(fields.append(k)) for k in self.errors])

@dataclasses.dataclass
class _ErrorSetEmpty(_ErrorSet):
    pass

    @override
    def list_all(self, fields: _FieldChain) -> list[str]:
        return []


class TypeValidationError(TypeError):
    """Exception raised on type validation errors.
    """

    def __init__(self: Self, *args: Any, target: _U, errors: _ErrorSet) -> None:
        super(TypeValidationError, self).__init__(*args)
        self.class_: type[Any] = target.__class__
        self.errors: _ErrorSet = errors

    @override
    def __repr__(self: Self) -> str:
        cls: type[Any] = self.class_
        cls_name: str = f"{cls.__module__}.{cls.__name__}" if cls.__module__ != "__main__" else cls.__name__
        attrs: str = ", ".join([repr(v) for v in self.args])
        return f"{cls_name}({attrs}, errors={repr(self.errors)})"

    @override
    def __str__(self: Self) -> str:
        cls: type[Any] = self.class_
        cls_name: str = f"{cls.__module__}.{cls.__name__}" if cls.__module__ != "__main__" else cls.__name__
        s: str = cls_name
        return f"{s} (errors = {self.errors})"


def _flatten(data: list[list[_U]]) -> list[_U]:
    d: list[_U] = []
    for p in data:
        d += p
    return d


def _type_misuse(expected_type: _EllipsisType, value: Any, globalns: GlobalNS_T) -> _ErrorSet:
    return _make_errors(f"Misplaced or misused type {expected_type}")


def _as_dict(what: list[_U]) -> dict[int, _U]:
    return {i: what[i] for i in range(0, len(what))}


def _thou_shalt_not_pass(pair: tuple[_U, _ErrorSet]) -> bool:
    return not isinstance(pair[1], _ErrorSetEmpty)


def _make_dict_errors(what: dict[_SI, _ErrorSet]) -> _ErrorSetDict[_SI] | _ErrorSetEmpty:
    d2: dict[_SI, _ErrorSet] = dict(filter(_thou_shalt_not_pass, what.items()))

    if len(d2) == 0:
        return _ErrorSetEmpty()

    return _ErrorSetDict(d2)


def _make_errors(what: list[_ErrorSet] | dict[str, _ErrorSet] | str | None = None) -> _ErrorSet:

    if what is None:
        return _ErrorSetEmpty()

    if isinstance(what, str):
        return _ErrorSetLeaf(what)

    if isinstance(what, dict):
        return _make_dict_errors(what)

    return _make_dict_errors(_as_dict(what))


_no_error: _ErrorSet = _make_errors()
_bad_ellipsis: _ErrorSet = _make_errors("Unexpected ... here")


def _validate_simple_type(expected_type: type[Any], value: Any, globalns: GlobalNS_T) -> _ErrorSet:
    if expected_type is Any or isinstance(value, expected_type):
        return _no_error
    return _make_errors(f"must be an instance of type {expected_type}, but received {type(value)}")


def _validate_typing_iterable(expected_type: _GenericType, value: Any, globalns: GlobalNS_T) -> _ErrorSet:
    if len(expected_type.__args__) != 1:
        return _make_errors(f"bad parameters for {expected_type}")

    if not isinstance(value, expected_type.__origin__):
        return _make_errors(f"must be an instance of iterable type {expected_type.__origin__.__name__}, but received {type(value)}")

    assert isinstance(value, Iterable)

    expected_item_type = expected_type.__args__[0]
    return _make_errors([_validate_types(expected_item_type, v, globalns) for v in value])


def _item_multiply(element: _U, times: int) -> list[_U]:
    return [element for x in range(0, times)]


def _to_error(what: type[Any] | _ErrorSet) -> _ErrorSet:
    if what is _EllipsisType:
        return _bad_ellipsis
    if isinstance(what, _ErrorSet):
        return what
    return _no_error


def _split_errors(entering: list[type[Any] | _ErrorSet]) -> _ErrorSet:
    return _make_errors([_to_error(t) for t in entering])


def _split_valids(entering: list[type[Any] | _ErrorSet]) -> list[type[Any]]:
    return [t for t in entering if not isinstance(t, _ErrorSet) and not isinstance(t, _EllipsisType)]


def _validate_typing_tuple(expected_type: _GenericType, value: Any, globalns: GlobalNS_T) -> _ErrorSet:
    if not isinstance(value, tuple):
        return _make_errors(f"must be an instance of tuple, but received {type(value)}")

    tvalue: tuple[Any, ...] = value

    types: list[type[Any] | _ErrorSet] = _type_resolve_all(expected_type.__args__, globalns)

    if len(types) == 2 and types[1] is _EllipsisType:
        types = _item_multiply(types[0], len(tvalue))

    error_types: _ErrorSet = _split_errors(types)
    if not isinstance(error_types, _ErrorSetEmpty):
        return error_types

    types2: list[type[Any]] = _split_valids(types)
    assert len(types2) == len(types)

    if len(tvalue) != len(types2):
        return _make_errors(f"must be an instance of {expected_type} with {len(types2)} element{'s' if len(types2) > 1 else ''}, but there {'are' if len(types2) > 1 else 'is'} {len(types2)} element{'s' if len(types2) > 1 else ''}")

    errors: list[_ErrorSet] = [_validate_types(types2[k], tvalue[k], globalns) for k in range(0, len(types2))]
    return _make_errors(errors)


def _validate_typing_typed_dict(expected_type: _TypedDictType, value: Any, globalns: GlobalNS_T) -> _ErrorSet:
    if not isinstance(value, dict):
        return _ErrorSetLeaf(f"must be an instance of TypedDict, but received {type(value)}")

    fields: dict[str, type] = get_type_hints(expected_type)
    errors: dict[str, _ErrorSet] = {}

    common_fields    : set[str] = set(fields.keys()).intersection(set(value .keys()))
    missing_fields   : set[str] = set(fields.keys()).difference  (set(value .keys()))
    unexpected_fields: set[str] = set(value .keys()).difference  (set(fields.keys()))

    for f in missing_fields:
        errors[f] = _make_errors(f"field is missing in {expected_type}")

    for f in unexpected_fields:
        errors[f] = _make_errors(f"field is unexpected in {expected_type}")

    for f in common_fields:
        errors[f] = _validate_types(fields[f], value[f], globalns)

    return _make_errors(errors)


def _validate_typing_dict(expected_type: _GenericType, value: Any, globalns: GlobalNS_T) -> _ErrorSet:
    if len(expected_type.__args__) != 2:
        return _make_errors(f"bad parameters for {expected_type}")

    if not isinstance(value, dict):
        return _make_errors(f"must be an instance of dict, but received {type(value)}")

    expected_key_type  : type[Any] | _ErrorSet = _type_resolve(expected_type.__args__[0], globalns)
    expected_value_type: type[Any] | _ErrorSet = _type_resolve(expected_type.__args__[1], globalns)

    bad: dict[str, _ErrorSet] = {
        "key": _to_error(expected_key_type),
        "value": _to_error(expected_value_type)
    }
    bad2: _ErrorSet = _make_errors(bad)
    if not isinstance(bad2, _ErrorSetEmpty):
        return bad2

    assert not isinstance(expected_key_type, _ErrorSet)
    assert not isinstance(expected_value_type, _ErrorSet)
    assert expected_key_type != _EllipsisType
    assert expected_value_type != _EllipsisType

    keys: list[Any] = list(value.keys())

    errors: dict[str, _ErrorSet] = {}

    for idx in range(0, len(keys)):
        key: Any = keys[idx]
        errors[f"key {key} ({idx})"] = _validate_types(expected_key_type, key, globalns)

    for k in value.keys():
        vkey: Any = keys[idx]
        value2: Any = value[keys[idx]]
        errors[f"value {value2} for {vkey} ({idx})"] = _validate_types(expected_value_type, value2, globalns)

    return _make_errors(errors)


def _validate_parameter(real: type[Any], formal: type[Any], check_any: bool) -> _ErrorSet:
    if (not check_any or formal != Any) and formal != real:
        return _make_errors(f"expected {formal} but was {real}")
    return _no_error


def _validate_parameters(names: list[str], reals: list[type[Any]], formals: list[type[Any]], is_ellipsis: bool) -> _ErrorSet:
    errors: dict[str, _ErrorSet] = {}

    if not is_ellipsis:
        for k in range(0, len(reals) - 1):
            errors[names[k]] = _validate_parameter(reals[k], formals[k], False)
    errors[names[-1]] = _validate_parameter(reals[-1], formals[-1], True)

    return _make_errors(errors)


def _validate_typing_callable(expected_type: _CallableTypeFormal, value: Any, globalns: GlobalNS_T) -> _ErrorSet:
    if not isinstance(value, _CallableTypeReal1) and not isinstance(value, _CallableTypeReal2):
        return _make_errors(f"must be an instance of {expected_type.__str__()}, but received {type(value)}")

    names  : list[str]                   = list(value.__annotations__.keys())
    reals  : list[type[Any] | _ErrorSet] = _type_resolve_all(value.__annotations__.values(), globalns)
    formals: list[type[Any] | _ErrorSet] = _type_resolve_all(expected_type.__args__, globalns)
    is_ellipsis: bool = len(formals) == 2 and formals[0] is _EllipsisType

    if is_ellipsis:
        t: type[Any] | _ErrorSet = cast(Any, type)
        r: type[Any] | _ErrorSet = formals[1]
        formals = _item_multiply(t, len(formals) - 1)
        formals.append(r)

    real_error  : _ErrorSet = _split_errors(reals  )
    formal_error: _ErrorSet = _split_errors(formals)
    bad: dict[str, _ErrorSet] = {
        "real": real_error,
        "formal": formal_error
    }
    bad2: _ErrorSet = _make_errors(bad)
    if not isinstance(bad2, _ErrorSetEmpty):
        return bad2

    reals2  : list[type[Any]] = _split_valids(reals  )
    formals2: list[type[Any]] = _split_valids(formals)

    if not is_ellipsis and len(reals2) != len(formals2):
        return _make_errors(f"bad parameters - should have {len(formals2)} but there are {len(reals2)}")

    return _validate_parameters(names, reals2, formals2, is_ellipsis)


def _validate_typing_literal(expected_type: _LiteralType, value: Any, globalns: GlobalNS_T) -> _ErrorSet:
    if value in expected_type.__args__:
        return _no_error
    return _make_errors(f"must be one of [{', '.join([x.__str__() for x in expected_type.__args__])}] but received {value}")


def _validate_union_types(expected_type: _UnionType | _OptionalType, value: Any, globalns: GlobalNS_T) -> _ErrorSet:
    is_valid: bool = any(isinstance(_validate_types(t, value, globalns), _ErrorSetEmpty) for t in expected_type.__args__)
    if not is_valid:
        return _make_errors(f"must be an instance of {expected_type}, but received {value}")
    return _no_error


_dict_values: type = type({}.values())
_dict_keys  : type = type({}.keys())


_validate_typing_mappings: dict[type, Callable[[_GenericType, Any, GlobalNS_T], _ErrorSet]] = {
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


def _validate_generic_type(expected_type: _GenericType, value: Any, globalns: GlobalNS_T) -> _ErrorSet:
    return _validate_typing_mappings.get(expected_type.__origin__, _validate_simple_type)(expected_type, value, globalns)


#def _validate_simple_type(expected_type: Any, value: Any, globalns: GlobalNS_T) -> _ErrorSet:
#    if isinstance(expected_type, type):
#        return _validate_direct_type(expected_type, value, globalns)
#    assert False
#    return _make_errors(f"Incompatible type {type(expected_type).__name__} with value {value} (typed as {type(value).__name__})")


class TypeMapper:
    def __init__(self) -> None:
        self.__mappeds: dict[Any, Callable[..., _ErrorSet]] = {}

    def put(self, key: type[_U], value: Callable[[_U, Any, GlobalNS_T], _ErrorSet]) -> None:
        self.__mappeds[key] = value

    def call(self, key: type[_U], value: Any, globalns: GlobalNS_T) -> _ErrorSet:
        return self.__mappeds.get(type(key), _validate_simple_type)(key, value, globalns)


_TM = TypeMapper()
_TM.put(_TypedDictType     , _validate_typing_typed_dict)
_TM.put(_UnionType         , _validate_union_types      )
_TM.put(_OptionalType      , _validate_union_types      )
_TM.put(_LiteralType       , _validate_typing_literal   )
_TM.put(_CallableTypeFormal, _validate_typing_callable  )
_TM.put(_GenericType       , _validate_generic_type     )
_TM.put(_EllipsisType      , _type_misuse               )


_TT1 = _GenericAlias | ForwardRef | str | None
_TT2 = type[Any] | _UnionType | _OptionalType | _LiteralType | _GenericType | _CallableTypeFormal | _TypedDictType
_TT3 = [type, _UnionType, _OptionalType, _LiteralType, _GenericType, _CallableTypeFormal, _TypedDictType]


def _type_resolve(expected_type: _TT1 | _TT2, globalns: GlobalNS_T) -> _TT2 | _ErrorSet:
    reworked_type: Any = expected_type

    if type(expected_type) is str:
        try:
            reworked_type = eval(reworked_type, globalns)
        except Exception as x:
            return _make_errors(f'Could not evaluate "{expected_type}" as a valid type')

    if type(reworked_type) is _GenericAlias:
        result: type[Any] | _ErrorSet = _reduce_alias(reworked_type, globalns)
        if isinstance(result, _ErrorSet):
            return result
        reworked_type = result

    if isinstance(reworked_type, ForwardRef):
        reworked_type = _evaluate_forward_reference(reworked_type, globalns)

    if reworked_type is None:
        return type(None)

    if reworked_type is _Ellipsis:
        return _EllipsisType

    if not any(isinstance(reworked_type, x) for x in _TT3):
        return _make_errors(f"{reworked_type} is not a valid type")

    return cast(_TT2, reworked_type)


def _type_resolve_all(types: Iterable[_TT1 | _TT2], globalns: GlobalNS_T) -> list[_TT2 | _ErrorSet]:
    return [_type_resolve(x, globalns) for x in types]


def _reduce_alias(alias: _GenericAlias, globalns: GlobalNS_T) -> type[Any] | _ErrorSet:
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

    found: list[type[Any] | _ErrorSet] = _type_resolve_all(alias.__args__, new_globalns)
    errors: _ErrorSet = _split_errors(found)
    if not isinstance(errors, _ErrorSetEmpty):
        return errors

    ok_found: list[Any] = _split_valids(found)

    names: str = ",".join(x.__name__ for x in ok_found)
    new_name: str = full_name + "[" + names + "]"
    try:
        return _evaluate_forward_reference(ForwardRef(new_name), new_globalns)
    except Exception as x:
        return _make_errors(f'Could not evaluate "{new_name}" as a valid type')


def _validate_types(expected_type: _TT1 | _TT2, value: Any, globalns: GlobalNS_T) -> _ErrorSet:
    reworked_type: _TT2 | _ErrorSet = _type_resolve(expected_type, globalns)
    if reworked_type is _EllipsisType:
        return _bad_ellipsis
    if isinstance(reworked_type, _ErrorSet):
        return reworked_type
    return _TM.call(reworked_type, value, globalns)


def _evaluate_forward_reference(ref_type: ForwardRef, globalns: GlobalNS_T) -> type[Any]:
    """ Support evaluating ForwardRef types on both Python 3.8 and 3.9. """
    return cast(type[Any], ref_type._evaluate(globalns, None, frozenset()))


def dataclass_type_validator(target: Any) -> None:
    fields: tuple[dataclasses.Field[Any], ...] = dataclasses.fields(target)
    globalns: GlobalNS_T = sys.modules[target.__module__].__dict__.copy()

    errors: dict[str, _ErrorSet] = {}
    for field in fields:
        field_name: str = field.name
        expected_type: Any = field.type
        value = getattr(target, field_name)
        errors[field_name] = _validate_types(expected_type, value, globalns)

    es: _ErrorSet = _make_errors(errors)
    if not isinstance(es, _ErrorSetEmpty):
        raise TypeValidationError("Dataclass Type Validation Error", target = target, errors = es)


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