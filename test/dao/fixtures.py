from ..db_test_util import *
from cofre_de_senhas.dao import \
    UsuarioPK, DadosUsuario, DadosUsuarioSemPK, LoginUsuario, \
    CategoriaPK, DadosCategoria, DadosCategoriaSemPK, NomeCategoria, \
    SegredoPK, DadosSegredo, DadosSegredoSemPK

def read_all(fn: str) -> str:
    import os
    with open(os.getcwd() + "/" + fn, "r", encoding = "utf-8") as f:
        return f.read()

mysql_clear: str = read_all("src/mariadb-create.sql").replace("$$$$", "test_cofre") + "\n" + read_all("test/test-mass.sql")

sqlite_db : SqliteTestConfig  = SqliteTestConfig ("test/cofre-teste.db", "test/cofre-teste-run.db")
mysql_db  : MysqlTestConfig   = MysqlTestConfig  (mysql_clear, "root", "root", "127.0.0.1", 3306, "test_cofre")
mariadb_db: MariaDbTestConfig = MariaDbTestConfig(mysql_clear, "root", "root", "127.0.0.1", 3306, "test_cofre", 3)

dbs: dict[str, DbTestConfig] = { \
    "sqlite" : sqlite_db , \
    "mysql"  : mysql_db  , \
    "mariadb": mariadb_db  \
}

def assert_db_ok(db: DbTestConfig) -> None:
    assert db in dbs.values(), f"Database connector failed to load. {len(dbs)}"

alohomora       : str = "SbhhiMEETzPiquOxabc178eb35f26c8f59981b01a11cbec48b16f6a8e2c204f4a9a1b633c9199e0b3b2a64b13e49226306bb451c57c851f3c6e872885115404cb74279db7f5372ea"
avada_kedavra   : str = "ZisNWkdEImMneIcX8ac8780d30e67df14c1afbaf256e1ee45afd1d3cf2654d154b2e9c63541a40d4132a9beed69c4a47b3f2e5612c2751cdfa3abfaed9797fe54777e2f3dfe6aaa0"
expecto_patronum: str = "sMIIsuQpzUZswvbW8bc81f083ae783d5dc4f4ae688b6d41d7c5d4b0da55bdb6f42d07453031c046ed4151d0cead5e647f307f96701e586dbb38e197222b645807f10f7b4c124d68c"
sectumsempra    : str = "VaVnCicwVrQUJaCR39f3afe61dd624f7c3fb3da1ca1249bcb938d35dce3af64910ac3341c5f15cd1bfa2f1312ed3f89ceee2b126c834176f8202f5aca0e43fd8c5eea6a036c7f9b5"
expelliarmus    : str = "VPJWqamYPZTUKxsxe79b2fdd41d88c308f2be7c92432d68c9d55ecc9fb9b277c1424d5626777b6e26067875b5a28f10d64db83e41a7537b21850d1bd8359b8e9bfe68e7acb02ff1d"

nome_curto = "ABC"
nome_longo = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxy"

harry_potter: DadosUsuario = DadosUsuario(1, "Harry Potter", 1, alohomora       )
voldemort   : DadosUsuario = DadosUsuario(2, "Voldemort"   , 0, avada_kedavra   )
dumbledore  : DadosUsuario = DadosUsuario(3, "Dumbledore"  , 2, expecto_patronum)
hermione    : DadosUsuario = DadosUsuario(4, "Hermione"    , 1, expelliarmus    )
snape       : DadosUsuario = DadosUsuario(5, "Snape"       , 1, sectumsempra    )

snape_sem_pk: DadosUsuarioSemPK = DadosUsuarioSemPK("Snape", 1, sectumsempra)

login_harry_potter = LoginUsuario("Harry Potter")
login_voldemort    = LoginUsuario("Voldemort")
login_dumbledore   = LoginUsuario("Dumbledore")
login_hermione     = LoginUsuario("Hermione")
login_snape        = LoginUsuario("Snape")

login_lixo_1       = LoginUsuario("Dollynho")
login_lixo_2       = LoginUsuario("Papai Noel")
login_lixo_3       = LoginUsuario("Faustão")

todos_usuarios: list[DadosUsuario] = [harry_potter, voldemort, dumbledore, hermione]
parte_usuarios: list[DadosUsuario] = [harry_potter, dumbledore]

banco_de_dados  : DadosCategoria = DadosCategoria( 1, "Banco de dados"  )
aplicacao       : DadosCategoria = DadosCategoria( 2, "Aplicação"       )
servidor        : DadosCategoria = DadosCategoria( 3, "Servidor"        )
api             : DadosCategoria = DadosCategoria( 4, "API"             )
producao        : DadosCategoria = DadosCategoria( 5, "Produção"        )
homologacao     : DadosCategoria = DadosCategoria( 6, "Homologação"     )
desenvolvimento : DadosCategoria = DadosCategoria( 7, "Desenvolvimento" )
qa              : DadosCategoria = DadosCategoria( 8, "QA"              )
integracao      : DadosCategoria = DadosCategoria( 9, "Integração"      )
millenium_falcon: DadosCategoria = DadosCategoria(10, "Millenium Falcon")
nao_existe      : DadosCategoria = DadosCategoria(88, "Coisas feitas com boa qualidade pela Prodam")

dados_millenium_falcon: DadosCategoriaSemPK = DadosCategoriaSemPK("Millenium Falcon")
nome_millenium_falcon : NomeCategoria = NomeCategoria("Millenium Falcon")
nome_producao         : NomeCategoria = NomeCategoria("Produção")
nome_qa               : NomeCategoria = NomeCategoria("QA")
nome_nao_existe       : NomeCategoria = NomeCategoria("Coisas feitas com boa qualidade pela Prodam")

todas_categorias: list[DadosCategoria] = [banco_de_dados, aplicacao, servidor, api, producao, homologacao, desenvolvimento, qa, integracao]
parte_categorias: list[DadosCategoria] = [api, producao, homologacao]

segredo_m1: DadosSegredo = DadosSegredo(-1, "Cofre de senhas" , "Segredos acerca do guardador de segredos.", 2)
dbz       : DadosSegredo = DadosSegredo( 1, "Dragon Ball Z"   , "Segredos acerca de Dragon Ball Z."        , 3)
lotr      : DadosSegredo = DadosSegredo( 2, "Senhor dos Anéis", "Segredos acerca do Senhor dos Anéis."     , 2)
star_wars : DadosSegredo = DadosSegredo( 3, "Star Wars"       , "Guerra nas estrelas."                     , 1)
star_trek : DadosSegredo = DadosSegredo( 4, "Star Trek"       , "Jornada nas estrelas."                    , 2)

star_trek_sem_pk: DadosSegredoSemPK = DadosSegredoSemPK("Star Trek", "Jornada nas estrelas.", 2)

todos_segredos: list[DadosSegredo] = [segredo_m1, dbz, lotr, star_wars]
parte_segredos: list[DadosSegredo] = [lotr, star_wars]
visiv_segredos: list[DadosSegredo] = [segredo_m1, lotr, star_wars]

lixo1: int = 444
lixo2: int = 555
lixo3: int = 666