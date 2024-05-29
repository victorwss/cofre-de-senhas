from typing import Callable, Literal, override, ParamSpec, Self, Sequence, TypeVar, TypeAlias
from abc import ABC, abstractmethod
from types import TracebackType
from functools import wraps
from cofre_de_senhas.dao import DadosUsuario, DadosUsuarioSemPK, DadosCategoria, DadosCategoriaSemPK, DadosSegredo, DadosSegredoSemPK
from cofre_de_senhas.erro import UsuarioNaoLogadoException
from cofre_de_senhas.service import (
    GerenciadorLogin, Servicos,
    ChaveUsuario, UsuarioComChave, LoginComSenha
)
from cofre_de_senhas.service_impl import ServicosImpl
from cofre_de_senhas.service_client import ServicosClient
from cofre_de_senhas.controller import servir
from connection.conn import SimpleConnection, Descriptor, RAW_DATA
from connection.trans import TransactedConnection
from connection.load import DatabaseConfig
import os
import shutil
from pytest import mark


_P = ParamSpec("_P")
_R = TypeVar("_R")


class DbTestConfig(ABC):

    def __init__(self, placeholder: str, database_type: str, database_name: str, maker: Callable[[], TransactedConnection]) -> None:
        self.__maker: Callable[[], TransactedConnection] = maker
        self.__conn: TransactedConnection | None = None
        self.__placeholder: str = placeholder
        self.__database_name: str = database_name
        self.__database_type: str = database_type

    def _poor_execute_script(self, script: str) -> None:
        with self._maker() as conn:
            for part in script.split(";"):
                if part.strip() != "":
                    conn.execute(part)
            conn.commit()

    @property
    @abstractmethod
    def local_decorator(self) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        pass

    @property
    @abstractmethod
    def remote_decorator(self) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        pass

    @property
    def transacted(self) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        def middle(call_this: Callable[_P, _R]) -> Callable[_P, _R]:
            @wraps(call_this)
            @self.local_decorator
            def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                @self.conn.transact
                def innermost() -> _R:
                    return call_this(*args, **kwargs)
                return innermost()
            return inner
        return middle

    @property
    def _maker(self) -> Callable[[], TransactedConnection]:
        return self.__maker

    def _set_conn(self, conn: TransactedConnection) -> TransactedConnection:
        self.__conn = conn
        return conn

    def _del_conn(self) -> None:
        if self.__conn is not None:
            self.__conn.close()
        self.__conn = None

    @property
    def conn(self) -> TransactedConnection:
        assert self.__conn is not None
        return self.__conn

    @property
    def placeholder(self) -> str:
        return self.__placeholder

    @property
    def database_type(self) -> str:
        return self.__database_type

    @property
    def database_name(self) -> str:
        return self.__database_name


class SqliteTestConfig(DbTestConfig):

    def __init__(self, pristine: str, sandbox: str) -> None:
        def inner() -> TransactedConnection:
            from connection.sqlite3conn import connect
            return connect(sandbox)

        super().__init__("?", "Sqlite", sandbox, inner)
        self.__pristine: str = pristine
        self.__sandbox: str = sandbox

    @property
    @override
    def local_decorator(self) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        def middle(call_this: Callable[_P, _R]) -> Callable[_P, _R]:
            @wraps(call_this)
            def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                try:
                    os.remove(self.__sandbox)
                except FileNotFoundError:
                    pass

                shutil.copy2(self.__pristine, self.__sandbox)

                self._set_conn(self._maker())
                try:
                    return call_this(*args, **kwargs)
                finally:
                    self._del_conn()
                    os.remove(self.__sandbox)

            return inner
        return middle

    @property
    @override
    def remote_decorator(self) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        def middle(call_this: Callable[_P, _R]) -> Callable[_P, _R]:
            @wraps(call_this)
            def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                try:
                    os.remove(self.__sandbox)
                except FileNotFoundError:
                    pass

                shutil.copy2(self.__pristine, self.__sandbox)

                # self._set_conn(self._maker())
                try:
                    return call_this(*args, **kwargs)
                finally:
                    # self._del_conn()
                    os.remove(self.__sandbox)

            return inner
        return middle

    @property
    def sandbox(self) -> str:
        return self.__sandbox


