from typing import override
from .db_test_util import DbTestConfig, SqliteTestConfig, MariaDbTestConfig, MysqlTestConfig
from cofre_de_senhas.dao import DadosUsuario, DadosUsuarioSemPK, DadosCategoria, DadosCategoriaSemPK, DadosSegredo, DadosSegredoSemPK
from cofre_de_senhas.erro import UsuarioNaoLogadoException
from connection.trans import TransactedConnection
from cofre_de_senhas.service import GerenciadorLogin, ChaveUsuario, UsuarioComChave
from cofre_de_senhas.service_impl import Servicos


def read_all(fn: str) -> str:
    import os
    with open(os.getcwd() + "/" + fn, "r", encoding = "utf-8") as f:
        return f.read()


def assert_db_ok(db: DbTestConfig) -> None:
    assert db in dbs.values(), f"Database connector failed to load. {len(dbs)}"


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


mysql_clear: str = read_all("src/mariadb-create.sql").replace("$$$$", "test_cofre") + "\n" + read_all("test/test-mass.sql")
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

alohomora       : str = "SbhhiMEETzPiquOxabc178eb35f26c8f59981b01a11cbec48b16f6a8e2c204f4a9a1b633c9199e0b3b2a64b13e49226306bb451c57c851f3c6e872885115404cb74279db7f5372ea"  # noqa: E203,E501
avada_kedavra   : str = "ZisNWkdEImMneIcX8ac8780d30e67df14c1afbaf256e1ee45afd1d3cf2654d154b2e9c63541a40d4132a9beed69c4a47b3f2e5612c2751cdfa3abfaed9797fe54777e2f3dfe6aaa0"  # noqa: E203,E501
expecto_patronum: str = "sMIIsuQpzUZswvbW8bc81f083ae783d5dc4f4ae688b6d41d7c5d4b0da55bdb6f42d07453031c046ed4151d0cead5e647f307f96701e586dbb38e197222b645807f10f7b4c124d68c"  # noqa: E203,E501
sectumsempra    : str = "VaVnCicwVrQUJaCR39f3afe61dd624f7c3fb3da1ca1249bcb938d35dce3af64910ac3341c5f15cd1bfa2f1312ed3f89ceee2b126c834176f8202f5aca0e43fd8c5eea6a036c7f9b5"  # noqa: E203,E501
expelliarmus    : str = "VPJWqamYPZTUKxsxe79b2fdd41d88c308f2be7c92432d68c9d55ecc9fb9b277c1424d5626777b6e26067875b5a28f10d64db83e41a7537b21850d1bd8359b8e9bfe68e7acb02ff1d"  # noqa: E203,E501

nome_curto: str = "ABC"
nome_longo: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxy"

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

nome_em_branco: str = ""
nome_longo_demais: str = alohomora + alohomora + alohomora + alohomora

todas_categorias: list[DadosCategoria] = [banco_de_dados, aplicacao, servidor, api, producao, homologacao, desenvolvimento, qa, integracao]
parte_categorias: list[DadosCategoria] = [api, producao, homologacao]

segredo_m1: DadosSegredo = DadosSegredo(-1, "Cofre de senhas" , "Segredos acerca do guardador de segredos.", 2)  # noqa: E201,E203
dbz       : DadosSegredo = DadosSegredo( 1, "Dragon Ball Z"   , "Segredos acerca de Dragon Ball Z."        , 3)  # noqa: E201,E203
lotr      : DadosSegredo = DadosSegredo( 2, "Senhor dos Anéis", "Segredos acerca do Senhor dos Anéis."     , 2)  # noqa: E201,E203
star_wars : DadosSegredo = DadosSegredo( 3, "Star Wars"       , "Guerra nas estrelas."                     , 1)  # noqa: E201,E203
star_trek : DadosSegredo = DadosSegredo( 4, "Star Trek"       , "Jornada nas estrelas."                    , 2)  # noqa: E201,E203

star_trek_sem_pk: DadosSegredoSemPK = DadosSegredoSemPK("Star Trek", "Jornada nas estrelas.", 2)

todos_segredos: list[DadosSegredo] = [segredo_m1, dbz, lotr, star_wars]
parte_segredos: list[DadosSegredo] = [lotr, star_wars]
visiv_segredos: list[DadosSegredo] = [segredo_m1, lotr, star_wars]

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

    def verificar(self) -> None:
        assert self.__chamada == 1

    @override
    def logout(self) -> None:
        assert False

    @property
    @override
    def usuario_logado(self) -> ChaveUsuario | UsuarioNaoLogadoException:
        assert False


def servicos_normal(c: TransactedConnection) -> Servicos:
    return Servicos(GerenciadorLoginChave(ChaveUsuario(harry_potter.pk_usuario)), c)


def servicos_admin(c: TransactedConnection) -> Servicos:
    return Servicos(GerenciadorLoginChave(ChaveUsuario(dumbledore.pk_usuario)), c)


def servicos_banido(c: TransactedConnection) -> Servicos:
    return Servicos(GerenciadorLoginChave(ChaveUsuario(voldemort.pk_usuario)), c)


def servicos_usuario_nao_existe(c: TransactedConnection) -> Servicos:
    return Servicos(GerenciadorLoginChave(ChaveUsuario(lixo2)), c)


def servicos_nao_logado(c: TransactedConnection) -> Servicos:
    return Servicos(GerenciadorLoginNaoLogado(), c)


def servicos_nao_logar(c: TransactedConnection) -> Servicos:
    return Servicos(GerenciadorLoginFalha(), c)
