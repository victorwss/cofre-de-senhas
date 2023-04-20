from typing import Any, cast, Callable, Generic, TypeVar
from dataclasses import asdict, dataclass, is_dataclass, fields
from dacite import from_dict
from connection.conn import TransactedConnection

T = TypeVar("T")
K = TypeVar("K")
NK = TypeVar("NK")
X = TypeVar("X")

@dataclass(frozen = True)
class Empty:
    pass

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

    def __check_subfields(self, subtype: type[X], role: str) -> None:
        if not is_dataclass(subtype):
            raise KeyError(f"The {role} {subtype.__name__} is not a dataclass.")
        where_fields: list[str] = [field.name for field in fields(subtype)]
        for f in where_fields:
            if f not in self.__type_fields:
                raise KeyError(f"The field {f} from {role} {subtype.__name__} is not in type_class {self.__type_class.__name__}.")

    def where(self, where_type: type[X]) -> str:
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

    def sql_replace(self) -> str:
        field_list: list[str] = self.__type_fields
        set_fields: str = ", ".join(field_list)
        wildcards: str = ", ".join(["?" for f in field_list])
        return f"REPLACE INTO {self.__table_name} ({set_fields}) VALUES ({wildcards})"

    def sql_update_by_key(self) -> str:
        return self.sql_update_by_fields(self.__key_type)

    def sql_update_by_fields(self, where_type: type[X]) -> str:
        where: str = self.where(where_type)
        set_fields = ", ".join([x + " = ?" for x in self.__type_fields])
        return f"UPDATE {self.__table_name} SET {set_fields}{where}"

    def sql_delete_by_key(self) -> str:
        return self.sql_delete_by_fields(self.__key_type)

    def sql_delete_by_fields(self, where_type: type[X]) -> str:
        where: str = self.where(where_type)
        return f"DELETE FROM {self.__table_name}{where}"

    def sql_select_by_key(self) -> str:
        return self.sql_select_by_fields(self.__key_type)

    def sql_select_all(self) -> str:
        return self.sql_select_by_fields(Empty)

    def sql_select_by_fields(self, where_type: type[X]) -> str:
        where: str = self.where(where_type)
        set_fields = ", ".join(self.__type_fields)
        return f"SELECT {set_fields} FROM {self.__table_name}{where}"

def as_list(value: X) -> list[Any]:
    assert is_dataclass(value) and not isinstance(value, type)
    return [*asdict(value).values()]

def as_dict(value: X) -> dict[str, Any]:
    assert is_dataclass(value) and not isinstance(value, type)
    return asdict(value)

class GenericDAO(Generic[T, K, NK]):

    def __init__(self, transacted_conn: TransactedConnection, table_name: str, type_class: type[T], key_type: type[K], keyless_type: type[NK], key_is_autoincrement: bool) -> None:
        self.__cf: TransactedConnection = transacted_conn
        self.__sqlf: SQLFactory[T, K, NK] = SQLFactory(table_name, type_class, key_type, keyless_type, key_is_autoincrement)

    def keyof(self, value: T) -> K:
        key_fields: list[str] = self.__sqlf.key_fields
        d: dict[str, Any] = as_dict(value)
        for f in [*d.keys()]:
            if f not in key_fields:
                del d[f]
        return from_dict(data_class = self.__sqlf.key_type, data = d)

    def nonkeyof(self, value: T) -> NK:
        key_fields: list[str] = self.__sqlf.key_fields
        d: dict[str, Any] = as_dict(value)
        for f in [*d.keys()]:
            if f in key_fields:
                del d[f]
        return from_dict(data_class = self.__sqlf.keyless_type, data = d)

    def join(self, key: K, values: NK) -> T:
        d1: dict[str, Any] = as_dict(key)
        d2: dict[str, Any] = as_dict(values)
        return from_dict(data_class = self.__sqlf.type_class, data = d1 | d2)

    def insert_autoincrement(self, value: NK) -> T:
        if not self.__sqlf.key_is_autoincrement: raise KeyError("This table isn't autoincrement. Use the insert method.")
        sql: str = self.__sqlf.sql_insert()
        data: list[Any] = as_list(value)
        self.__cf.execute(sql, data)
        key: K = from_dict(data_class = self.__sqlf.key_type, data = {self.__sqlf.key_fields[0] : self.__cf.lastrowid})
        return self.join(key, value)

    def insert(self, value: T) -> T:
        if self.__sqlf.key_is_autoincrement: raise KeyError("This table is autoincrement. Use the insert_autoincrement method.")
        sql: str = self.__sqlf.sql_insert()
        data: list[Any] = as_list(value)
        self.__cf.execute(sql, data)
        return value

    def save(self, value: T) -> T:
        sql: str = self.__sqlf.sql_replace()
        data: list[Any] = as_list(value)
        self.__cf.execute(sql, data)
        return value

    def update_by_fields(self, value: T, criteria: X) -> T:
        sql: str = self.__sqlf.sql_update_by_fields(criteria.__class__)
        data: list[Any] = as_list(value) + as_list(criteria)
        self.__cf.execute(sql, data)
        return value

    def delete_by_key(self, key: K) -> None:
        sql: str = self.__sqlf.sql_delete_by_key()
        data: list[Any] = as_list(key)
        self.__cf.execute(sql, data)

    def delete_by_fields(self, criteria: X) -> None:
        sql: str = self.__sqlf.sql_delete_by_fields(criteria.__class__)
        data: list[Any] = as_list(criteria)
        self.__cf.execute(sql, data)

    def select_by_key(self, key: K) -> T | None:
        sql: str = self.__sqlf.sql_select_by_key()
        data: list[Any] = as_list(key)
        self.__cf.execute(sql, data)
        return self.__cf.fetchone_class(self.__sqlf.type_class)

    def select_one_by_fields(self, criteria: X) -> T | None:
        sql: str = self.__sqlf.sql_select_by_fields(criteria.__class__)
        data: list[Any] = as_list(criteria)
        self.__cf.execute(sql, data)
        return self.__cf.fetchone_class(self.__sqlf.type_class)

    def select_all(self) -> list[T]:
        sql: str = self.__sqlf.sql_select_all()
        self.__cf.execute(sql)
        return self.__cf.fetchall_class(self.__sqlf.type_class)

    def select_all_by_fields(self, criteria: X) -> list[T]:
        sql: str = self.__sqlf.sql_select_by_fields(criteria.__class__)
        data: list[Any] = as_list(criteria)
        self.__cf.execute(sql, data)
        return self.__cf.fetchall_class(self.__sqlf.type_class)

    def select_many(self, size: int = 0) -> list[T]:
        sql: str = self.__sqlf.sql_select_all()
        self.__cf.execute(sql)
        return self.__cf.fetchmany_class(self.__sqlf.type_class, size)

    def select_many_by_fields(self, criteria: X, size: int = 0) -> list[T]:
        sql: str = self.__sqlf.sql_select_by_fields(criteria.__class__)
        data: list[Any] = as_list(criteria)
        self.__cf.execute(sql, data)
        return self.__cf.fetchmany_class(self.__sqlf.type_class, size)

del T
del K
del NK
del X