class MariaDbTestConfig(DbTestConfig):

    def __init__(self, reset_script: str, user: str, password: str, host: str, port: int, database: str, connect_timeout: int) -> None:
        def inner() -> TransactedConnection:
            from connection.mariadbconn import connect
            return connect(user = user, password = password, host = host, port = port, database = database, connect_timeout = connect_timeout)

        super().__init__("%s", "MariaDB", database, inner)
        self.__reset_script: str = reset_script

    @property
    @override
    def local_decorator(self) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        def middle(call_this: Callable[_P, _R]) -> Callable[_P, _R]:
            @wraps(call_this)
            def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                self._poor_execute_script(self.__reset_script)

                self._set_conn(self._maker())
                try:
                    return call_this(*args, **kwargs)
                finally:
                    self._del_conn()
                    self._poor_execute_script(self.__reset_script)

            return inner
        return middle

    @property
    @override
    def remote_decorator(self) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        assert False


class MysqlTestConfig(DbTestConfig):

    def __init__(self, reset_script: str, user: str, password: str, host: str, port: int, database: str) -> None:
        def inner() -> TransactedConnection:
            from connection.mysqlconn import connect
            return connect(user = user, password = password, host = host, port = port, database = database)

        super().__init__("%s", "MySQL", database, inner)
        self.__reset_script: str = reset_script

    @property
    @override
    def local_decorator(self) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        def middle(call_this: Callable[_P, _R]) -> Callable[_P, _R]:
            @wraps(call_this)
            def inner(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                self._poor_execute_script(self.__reset_script)

                self._set_conn(self._maker())
                try:
                    return call_this(*args, **kwargs)
                finally:
                    self._del_conn()
                    self._poor_execute_script(self.__reset_script)

            return inner
        return middle

    @property
    @override
    def remote_decorator(self) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        assert False


def read_all(fn: str) -> str:
    import os
    with open(os.getcwd() + "/" + fn, "r", encoding = "utf-8") as f:
        return f.read()


def mix(nome: str) -> str:
    out: str = ""
    a: bool = True
    for x in range(0, len(nome)):
        n: str = nome[x]
        if a:
            out += n.lower()
        else:
            out += n.upper()
        a = not a
    return out


alohomora       : str = "SbhhiMEETzPiquOxabc178eb35f26c8f59981b01a11cbec48b16f6a8e2c204f4a9a1b633c9199e0b3b2a64b13e49226306bb451c57c851f3c6e872885115404cb74279db7f5372ea"  # noqa: E203,E501
avada_kedavra   : str = "ZisNWkdEImMneIcX8ac8780d30e67df14c1afbaf256e1ee45afd1d3cf2654d154b2e9c63541a40d4132a9beed69c4a47b3f2e5612c2751cdfa3abfaed9797fe54777e2f3dfe6aaa0"  # noqa: E203,E501
expecto_patronum: str = "sMIIsuQpzUZswvbW8bc81f083ae783d5dc4f4ae688b6d41d7c5d4b0da55bdb6f42d07453031c046ed4151d0cead5e647f307f96701e586dbb38e197222b645807f10f7b4c124d68c"  # noqa: E203,E501
sectumsempra    : str = "VaVnCicwVrQUJaCR39f3afe61dd624f7c3fb3da1ca1249bcb938d35dce3af64910ac3341c5f15cd1bfa2f1312ed3f89ceee2b126c834176f8202f5aca0e43fd8c5eea6a036c7f9b5"  # noqa: E203,E501
expelliarmus    : str = "VPJWqamYPZTUKxsxe79b2fdd41d88c308f2be7c92432d68c9d55ecc9fb9b277c1424d5626777b6e26067875b5a28f10d64db83e41a7537b21850d1bd8359b8e9bfe68e7acb02ff1d"  # noqa: E203,E501

nome_curto: str = "ABC"
nome_longo: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxy"
nome_em_branco: str = ""
nome_muito_curto: str = "Z"
nome_longo_demais: str = alohomora + alohomora + alohomora + alohomora

harry_potter: DadosUsuario = DadosUsuario(1, "Harry Potter", 1, alohomora       )  # noqa: E202,E203
voldemort   : DadosUsuario = DadosUsuario(2, "Voldemort"   , 0, avada_kedavra   )  # noqa: E202,E203
dumbledore  : DadosUsuario = DadosUsuario(3, "Dumbledore"  , 2, expecto_patronum)  # noqa: E202,E203
hermione    : DadosUsuario = DadosUsuario(4, "Hermione"    , 1, expelliarmus    )  # noqa: E202,E203
snape       : DadosUsuario = DadosUsuario(5, "Snape"       , 1, sectumsempra    )  # noqa: E202,E203

snape_sem_pk: DadosUsuarioSemPK = DadosUsuarioSemPK("Snape", 1, sectumsempra)

todos_usuarios: list[DadosUsuario] = [harry_potter, voldemort, dumbledore, hermione]
parte_usuarios: list[DadosUsuario] = [harry_potter, dumbledore]

banco_de_dados  : DadosCategoria = DadosCategoria( 1, "Banco de dados"                             )  # noqa: E201,E202,E203
aplicacao       : DadosCategoria = DadosCategoria( 2, "Aplicação"                                  )  # noqa: E201,E202,E203
servidor        : DadosCategoria = DadosCategoria( 3, "Servidor"                                   )  # noqa: E201,E202,E203
api             : DadosCategoria = DadosCategoria( 4, "API"                                        )  # noqa: E201,E202,E203
producao        : DadosCategoria = DadosCategoria( 5, "Produção"                                   )  # noqa: E201,E202,E203
homologacao     : DadosCategoria = DadosCategoria( 6, "Homologação"                                )  # noqa: E201,E202,E203
desenvolvimento : DadosCategoria = DadosCategoria( 7, "Desenvolvimento"                            )  # noqa: E201,E202,E203
qa              : DadosCategoria = DadosCategoria( 8, "QA"                                         )  # noqa: E201,E202,E203
integracao      : DadosCategoria = DadosCategoria( 9, "Integração"                                 )  # noqa: E201,E202,E203
millenium_falcon: DadosCategoria = DadosCategoria(10, "Millenium Falcon"                           )  # noqa: E201,E202,E203
nao_existe      : DadosCategoria = DadosCategoria(88, "Coisas feitas com boa qualidade pela Prodam")  # noqa: E201,E202,E203

dados_millenium_falcon: DadosCategoriaSemPK = DadosCategoriaSemPK("Millenium Falcon")

todas_categorias: list[DadosCategoria] = [banco_de_dados, aplicacao, servidor, api, producao, homologacao, desenvolvimento, qa, integracao]
parte_categorias: list[DadosCategoria] = [api, producao, homologacao]

segredo_m1 : DadosSegredo = DadosSegredo(-1, "Cofre de senhas" , "Segredos acerca do guardador de segredos.", 2)  # noqa: E201,E203
dbz        : DadosSegredo = DadosSegredo( 1, "Dragon Ball Z"   , "Segredos acerca de Dragon Ball Z."        , 3)  # noqa: E201,E203
lotr       : DadosSegredo = DadosSegredo( 2, "Senhor dos Anéis", "Segredos acerca do Senhor dos Anéis."     , 2)  # noqa: E201,E203
star_wars  : DadosSegredo = DadosSegredo( 3, "Star Wars"       , "Guerra nas estrelas."                     , 1)  # noqa: E201,E203
oppenheimer: DadosSegredo = DadosSegredo( 4, "Oppenheimer"     , "Bomba atômica."                           , 3)  # noqa: E201,E203
star_trek  : DadosSegredo = DadosSegredo( 5, "Star Trek"       , "Jornada nas estrelas."                    , 2)  # noqa: E201,E203

star_trek_sem_pk: DadosSegredoSemPK = DadosSegredoSemPK("Star Trek", "Jornada nas estrelas.", 2)

todos_segredos: list[DadosSegredo] = [segredo_m1, dbz, lotr, star_wars, oppenheimer]
parte_segredos: list[DadosSegredo] = [lotr, star_wars]
visiv_segredos: list[DadosSegredo] = [segredo_m1, lotr, star_wars]
harry_segredos: list[DadosSegredo] = [segredo_m1, dbz, lotr, star_wars]
hermi_segredos: list[DadosSegredo] = [segredo_m1, lotr, star_wars, oppenheimer]

lixo1: int = 444
lixo2: int = 555
lixo3: int = 666
lixo4: str = "Melancia"
lixo5: str = "Cachorro"
lixo6: str = "Garfo"


class GerenciadorLoginFalha(GerenciadorLogin):

    @override
    def login(self, usuario: UsuarioComChave) -> None:
        assert False

    @override
    def logout(self) -> None:
        assert False

    @property
    @override
    def usuario_logado(self) -> ChaveUsuario | UsuarioNaoLogadoException:
        assert False


class GerenciadorLoginNaoLogado(GerenciadorLogin):

    @override
    def login(self, usuario: UsuarioComChave) -> None:
        assert False

    @override
    def logout(self) -> None:
        assert False

    @property
    @override
    def usuario_logado(self) -> ChaveUsuario | UsuarioNaoLogadoException:
        return UsuarioNaoLogadoException()


class GerenciadorLoginChave(GerenciadorLogin):

    def __init__(self, chave: ChaveUsuario) -> None:
        self.__chave: ChaveUsuario = chave

    @override
    def login(self, usuario: UsuarioComChave) -> None:
        assert False

    @override
    def logout(self) -> None:
        assert False

    @property
    @override
    def usuario_logado(self) -> ChaveUsuario | UsuarioNaoLogadoException:
        return self.__chave


class GerenciadorLoginSimples(GerenciadorLogin):

    def __init__(self) -> None:
        self.__chave: ChaveUsuario | None = None

    @override
    def login(self, usuario: UsuarioComChave) -> None:
        self.__chave = usuario.chave

    @override
    def logout(self) -> None:
        self.__chave = None

    @property
    @override
    def usuario_logado(self) -> ChaveUsuario | UsuarioNaoLogadoException:
        if self.__chave is None:
            return UsuarioNaoLogadoException()
        return self.__chave


class GerenciadorFazLogin(GerenciadorLogin):

    def __init__(self, chave: ChaveUsuario) -> None:
        self.__chave: ChaveUsuario = chave
        self.__chamada: int = 0

    @override
    def login(self, usuario: UsuarioComChave) -> None:
        assert usuario.chave == self.__chave
        self.__chamada += 1

    @override
    def logout(self) -> None:
        assert False

    @property
    @override
    def usuario_logado(self) -> ChaveUsuario | UsuarioNaoLogadoException:
        assert False

    def verificar(self) -> None:
        assert self.__chamada == 1


class GerenciadorLogout(GerenciadorLogin):

    def __init__(self) -> None:
        self.__chamou = False

    @override
    def login(self, usuario: UsuarioComChave) -> None:
        assert False

    @override
    def logout(self) -> None:
        assert not self.__chamou
        self.__chamou = True

    @property
    @override
    def usuario_logado(self) -> ChaveUsuario | UsuarioNaoLogadoException:
        assert False

    def verificar(self) -> None:
        assert self.__chamou


class _NoConnection(SimpleConnection):

    def __init__(self, callback: Callable[[str], None]) -> None:
        self.__commited: bool = False
        self.__closed: bool = False
        self.__callback: Callable[[str], None] = callback

    @property
    def commited(self) -> bool:
        return self.__commited

    @override
    def commit(self) -> None:
        if self.__commited or self.__closed:
            assert False
        self.__commited = True
        self.__callback("commit")

    @override
    def rollback(self) -> None:
        assert False

    @override
    def close(self) -> None:
        if self.__closed:
            assert False
        self.__closed = True
        self.__callback("close")

    @override
    def fetchone(self) -> tuple[RAW_DATA, ...] | None:
        assert False

    @override
    def fetchall(self) -> Sequence[tuple[RAW_DATA, ...]]:
        assert False

    @override
    def fetchmany(self, size: int = 0) -> Sequence[tuple[RAW_DATA, ...]]:
        assert False

    @override
    def callproc(self, sql: str, parameters: Sequence[RAW_DATA] = ()) -> Self:
        assert False

    @override
    def execute(self, sql: str, parameters: Sequence[RAW_DATA] = ()) -> Self:
        assert False

    @override
    def executemany(self, sql: str, parameters: Sequence[Sequence[RAW_DATA]] = ()) -> Self:
        assert False

    @override
    def executescript(self, sql: str) -> Self:
        assert False

    @property
    @override
    def rowcount(self) -> int:
        assert False

    @property
    @override
    def description(self) -> Descriptor:
        assert False

    @property
    @override
    def lastrowid(self) -> int | None:
        assert False

    @property
    @override
    def raw_connection(self) -> object:
        assert False

    @property
    @override
    def raw_cursor(self) -> object:
        assert False

    @property
    @override
    def placeholder(self) -> str:
        assert False

    @property
    @override
    def autocommit(self) -> Literal[False]:
        return False

    @property
    @override
    def database_type(self) -> str:
        assert False

    @property
    @override
    def database_name(self) -> str:
        assert False


def no_transaction(callback: Callable[[str], None]) -> TransactedConnection:
    n: _NoConnection = _NoConnection(callback)

    def activate() -> _NoConnection:
        return n

    return TransactedConnection(activate, "BAD BAD BAD", "BAD BAD BAD", "BAD BAD BAD")


class ContextoServico:

    def __enter__(self) -> Self:
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,  # noqa: E203,E221
            exc_val : BaseException       | None,  # noqa: E203,E221
            exc_tb  : TracebackType       | None   # noqa: E203,E221
    ) -> Literal[False]:
        return False

    @property
    @abstractmethod
    def servicos(self) -> Servicos:
        pass

    @abstractmethod
    def local_connect(self) -> TransactedConnection:
        pass


