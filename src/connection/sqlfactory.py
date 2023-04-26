from abc import ABC, abstractmethod
from typing import Any, cast, Callable, Generic, TypeVar
from dataclasses import asdict, dataclass, is_dataclass, Field, fields
from dacite import from_dict
from validator import dataclass_validate, TypeValidationError
from connection.conn import TransactedConnection

T = TypeVar("T")
K = TypeVar("K")
NK = TypeVar("NK")
X = TypeVar("X")

def as_list(value: object) -> list[Any]:
    assert is_dataclass(value) and not isinstance(value, type)
    return [*asdict(value).values()]

def as_dict(value: object) -> dict[str, Any]:
    assert is_dataclass(value) and not isinstance(value, type)
    return asdict(value)

@dataclass(frozen = True)
class Empty:
    pass

class Joinable(ABC, Generic[T]):

    def inner(self, table_name: str, alias: str, joined_alias: str, join_fields: type[object], joined_fields: type[object]) -> "CriteriaJoin[T]":
        return CriteriaJoin(self, "INNER JOIN", table_name, alias, joined_alias, join_fields, joined_fields)

    def left_outer(self, table_name: str, alias: str, joined_alias: str, join_fields: type[object], joined_fields: type[object]) -> "CriteriaJoin[T]":
        return CriteriaJoin(self, "LEFT OUTER JOIN", table_name, alias, joined_alias, join_fields, joined_fields)

    def right_outer(self, table_name: str, alias: str, joined_alias: str, join_fields: type[object], joined_fields: type[object]) -> "CriteriaJoin[T]":
        return CriteriaJoin(self, "RIGHT OUTER JOIN", table_name, alias, joined_alias, join_fields, joined_fields)

    def full_outer(self, table_name: str, alias: str, joined_alias: str, join_fields: type[object], joined_fields: type[object]) -> "CriteriaJoin[T]":
        return CriteriaJoin(self, "FULL OUTER JOIN", table_name, alias, joined_alias, join_fields, joined_fields)

    def cross(self, table_name: str, alias: str) -> "CrossJoin[T]":
        return CrossJoin(self, table_name, alias)

    @abstractmethod
    def has(self, alias: str) -> bool:
        ...

    @abstractmethod
    @property
    def type_class(self) -> type[T]:
        ...

class Join(Generic[T], Joinable[T]):

    def where(self, where_types: type[X]) -> JoinedSelect[T, X]:
        if not is_dataclass(where_types): raise KeyError(f"The class {where_types} should be a dataclass.")
        where_fields: list[str] = []
        for f in fields(where_types):
            idx: int = f.name.find("__")
            if idx <= 0: raise KeyError(f"The field {f.name} should have a __ in the middle.")
            if idx == len(f.name) - 2: raise KeyError(f"The field {f.name} should have a __ in the middle.")
            alias: str = f.name[0 : idx]
            field_name: str = f.name[idx + 2 : ]
            if not self.has(alias): raise KeyError(f"The alias {alias} was not found.")
            where_fields.append(f"{alias}.{field_name} = ?")
        criteria: str = " AND ".join(where_fields)
        sql: str = f"{self}" if criteria == "" else f"{self} WHERE {criteria}"
        return JoinedSelect(sql, self.type_class, cast(type[X], where_types))

@dataclass_validate
@dataclass(frozen = True)
class JoinedSelect(Generic[T, X]):
    sql: str
    type_class: type[T]
    where_types: type[X]

    def select_one(self, cf: TransactedConnection, data: X) -> T | None:
        cf.execute(self.sql, as_list(data))
        return cf.fetchone_class(self.type_class)

    def select_one_or_else(self, cf: TransactedConnection, data: X, or_else: Callable[[], Exception]) -> T:
        cf.execute(self.sql, as_list(data))
        instance: T | None = cf.fetchone_class(self.type_class)
        if instance is None: raise or_else()
        return instance

    def select_all(self, cf: TransactedConnection, data: X) -> list[T]:
        cf.execute(self.sql, as_list(data))
        return cf.fetchall_class(self.type_class)

    def select_many(self, cf: TransactedConnection, data: X, size: int = 0) -> list[T]:
        cf.execute(self.sql, as_list(data))
        return cf.fetchmany_class(self.type_class, size)

@dataclass_validate
@dataclass(frozen = True)
class From(Generic[T], Joinable[T]):
    type_class: type[T]
    select: str
    table_name: str
    alias: str

    def __str__(self) -> str:
        return f"SELECT {self.select} FROM {self.table_name} {self.alias}"

    def has(self, alias: str) -> bool:
        return self.alias == alias

