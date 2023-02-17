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

    def confirmar_que_usuario_ja_existe(self, quem: str) -> int:
        cf.execute("SELECT pk_usuario FROM INTO usuario WHERE login = ?", [quem])
        tupla = cf.fetchone()
        if tupla is None: raise UsuarioNaoExisteException()
        return int(tupla[0])

    def confirmar_que_usuario_nao_existe(self, quem: str) -> None:
        cf.execute("SELECT pk_usuario FROM INTO usuario WHERE login = ?", [quem])
        if cf.fetchone() is not None: raise UsuarioJaExisteException()

    def confirmar_que_categoria_ja_existe(self, nome: str) -> int:
        cf.execute("SELECT nome FROM INTO categoria WHERE nome = ?", [nome])
        tupla = cf.fetchone()
        if tupla is None: raise CategoriaNaoExisteException()
        return int(tupla[0])

    def confirmar_que_categoria_nao_existe(self, nome: str) -> None:
        cf.execute("SELECT nome FROM INTO categoria WHERE nome = ?", [nome])
        if cf.fetchone() is not None: raise CategoriaJaExisteException()

    # Pode lançar PermissaoNegadaException, UsuarioJaExisteException
    def criar_usuario(self, quem_faz: LoginUsuario, dados: UsuarioNovo) -> None:
        self.login_admin(quem_faz)
        self.confirmar_que_usuario_nao_existe(dados.login)
        hash_com_sal = criar_hash(dados.senha)
        cf.execute("INSERT INTO usuario(login, fk_nivel_acesso, hash_com_sal) VALUES (?, ?, ?)", [dados.login, dados.nivel_acesso.value, hash_com_sal])

    def trocar_senha(self, quem_faz: LoginUsuario, dados: NovaSenha) -> None:
        self.login(quem_faz)
        hash_com_sal = criar_hash(dados.senha)
        cf.execute("UPDATE usuario SET hash_com_sal = ? WHERE login = ?", [hash_com_sal, quem_faz.login])

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def resetar_senha(self, quem_faz: LoginUsuario, dados: ResetLoginUsuario) -> str:
        self.login_admin(quem_faz)
        self.confirmar_que_usuario_ja_existe(dados.login)
        nova_senha = string_random()
        hash_com_sal = criar_hash(nova_senha)
        cf.execute("UPDATE usuario SET hash_com_sal = ? WHERE login = ?", [hash_com_sal, dados.login])
        return nova_senha

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def alterar_nivel_de_acesso(self, quem_faz: LoginUsuario, dados: UsuarioComNivel) -> None:
        self.login_admin(quem_faz)
        self.confirmar_que_usuario_ja_existe(dados.login)
        cf.execute("UPDATE usuario SET fk_nivel_acesso = ? WHERE login = ?", [dados.nivel_acesso.value, dados.login])

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def listar_usuarios(self, quem_faz: LoginUsuario) -> ResultadoUsuario:
        self.login(quem_faz)
        cf.execute("SELECT login, nivel_acesso FROM usuario")
        return ResultadoUsuario(segredos = cf.fetchall_class(UsuarioComNivel))

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    def criar_segredo(self, quem_faz: LoginUsuario, dados: SegredoSemPK) -> None:
        self.login(quem_faz)

        pk_usuarios: dict[str, int] = {}
        for login in dados.usuarios:
            pk_usuarios[login] = self.confirmar_que_usuario_ja_existe(login)

        pk_categorias: dict[str, int] = {}
        for nome in dados.categorias:
            pk_categorias[nome] = self.confirmar_que_categoria_ja_existe(nome)

        cf.execute("INSERT INTO segredo(nome, descricao, fk_tipo_segredo) VALUES (?, ?, ?)", [dados.nome, dados.descricao, dados.tipo.value])
        rowid = cf.lastrowid
        if rowid is None: raise Exception("OPS")

        for descricao in dados.campos.keys():
            valor = dados.campos[descricao]
            cf.execute("INSERT INTO campo_segredo(pfk_segredo, pk_descricao, valor) VALUES (?, ?, ?)", [rowid, descricao, valor])

        for login in dados.usuarios.keys():
            pk_usuario = pk_usuarios[login]
            permissao = dados.usuarios[login]
            cf.execute("INSERT INTO permissao(pfk_usuario, pfk_segredo, fk_tipo_permissao) VALUES (?, ?, ?)", [pk_usuario, rowid, permissao])

        for nome in dados.categorias:
            pk_categoria = pk_categorias[nome]
            cf.execute("INSERT INTO categoria_segredo(pfk_segredo, pfk_categoria) VALUES (?, ?)", [rowid, pk_categoria])

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException
    def alterar_segredo(self, quem_faz: LoginUsuario, dados: SegredoComPK) -> None:
        self.login(quem_faz)
        raise NotImplementedError()

    # Pode lançar SegredoNaoExisteException
    def excluir_segredo(self, quem_faz: LoginUsuario, dados: SegredoPK) -> None:
        self.login(quem_faz)
        raise NotImplementedError()

    def listar_segredos(self, quem_faz: LoginUsuario) -> ResultadoPesquisa:
        self.login(quem_faz)
        raise NotImplementedError()

    # Pode lançar CategoriaNaoExisteException
    def pesquisar_segredos(self, quem_faz: LoginUsuario, dados: PesquisaSegredos) -> ResultadoPesquisa:
        self.login(quem_faz)
        raise NotImplementedError()

    # Pode lançar CategoriaJaExisteException
    def criar_categoria(self, quem_faz: LoginUsuario, dados: NomeCategoria) -> None:
        self.login_admin(quem_faz)
        self.confirmar_que_categoria_nao_existe(dados.nome)
        cf.execute("INSERT INTO categoria(nome) VALUES (?)", [dados.nome])

    # Pode lançar CategoriaJaExisteException, CategoriaNaoExisteException
    def renomear_categoria(self, quem_faz: LoginUsuario, dados: RenomeCategoria) -> None:
        self.login_admin(quem_faz)
        self.confirmar_que_categoria_ja_existe(dados.antigo)
        self.confirmar_que_categoria_nao_existe(dados.novo)
        cf.execute("UPDATE categoria SET nome = ? WHERE nome = ?", [dados.novo, dados.antigo])

    # Pode lançar CategoriaNaoExisteException
    def excluir_categoria(self, quem_faz: LoginUsuario, dados: NomeCategoria) -> None:
        self.login_admin(quem_faz)
        self.confirmar_que_categoria_ja_existe(dados.nome)
        cf.execute("DELETE categoria WHERE nome = ?", [dados.nome])