class ContextoServicoLocal(ContextoServico):

    def __init__(self, serv: Servicos, conn: TransactedConnection) -> None:
        self.__serv: Servicos = serv
        self.__conn: TransactedConnection = conn

    @property
    def servicos(self) -> Servicos:
        return self.__serv

    @override
    def local_connect(self) -> TransactedConnection:
        return self.__conn


class ContextoOperacao(ABC):

    @abstractmethod
    def servicos_normal(self) -> ContextoServico:
        pass

    @abstractmethod
    def servicos_normal2(self) -> ContextoServico:
        pass

    @abstractmethod
    def servicos_admin(self) -> ContextoServico:
        pass

    @abstractmethod
    def servicos_banido(self) -> ContextoServico:
        pass

    @abstractmethod
    def servicos_usuario_nao_existe(self) -> ContextoServico:
        pass

    @abstractmethod
    def servicos_nao_logar(self) -> ContextoServico:
        pass

    @property
    @abstractmethod
    def decorator(self) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        pass


class ContextoOperacaoLocal(ContextoOperacao):

    def __init__(self, db: DbTestConfig) -> None:
        self.__db: DbTestConfig = db
        self.__gl: GerenciadorLogin | None = None

    @property
    def db(self) -> DbTestConfig:
        return self.__db

    @property
    def conn(self) -> TransactedConnection:
        return self.db.conn

    @override
    def servicos_normal(self) -> ContextoServicoLocal:
        self.__gl = GerenciadorLoginChave(ChaveUsuario(harry_potter.pk_usuario))
        return self.__make

    def servicos_normal_login(self) -> ContextoServicoLocal:
        self.__gl = GerenciadorFazLogin(ChaveUsuario(harry_potter.pk_usuario))
        return self.__make

    @override
    def servicos_normal2(self) -> ContextoServicoLocal:
        self.__gl = GerenciadorLoginChave(ChaveUsuario(hermione.pk_usuario))
        return self.__make

    def servicos_normal2_login(self) -> ContextoServicoLocal:
        self.__gl = GerenciadorFazLogin(ChaveUsuario(hermione.pk_usuario))
        return self.__make

    @override
    def servicos_admin(self) -> ContextoServicoLocal:
        self.__gl = GerenciadorLoginChave(ChaveUsuario(dumbledore.pk_usuario))
        return self.__make

    def servicos_admin_login(self) -> ContextoServicoLocal:
        self.__gl = GerenciadorFazLogin(ChaveUsuario(dumbledore.pk_usuario))
        return self.__make

    @override
    def servicos_banido(self) -> ContextoServicoLocal:
        self.__gl = GerenciadorLoginChave(ChaveUsuario(voldemort.pk_usuario))
        return self.__make

    def servicos_banido_login(self) -> ContextoServicoLocal:
        self.__gl = GerenciadorFazLogin(ChaveUsuario(voldemort.pk_usuario))
        return self.__make

    @override
    def servicos_usuario_nao_existe(self) -> ContextoServico:
        self.__gl = GerenciadorLoginChave(ChaveUsuario(lixo2))
        return self.__make

    def servicos_usuario_nao_existe_login(self) -> ContextoServicoLocal:
        self.__gl = GerenciadorFazLogin(ChaveUsuario(lixo2))
        return self.__make

    @override
    def servicos_nao_logar(self) -> ContextoServico:
        self.__gl = GerenciadorLoginNaoLogado()
        return self.__make

    @property
    def __make(self) -> ContextoServicoLocal:
        assert self.__gl is not None
        return ContextoServicoLocal(ServicosImpl(self.__gl, self.conn), self.conn)

    def verificar(self) -> None:
        assert isinstance(self.__gl, GerenciadorFazLogin) or isinstance(self.__gl, GerenciadorLogout)
        self.__gl.verificar()

    @property
    @override
    def decorator(self) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        return self.db.local_decorator