@dataclass_validate
@dataclass(frozen = True)
class FieldPair:
    a: Field[Any]
    b: Field[Any]

    @staticmethod
    def zip(a: type[object], b: type[object]) -> list[FieldPair]:
        if not is_dataclass(a): raise KeyError(f"The class {a} should be a dataclass.")
        if not is_dataclass(b): raise KeyError(f"The class {b} should be a dataclass.")
        fa: tuple[Field[Any], ...] = fields(a)
        fb: tuple[Field[Any], ...] = fields(b)
        if len(fa) == 0: raise KeyError("No join fields.")
        if len(fb) == 0: raise KeyError("No joined fields.")
        if len(fa) != len(fb): raise KeyError("The join and joined fields don't match.")
        result: list[FieldPair] = []
        for i in range(0, len(fa)):
            result.append(FieldPair(fa[i], fb[i]))
        return result

@dataclass_validate
@dataclass(frozen = True)
class CriteriaJoin(Generic[T], Join[T]):
    base: Joinable[T]
    join_type: str
    table_name: str
    alias: str
    joined_alias: str
    join_fields: type[object]
    joined_fields: type[object]

    def __post_type_validate__(self) -> None:
        if self.alias == self.joined_alias: raise KeyError("The aliases can't be the same.")
        if self.base.has(self.alias): raise KeyError(f"The alias {self.alias} is already present in the base.")
        if not self.base.has(self.joined_alias): raise KeyError(f"The alias {self.joined_alias} is not present in the base.")
        FieldPair.zip(self.join_fields, self.joined_fields)

    def __str__(self) -> str:
        fields: str = " AND ".join([f"{self.alias}.{f.a.name} = {self.joined_alias}.{f.b.name}" for f in FieldPair.zip(self.join_fields, self.joined_fields)])
        return f"{self.base} {self.join_type} {self.table_name} {self.alias} ON {fields}"

    def has(self, alias: str) -> bool:
        return self.alias == alias or self.base.has(alias)

    @property
    def type_class(self) -> type[T]:
        return self.base.type_class

@dataclass_validate
@dataclass(frozen = True)
class CrossJoin(Generic[T], Join[T]):
    base: Joinable[T]
    table_name: str
    alias: str

    def __post_type_validate__(self) -> None:
        if self.base.has(self.alias): raise KeyError(f"The alias {self.alias} is already present in the base.")

    def __str__(self) -> str:
        return f"{self.base} CROSS JOIN {self.table_name} {self.alias}"

    def has(self, alias: str) -> bool:
        return self.alias == alias or self.base.has(alias)

    @property
    def type_class(self) -> type[T]:
        return self.base.type_class

