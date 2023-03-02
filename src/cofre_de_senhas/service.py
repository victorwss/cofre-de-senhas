import sqlite3
import hashlib
from connection.conn import TransactedConnection
from connection.sqlite3conn import Sqlite3ConnectionWrapper
from .model import *
from decorators.tracer import Logger
from decorators.for_all import for_all_methods

def string_random() -> str:
    import random
    import string
    letters = string.ascii_letters
    return "".join(random.choice(letters) for i in range(10))

def criar_hash(senha: str) -> str:
    sal = string_random()
    return sal + hashlib.sha3_224((sal + senha).encode("utf-8")).hexdigest()

def comparar_hash(senha: str, hash: str) -> bool:
    sal = hash[0:10]
    return sal + hashlib.sha3_224((sal + senha).encode("utf-8")).hexdigest() == hash

log = Logger.for_print_fn()
cf = TransactedConnection(lambda: Sqlite3ConnectionWrapper(sqlite3.connect("banco.db")))

# Todos os métodos podem lançar SenhaErradaException ou UsuarioBanidoException.
@for_all_methods(log.trace)
@for_all_methods(cf.transact)
class CofreDeSenhasImpl(CofreDeSenhas):

    def login(self, quem_faz: LoginUsuario) -> NivelAcesso:
        cf.execute("SELECT fk_nivel_acesso, hash_com_sal FROM usuario WHERE login = ?", [quem_faz.login])
        cadastrado = cf.fetchone_class(DadosLogin)
        if cadastrado is None or not comparar_hash(quem_faz.senha, cadastrado.hash_com_sal): raise SenhaErradaException()
        if cadastrado.fk_nivel_acesso == NivelAcesso.BANIDO: raise UsuarioBanidoException()
        return cadastrado.fk_nivel_acesso

    def login_admin(self, quem_faz: LoginUsuario) -> None:
        acesso = self.login(quem_faz)
        if acesso != NivelAcesso.CHAVEIRO_DEUS_SUPREMO: raise PermissaoNegadaException()

    def __confirmar_que_usuario_ja_existe(self, quem: str) -> int:
        cf.execute("SELECT pk_usuario FROM usuario WHERE login = ?", [quem])
        tupla = cf.fetchone()
        if tupla is None: raise UsuarioNaoExisteException()
        return int(tupla[0])

    def __confirmar_que_usuario_nao_existe(self, quem: str) -> None:
        cf.execute("SELECT pk_usuario FROM usuario WHERE login = ?", [quem])
        if cf.fetchone() is not None: raise UsuarioJaExisteException()

    def __confirmar_que_categoria_ja_existe(self, nome: str) -> int:
        cf.execute("SELECT nome FROM categoria WHERE nome = ?", [nome])
        tupla = cf.fetchone()
        if tupla is None: raise CategoriaNaoExisteException()
        return int(tupla[0])

    def __confirmar_que_categoria_nao_existe(self, nome: str) -> None:
        cf.execute("SELECT nome FROM categoria WHERE nome = ?", [nome])
        if cf.fetchone() is not None: raise CategoriaJaExisteException()

    def __confirmar_que_segredo_ja_existe(self, pk: SegredoPK) -> int:
        cf.execute("SELECT pk_segredo FROM segredo WHERE pk_segredo = ?", [pk.valor])
        tupla = cf.fetchone()
        if tupla is None: raise SegredoNaoExisteException()
        return int(tupla[0])

    # Pode lançar PermissaoNegadaException, UsuarioJaExisteException
    def criar_usuario(self, quem_faz: LoginUsuario, dados: UsuarioNovo) -> None:
        self.login_admin(quem_faz)
        self.__confirmar_que_usuario_nao_existe(dados.login)
        hash_com_sal = criar_hash(dados.senha)
        cf.execute("INSERT INTO usuario(login, fk_nivel_acesso, hash_com_sal) VALUES (?, ?, ?)", [dados.login, dados.nivel_acesso.value, hash_com_sal])

    def trocar_senha(self, quem_faz: LoginUsuario, dados: NovaSenha) -> None:
        self.login(quem_faz)
        hash_com_sal = criar_hash(dados.senha)
        cf.execute("UPDATE usuario SET hash_com_sal = ? WHERE login = ?", [hash_com_sal, quem_faz.login])

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def resetar_senha(self, quem_faz: LoginUsuario, dados: ResetLoginUsuario) -> str:
        self.login_admin(quem_faz)
        self.__confirmar_que_usuario_ja_existe(dados.login)
        nova_senha = string_random()
        hash_com_sal = criar_hash(nova_senha)
        cf.execute("UPDATE usuario SET hash_com_sal = ? WHERE login = ?", [hash_com_sal, dados.login])
        return nova_senha

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def alterar_nivel_de_acesso(self, quem_faz: LoginUsuario, dados: UsuarioComNivel) -> None:
        self.login_admin(quem_faz)
        self.__confirmar_que_usuario_ja_existe(dados.login)
        cf.execute("UPDATE usuario SET fk_nivel_acesso = ? WHERE login = ?", [dados.nivel_acesso.value, dados.login])

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def listar_usuarios(self, quem_faz: LoginUsuario) -> ResultadoUsuario:
        self.login(quem_faz)
        cf.execute("SELECT login, nivel_acesso FROM usuario")
        return ResultadoUsuario(segredos = cf.fetchall_class(UsuarioComNivel))

    def __mapear_usuarios(self, logins: list[str]) -> dict[str, int]:
        pk_usuarios: dict[str, int] = {}
        for login in logins:
            pk_usuarios[login] = self.__confirmar_que_usuario_ja_existe(login)
        return pk_usuarios

    def __mapear_categorias(self, nomes: list[str]) -> dict[str, int]:
        pk_categorias: dict[str, int] = {}
        for nome in nomes:
            pk_categorias[nome] = self.__confirmar_que_categoria_ja_existe(nome)
        return pk_categorias

    def __alterar_dados_segredo(self, dados: SegredoComPK) -> None:
        cf.execute("DELETE FROM campo_segredo WHERE pfk_segredo = ?", [rowid])
        for descricao in dados.campos.keys():
            valor = dados.campos[descricao]
            cf.execute("INSERT INTO campo_segredo(pfk_segredo, pk_descricao, valor) VALUES (?, ?, ?)", [rowid, descricao, valor])

        cf.execute("DELETE FROM permissao WHERE pfk_segredo = ?", [rowid])
        for login in dados.usuarios.keys():
            pk_usuario = pk_usuarios[login]
            permissao = dados.usuarios[login]
            cf.execute("INSERT INTO permissao(pfk_usuario, pfk_segredo, fk_tipo_permissao) VALUES (?, ?, ?)", [pk_usuario, rowid, permissao])

        cf.execute("DELETE FROM categoria_segredo WHERE pfk_segredo = ?", [rowid])
        for nome in dados.categorias:
            pk_categoria = pk_categorias[nome]
            cf.execute("INSERT INTO categoria_segredo(pfk_segredo, pfk_categoria) VALUES (?, ?)", [rowid, pk_categoria])

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    def criar_segredo(self, quem_faz: LoginUsuario, dados: SegredoSemPK) -> None:
        self.login(quem_faz)

        if dados.usuarios[quem_faz.login] != TipoPermissao.PROPRIETARIO: raise PermissaoNegadaException

        pk_usuarios: dict[str, int] = self.__mapear_usuarios(dados.usuarios)
        pk_categorias: dict[str, int] = self.__mapear_categorias(dados.usuarios)

        cf.execute("INSERT INTO segredo(nome, descricao, fk_tipo_segredo) VALUES (?, ?, ?)", [dados.nome, dados.descricao, dados.tipo.value])
        rowid = cf.lastrowid
        assert rowid is not None

        self.__alterar_dados_segredo(dados.com_pk(SegredoPK(rowid)))

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException, PermissaoNegadaException
    def alterar_segredo(self, quem_faz: LoginUsuario, dados: SegredoComPK) -> None:
        self.login(quem_faz)

        self.__confirmar_que_segredo_ja_existe(dados.pk) # Pode lançar SegredoNaoExisteException
        pk_usuarios: dict[str, int] = self.__mapear_usuarios(dados.usuarios)
        pk_categorias: dict[str, int] = self.__mapear_categorias(dados.usuarios)

        rowid = dados.pk.valor
        cf.execute("UPDATE segredo SET nome = ?, descricao = ?, fk_tipo_segredo = ? WHERE pk_segredo = ?", [dados.nome, dados.descricao, dados.tipo.value, dados.pk.valor])

        self.__alterar_dados_segredo(dados)

    # Pode lançar SegredoNaoExisteException, PermissaoNegadaException
    def excluir_segredo(self, quem_faz: LoginUsuario, dados: SegredoPK) -> None:
        nivel = self.login(quem_faz)

        self.__confirmar_que_segredo_ja_existe(dados) # Pode lançar SegredoNaoExisteException

        if nivel == NivelAcesso.NORMAL:
            cf.execute("SELECT p.fk_tipo_permissao FROM permissao p INNER JOIN usuario u ON u.pk_usuario = p.pfk_usuario WHERE p.pfk_segredo = ? AND u.login = ?", [dados, quem_faz.login])
            tupla = cf.fetchone()
            if tupla is None: raise PermissaoNegadaException
            permissao: TipoPermissao = TipoPermissao.por_codigo(tupla[0])
            if permissao not in [TipoPermissao.LEITURA_E_ESCRITA, TipoPermissao.PROPRIETARIO]: raise PermissaoNegadaException
        elif nivel == NivelAcesso.CHAVEIRO_DEUS_SUPREMO:
            pass
        else:
            assert false

        cf.execute("DELETE FROM segredo WHERE pk_segredo = ?", [dados.pk.valor]) # Deleta nas outras tabelas graças ao ON DELETE CASCADE.

    def listar_segredos(self, quem_faz: LoginUsuario) -> ResultadoPesquisa:
        @dataclass_validate(strict = True)
        @dataclass(frozen = True)

        nivel = self.login(quem_faz)
        if acesso == NivelAcesso.CHAVEIRO_DEUS_SUPREMO:
            cf.execute("SELECT * FROM segredo")
        else:
            cf.execute("SELECT s.* FROM segredo s INNER JOIN permissao p ON p.pfk_segredo = s.pk_segredo INNER JOIN usuario u ON p.pfk_usuario = u.pk_usuario")
        return ResultadoPesquisa(cf.fetchall_class(SegredoComPK))

    # Pode lançar SegredoNaoExisteException
    def buscar_segredo(self, quem_faz: LoginUsuario, pk: SegredoPK) -> SegredoComPK:
        acesso: NivelAcesso = self.login(quem_faz)
        valor_pk = pk.valor

        cf.execute("SELECT nome, descricao, fk_tipo_segredo FROM segredo WHERE pk_segredo = ?", [valor_pk])
        tupla = cf.fetchone()
        if tupla is None: raise SegredoNaoExisteException()

        nome: str = tupla[0]
        descricao: str = tupla[1]
        tipo: TipoSegredo = TipoSegredo.por_codigo(tupla[2])

        cf.execute("SELECT c.pk_chave, c.valor FROM campo_segredo WHERE pfk_segredo = ?", [valor_pk])
        campos: dict[str, str] = {a: b for (a, b) in cf.fetchall()}

        cf.execute("SELECT c.nome FROM categoria c INNER JOIN categoria_segredo cs ON c.pk_categoria = cs.pfk_categoria WHERE cs.pfk_segredo = ?", [valor_pk])
        categorias: list[str] = [a for a in cf.fetchall()]

        cf.execute("SELECT u.login, p.fk_tipo_permissao FROM permissao p INNER JOIN usuario u ON u.pk_usuario = p.pfk_usuario WHERE p.pfk_segredo = ?", [valor_pk])
        usuarios: dict[str, TipoPermissao] = {a: TipoPermissao.por_codigo(b) for (a, b) in cf.fetchall()}

        if acesso != NivelAcesso.CHAVEIRO_DEUS_SUPREMO && quem_faz.login not in usuarios: raise SegredoNaoExisteException()

        return SegredoComPK(valor_pk, nome, descricao, tipo, campos, categorias, usuarios)

    # Pode lançar CategoriaNaoExisteException
    def pesquisar_segredos(self, quem_faz: LoginUsuario, dados: PesquisaSegredos) -> ResultadoPesquisa:
        self.login(quem_faz)
        raise NotImplementedError()

    # Pode lançar CategoriaJaExisteException
    def criar_categoria(self, quem_faz: LoginUsuario, dados: NomeCategoria) -> None:
        self.login_admin(quem_faz)
        self.__confirmar_que_categoria_nao_existe(dados.nome)
        cf.execute("INSERT INTO categoria(nome) VALUES (?)", [dados.nome])

    # Pode lançar CategoriaJaExisteException, CategoriaNaoExisteException
    def renomear_categoria(self, quem_faz: LoginUsuario, dados: RenomeCategoria) -> None:
        self.login_admin(quem_faz)
        self.__confirmar_que_categoria_ja_existe(dados.antigo)
        self.__confirmar_que_categoria_nao_existe(dados.novo)
        cf.execute("UPDATE categoria SET nome = ? WHERE nome = ?", [dados.novo, dados.antigo])

    # Pode lançar CategoriaNaoExisteException
    def excluir_categoria(self, quem_faz: LoginUsuario, dados: NomeCategoria) -> None:
        self.login_admin(quem_faz)
        self.__confirmar_que_categoria_ja_existe(dados.nome)
        cf.execute("DELETE categoria WHERE nome = ?", [dados.nome])