class ContextoServicoRemoto(ContextoServico):

    def __init__(self, dbtcfg: SqliteTestConfig, login: str | None, senha: str | None, modo: str) -> None:
        self.__cfg: DatabaseConfig = DatabaseConfig("sqlite", {"file_name": dbtcfg.sandbox})
        self.__sair: Callable[[], None] | None = None
        self.__inner: Servicos | None = None
        self.__login: str | None = login
        self.__senha: str | None = senha
        self.__modo: str = modo

    def __enter__(self) -> Self:
        ok: bool = False
        try:
            self.__sair = servir(5000, self.__cfg)
            self.__inner = ServicosClient("http://127.0.0.1:5000")
            if self.__login is not None and self.__senha is not None:

                if self.__modo == "UPDATE":
                    with self.local_connect() as t:
                        t.execute("UPDATE usuario SET fk_nivel_acesso = 1 WHERE login = ?", [self.__login])
                if self.__modo == "CREATE":
                    with self.local_connect() as t:
                        t.execute("INSERT INTO usuario (login, fk_nivel_acesso, hash_com_sal) VALUES (?, 1, ?)", [self.__login, avada_kedavra])

                x: UsuarioComChave | BaseException = self.__inner.usuario.login(LoginComSenha(self.__login, self.__senha))
                if isinstance(x, BaseException):
                    raise x

                if self.__modo == "UPDATE":
                    with self.local_connect() as t:
                        t.execute("UPDATE usuario SET fk_nivel_acesso = 0 WHERE login = ?", [self.__login])
                if self.__modo == "CREATE":
                    with self.local_connect() as t:
                        t.execute("DELETE FROM usuario WHERE login = ?", [self.__login])
            ok = True
            return self
        finally:
            if not ok:
                if self.__sair is not None:
                    self.__sair()
                self.__sair = None
                self.__inner = None

    def __exit__(
            self,
            exc_type: type[BaseException] | None,  # noqa: E203,E221
            exc_val : BaseException       | None,  # noqa: E203,E221
            exc_tb  : TracebackType       | None   # noqa: E203,E221
    ) -> Literal[False]:
        if self.__sair is not None:
            self.__sair()
        return False

    @override
    @property
    def servicos(self) -> Servicos:
        assert self.__inner is not None
        return self.__inner

    @override
    def local_connect(self) -> TransactedConnection:
        return self.__cfg.connect()