class SQLFactory(Generic[T, K, NK]):

    def __init__(self, table_name: str, type_class: type[T], key_type: type[K], keyless_type: type[NK], key_is_autoincrement: bool) -> None:
        if not is_dataclass(type_class):
            raise KeyError(f"The type_class {type_class.__name__} is not a dataclass.")
        if not is_dataclass(key_type):
            raise KeyError(f"The key_type {key_type.__name__} is not a dataclass.")
        if not is_dataclass(keyless_type):
            raise KeyError(f"The keyless_type {keyless_type.__name__} is not a dataclass.")

        self.__type_class  : type[T]      = cast(type[T] , type_class)
        self.__key_type    : type[K]      = cast(type[K] , key_type)
        self.__keyless_type: type[NK]     = cast(type[NK], keyless_type)
        self.__table_name  : str          = table_name
        self.__key_is_autoincrement: bool = key_is_autoincrement
        self.__type_fields  : list[str] = [field.name for field in fields(type_class  )]
        self.__key_fields   : list[str] = [field.name for field in fields(key_type    )]
        self.__nonkey_fields: list[str] = [field.name for field in fields(keyless_type)]

        if len(self.__type_fields) == 0:
            raise KeyError(f"The type_class {type_class.__name__} has no fields.")
        if len(self.__type_fields) == 0:
            raise KeyError(f"The key_type {key_type.__name__} has no fields.")
        if self.keyless_type == Empty:
            if type_class != key_type:
                raise KeyError(f"All the table fields are key-typed, but the type_class {type_class.__name__} is not the same as the key_type {key_type.__name__}.")
        elif len(self.__nonkey_fields) == 0:
            raise KeyError(f"The keyless_type {keyless_type.__name__} has no fields and isn't the Empty class.")

        self.__check_subfields(key_type, "key_type")
        self.__check_subfields(keyless_type, "__keyless_type")
        for f in self.__key_fields:
            if f in self.__nonkey_fields:
                raise KeyError(f"The field {f} is both from key_type {key_type.__name__} and keyless_type {keyless_type.__name__}.")
        for f in self.__type_fields:
            if f not in self.__nonkey_fields and f not in self.__key_fields:
                raise KeyError(f"The field {f} from type_class is neither from key_type {key_type.__name__} nor from keyless_type {keyless_type.__name__}.")
        if key_is_autoincrement and len(self.__key_fields) != 1:
            raise KeyError(f"The table key is auto_increment but there is more than one field in key_type {key_type.__name__}.")

    @property
    def key_is_autoincrement(self) -> bool:
        return self.__key_is_autoincrement

    @property
    def table_name(self) -> str:
        return self.__table_name

    @property
    def type_class(self) -> type[T]:
        return self.__type_class

    @property
    def key_type(self) -> type[K]:
        return self.__key_type

    @property
    def keyless_type(self) -> type[NK]:
        return self.__keyless_type

    @property
    def type_fields(self) -> list[str]:
        return self.__type_fields[:]

    @property
    def key_fields(self) -> list[str]:
        return self.__key_fields[:]

    @property
    def nonkey_fields(self) -> list[str]:
        return self.__nonkey_fields[:]

    def keyof(self, value: T) -> K:
        key_fields: list[str] = self.key_fields
        d: dict[str, Any] = as_dict(value)
        for f in [*d.keys()]:
            if f not in key_fields:
                del d[f]
        return from_dict(data_class = self.key_type, data = d)

    def nonkeyof(self, value: T) -> NK:
        key_fields: list[str] = self.key_fields
        d: dict[str, Any] = as_dict(value)
        for f in [*d.keys()]:
            if f in key_fields:
                del d[f]
        return from_dict(data_class = self.keyless_type, data = d)

    def glue(self, key: K, values: NK) -> T:
        d1: dict[str, Any] = as_dict(key)
        d2: dict[str, Any] = as_dict(values)
        return from_dict(data_class = self.type_class, data = d1 | d2)

    def __check_subfields(self, subtype: type[X], role: str) -> None:
        if not is_dataclass(subtype):
            raise KeyError(f"The {role} {subtype.__name__} is not a dataclass.")
        where_fields: list[str] = [field.name for field in fields(subtype)]
        for f in where_fields:
            if f not in self.__type_fields:
                raise KeyError(f"The field {f} from {role} {subtype.__name__} is not in type_class {self.__type_class.__name__}.")

    def lone_where(self, where_type: type[X]) -> str:
        self.__check_subfields(where_type, "where_type")
        assert is_dataclass(where_type)
        where_fields: list[str] = [field.name for field in fields(where_type)]
        criteria: str = " AND ".join([x + " = ?" for x in where_fields])
        if criteria == "": return ""
        return " WHERE " + criteria

    def sql_insert(self) -> str:
        field_list: list[str] = self.__nonkey_fields if self.__key_is_autoincrement else self.__type_fields
        set_fields: str = ", ".join(field_list)
        wildcards: str = ", ".join(["?" for f in field_list])
        return f"INSERT INTO {self.__table_name} ({set_fields}) VALUES ({wildcards})"

    def insert_autoincrement(self) -> Callable[[TransactedConnection, NK], T]:
        if not self.key_is_autoincrement: raise KeyError("This table isn't autoincrement. Use the insert method.")
        sql: str = self.sql_insert()
        def tx(cf: TransactedConnection, value: NK) -> T:
            data: list[Any] = as_list(value)
            cf.execute(sql, data)
            key: K = from_dict(data_class = self.key_type, data = {self.key_fields[0] : cf.lastrowid})
            return self.glue(key, value)
        return tx

    def insert(self) -> Callable[[TransactedConnection, T], T]:
        if self.key_is_autoincrement: raise KeyError("This table is autoincrement. Use the insert_autoincrement method.")
        sql: str = self.sql_insert()
        def tx(cf: TransactedConnection, value: T) -> T:
            data: list[Any] = as_list(value)
            cf.execute(sql, data)
            return value
        return tx

    def sql_replace(self) -> str:
        field_list: list[str] = self.__type_fields
        set_fields: str = ", ".join(field_list)
        wildcards: str = ", ".join(["?" for f in field_list])
        return f"REPLACE INTO {self.__table_name} ({set_fields}) VALUES ({wildcards})"

    def save(self) -> Callable[[TransactedConnection, T], T]:
        sql: str = self.sql_replace()
        def tx(cf: TransactedConnection, value: T) -> T:
            data: list[Any] = as_list(value)
            cf.execute(sql, data)
            return value
        return tx

    def update_by_fields(self, criteria_type: type[X]) -> Callable[[TransactedConnection, T, X], T]:
        sql: str = self.sql_update_by_fields(criteria_type)
        def tx(cf: TransactedConnection, value: T, criteria: X) -> T:
            data: list[Any] = as_list(value) + as_list(criteria)
            cf.execute(sql, data)
            return value
        return tx

    def sql_update_by_key(self) -> str:
        return self.sql_update_by_fields(self.__key_type)

    def sql_update_by_fields(self, where_type: type[X]) -> str:
        where: str = self.lone_where(where_type)
        set_fields = ", ".join([x + " = ?" for x in self.__type_fields])
        return f"UPDATE {self.__table_name} SET {set_fields}{where}"

    def sql_delete_by_key(self) -> str:
        return self.sql_delete_by_fields(self.__key_type)

    def delete_by_key(self) -> Callable[[TransactedConnection, K], None]:
        sql: str = self.sql_delete_by_key()
        def tx(cf: TransactedConnection, key: K) -> None:
            data: list[Any] = as_list(key)
            cf.execute(sql, data)
        return tx

    def sql_delete_by_fields(self, where_type: type[X]) -> str:
        where: str = self.lone_where(where_type)
        return f"DELETE FROM {self.__table_name}{where}"

    def delete_by_fields(self, criteria_type: type[X]) -> Callable[[TransactedConnection, X], None]:
        sql: str = self.sql_delete_by_fields(criteria_type)
        def tx(cf: TransactedConnection, criteria: X) -> None:
            data: list[Any] = as_list(criteria)
            cf.execute(sql, data)
        return tx

    def sql_select_by_key(self) -> str:
        return self.sql_select_by_fields(self.__key_type)

    def select_by_key(self) -> Callable[[TransactedConnection, K], T | None]:
        sql: str = self.sql_select_by_key()
        def tx(cf: TransactedConnection, key: K) -> T | None:
            data: list[Any] = as_list(key)
            cf.execute(sql, data)
            return cf.fetchone_class(self.type_class)
        return tx

    def select_by_key_or_else(self, or_else: Callable[[], Exception]) -> Callable[[TransactedConnection, K], T]:
        sql: str = self.sql_select_by_key()
        def tx(cf: TransactedConnection, key: K) -> T:
            data: list[Any] = as_list(key)
            cf.execute(sql, data)
            instance: T | None = cf.fetchone_class(self.type_class)
            if instance is None: raise or_else()
            return instance
        return tx

    def sql_select_all(self) -> str:
        return self.sql_select_by_fields(Empty)

    def select_all(self) -> Callable[[TransactedConnection], list[T]]:
        sql: str = self.sql_select_all()
        def tx(cf: TransactedConnection) -> list[T]:
            cf.execute(sql)
            return cf.fetchall_class(self.type_class)
        return tx

    def select_many(self, size: int = 0) -> Callable[[TransactedConnection], list[T]]:
        sql: str = self.sql_select_all()
        def tx(cf: TransactedConnection) -> list[T]:
            cf.execute(sql)
            return cf.fetchmany_class(self.type_class, size)
        return tx

    def sql_select_by_fields(self, where_type: type[X]) -> str:
        where: str = self.lone_where(where_type)
        set_fields = ", ".join(self.__type_fields)
        return f"SELECT {set_fields} FROM {self.__table_name}{where}"

    def select_one_by_fields(self, criteria_type: type[X]) -> Callable[[TransactedConnection, X], T | None]:
        sql: str = self.sql_select_by_fields(criteria_type)
        def tx(cf: TransactedConnection, criteria: X) -> T | None:
            data: list[Any] = as_list(criteria)
            cf.execute(sql, data)
            return cf.fetchone_class(self.type_class)
        return tx

    def select_one_by_fields_or_else(self, criteria_type: type[X], or_else: Callable[[], Exception]) -> Callable[[TransactedConnection, X], T]:
        sql: str = self.sql_select_by_fields(criteria_type)
        def tx(cf: TransactedConnection, criteria: X) -> T:
            data: list[Any] = as_list(criteria)
            cf.execute(sql, data)
            instance: T | None = cf.fetchone_class(self.type_class)
            if instance is None: raise or_else()
            return instance
        return tx

    def select_all_by_fields(self, criteria_type: type[X]) -> Callable[[TransactedConnection, X], list[T]]:
        sql: str = self.sql_select_by_fields(criteria_type)
        def tx(cf: TransactedConnection, criteria: X) -> list[T]:
            data: list[Any] = as_list(criteria)
            cf.execute(sql, data)
            return cf.fetchall_class(self.type_class)
        return tx

    def select_many_by_fields(self, criteria_type: type[X]) -> Callable[[TransactedConnection, X, int], list[T]]:
        sql: str = self.sql_select_by_fields(criteria_type)
        def tx(cf: TransactedConnection, criteria: X, size: int = 0) -> list[T]:
            data: list[Any] = as_list(criteria)
            cf.execute(sql, data)
            return cf.fetchmany_class(self.type_class, size)
        return tx

    def alias(self, alias: str) -> From[T]:
        set_fields = ", ".join([alias + "." + n for n in self.__type_fields])
        return From(self.type_class, set_fields, self.table_name, alias)

del T
del K
del NK
del X