class ContextoOperacaoRemoto(ContextoOperacao):

    def __init__(self, dbtcfg: SqliteTestConfig) -> None:
        self.__dbtcfg: SqliteTestConfig = dbtcfg

    @override
    def servicos_normal(self) -> ContextoServico:
        return ContextoServicoRemoto(self.__dbtcfg, "Harry Potter", "alohomora", "OK")

    @override
    def servicos_normal2(self) -> ContextoServico:
        return ContextoServicoRemoto(self.__dbtcfg, "Hermione", "expelliarmus", "OK")

    @override
    def servicos_admin(self) -> ContextoServico:
        return ContextoServicoRemoto(self.__dbtcfg, "Dumbledore", "expecto patronum", "OK")

    @override
    def servicos_banido(self) -> ContextoServico:
        return ContextoServicoRemoto(self.__dbtcfg, "Voldemort", "avada kedavra", "UPDATE")

    @override
    def servicos_usuario_nao_existe(self) -> ContextoServico:
        return ContextoServicoRemoto(self.__dbtcfg, lixo4, "avada kedavra", "CREATE")

    @override
    def servicos_nao_logar(self) -> ContextoServico:
        return ContextoServicoRemoto(self.__dbtcfg, None, None, "OK")

    @property
    @override
    def decorator(self) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
        return self.__dbtcfg.remote_decorator


mysql_clear: str = read_all("src/mariadb-create.sql") + "\n" + read_all("test/test-mass.sql")
mysql_reset: str = read_all("test/create-fruits-mysql.sql")
sqlite_create: str = read_all("test/create-fruits-sqlite.sql")

sqlite_db   : SqliteTestConfig  = SqliteTestConfig ("test/cofre-teste.db", "test/cofre-teste-run.db"                   )  # noqa: E202,E203,E211,E221
sqlite_db_f : SqliteTestConfig  = SqliteTestConfig ("test/fruits-ok.db"  , "test/fruits.db"                            )  # noqa: E202,E203,E211,E221
sqlite_db_x : SqliteTestConfig  = SqliteTestConfig ("test/empty.db"      , "test/cofre-teste-create-run.db"            )  # noqa: E202,E203,E211,E221
mysql_db    : MysqlTestConfig   = MysqlTestConfig  (mysql_clear, "root", "root", "mariadb", 3306, "test_cofre"         )  # noqa: E202,E203,E211,E221
mysql_db_f  : MysqlTestConfig   = MysqlTestConfig  (mysql_reset, "root", "root", "mariadb", 3306, "test_fruits"        )  # noqa: E202,E203,E211,E221
mysql_db_x  : MysqlTestConfig   = MysqlTestConfig  (""         , "root", "root", "mariadb", 3306, "test_cofre_empty"   )  # noqa: E202,E203,E211,E221
mariadb_db  : MariaDbTestConfig = MariaDbTestConfig(mysql_clear, "root", "root", "mariadb", 3306, "test_cofre"      , 5)  # noqa: E202,E203,E211,E221
mariadb_db_f: MariaDbTestConfig = MariaDbTestConfig(mysql_reset, "root", "root", "mariadb", 3306, "test_fruits"     , 5)  # noqa: E202,E203,E211,E221
mariadb_db_x: MariaDbTestConfig = MariaDbTestConfig(""         , "root", "root", "mariadb", 3306, "test_cofre_empty", 3)  # noqa: E202,E203,E211,E221

dbs: dict[str, DbTestConfig] = {
    "sqlite" : sqlite_db   ,  # noqa: E203
    "mysql"  : mysql_db    ,  # noqa: E203
    "mariadb": mariadb_db     # noqa: E203
}

dbs_f: dict[str, DbTestConfig] = {
    "sqlite" : sqlite_db_f ,  # noqa: E203
    "mysql"  : mysql_db_f  ,  # noqa: E203
    "mariadb": mariadb_db_f   # noqa: E203
}

dbs_x: dict[str, DbTestConfig] = {
    "sqlite" : sqlite_db_x ,  # noqa: E203
    "mysql"  : mysql_db_x  ,  # noqa: E203
    "mariadb": mariadb_db_x   # noqa: E203
}

ctxs_local: dict[str, ContextoOperacaoLocal] = {
    "sqlite" : ContextoOperacaoLocal(sqlite_db ),  # noqa: E202,E203,E211
    "mysql"  : ContextoOperacaoLocal(mysql_db  ),  # noqa: E202,E203,E211
    "mariadb": ContextoOperacaoLocal(mariadb_db)   # noqa: E202,E203,E211
}

ctxs_remoto: dict[str, ContextoOperacaoRemoto] = {
    "remoto" : ContextoOperacaoRemoto(sqlite_db )   # noqa: E202,E203
}

ctxs: dict[str, ContextoOperacao] = {}
ctxs.update(ctxs_local)
ctxs.update(ctxs_remoto)


def assert_db_ok(db: DbTestConfig) -> None:
    assert db in dbs.values(), f"Database connector failed to load. {len(dbs)}"


def assert_dbf_ok(db: DbTestConfig) -> None:
    assert db in dbs_f.values(), f"Database connector failed to load. {len(dbs)}"


def _do_nothing(which: DbTestConfig) -> None:
    pass


_CO = TypeVar("_CO", bound = ContextoOperacao)
_A: TypeAlias = Callable[[DbTestConfig], None]
_B: TypeAlias = Callable[[TransactedConnection], None]
_C: TypeAlias = Callable[[TransactedConnection, DbTestConfig], None]
_D: TypeAlias = Callable[[str], None]
_E: TypeAlias = dict[str, DbTestConfig]


def applier(appliances: _E, pretest: _A = _do_nothing) -> Callable[[_A], _D]:
    def outer(applied: _A) -> _D:
        @mark.parametrize("db", appliances.keys())
        @wraps(applied)
        def middle(db: str) -> None:
            dbc: DbTestConfig = appliances[db]
            pretest(dbc)

            @wraps(applied)
            @dbc.local_decorator
            def call() -> None:
                applied(dbc)

            call()

        return middle
    return outer


def applier_trans(appliances: _E, pretest: _A = _do_nothing) -> Callable[[_B], _D]:
    def outer(applied: _B) -> _D:
        @applier(appliances, pretest)
        def inner(db: DbTestConfig) -> None:
            conn: TransactedConnection = db.conn
            with conn as c:
                applied(c)

        return inner
    return outer


def applier_trans2(appliances: _E, pretest: _A = _do_nothing) -> Callable[[_C], _D]:
    def outer(applied: _C) -> _D:
        @applier(appliances, pretest)
        def inner(db: DbTestConfig) -> None:
            conn: TransactedConnection = db.conn
            with conn as c:
                applied(c, db)

        return inner
    return outer


def applier_ctx_tipo(t: dict[str, _CO], applied: Callable[[_CO], None]) -> _D:
    @mark.parametrize("co", t.keys())
    def inner(co: str) -> None:
        op: _CO = t[co]

        @wraps(applied)
        @op.decorator
        def call() -> None:
            opx: _CO = op
            if isinstance(op, ContextoOperacaoLocal):
                with op.conn:
                    applied(opx)
            else:
                applied(op)

        call()

    return inner


def applier_ctx(applied: Callable[[ContextoOperacao], None]) -> _D:
    return applier_ctx_tipo(ctxs, applied)


def applier_ctx_local(applied: Callable[[ContextoOperacaoLocal], None]) -> _D:
    return applier_ctx_tipo(ctxs_local, applied)


def applier_ctx_remoto(applied: Callable[[ContextoOperacaoRemoto], None]) -> _D:
    return applier_ctx_tipo(ctxs_remoto, applied)
