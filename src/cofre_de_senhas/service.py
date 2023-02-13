# Todos os métodos podem lançar SenhaErradaException ou UsuarioBanidoException.

import sqlite3
from contextlib import closing
from typing import Any, Callable, cast, TypeVar
import hashlib
from functools import wraps
from conn import TransactedConnection
from sqlite3conn import Sqlite3Connection
from model import *

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

FuncT = TypeVar("FuncT", bound = Callable[..., Any])

def trace(func: FuncT) -> FuncT:
    @wraps(func)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        print(f"Calling {func} - Args: {args} - Kwargs: {kwargs}")
        try:
            r = func(*args, **kwargs)
            print(f"Call of {func} returned {r}.")
            return r
        except BaseException as x:
            print(f"Call of {func} raised {x}.")
            raise x
    return cast(FuncT, wrapped)

cf = TransactedConnection(lambda: Sqlite3Connection(sqlite3.connect("banco.db")))

class CofreDeSenhasImpl(CofreDeSenhas):

    @cf.transact
    def login(self, quem_faz: LoginUsuario) -> None:
        cf.execute("SELECT hash_com_sal FROM usuario WHERE login = ?", [quem_faz.login])
        tupla = cf.fetchone()
        if tupla is None:
            raise SenhaErradaException
        hash_com_sal = tupla[0]
        if not comparar_hash(quem_faz.senha, hash_com_sal):
            raise SenhaErradaException

    # Pode lançar PermissaoNegadaException, UsuarioJaExisteException
    @cf.transact
    def criar_usuario(self, quem_faz: LoginUsuario, dados: UsuarioNovo) -> None:
        self.login(quem_faz)
        hash_com_sal = criar_hash(dados.senha)
        cf.execute("INSERT INTO usuario(login, fk_nivel_acesso, hash_com_sal) VALUES (?, ?, ?)", [dados.login, dados.nivel_acesso, hash_com_sal])

    @cf.transact
    def trocar_senha(self, quem_faz: LoginUsuario, dados: NovaSenha) -> None:
        self.login(quem_faz)
        hash_com_sal = criar_hash(dados.senha)
        cf.execute("UPDATE usuario SET hash_com_sal = ? WHERE login = ?", [hash_com_sal, quem_faz.login])

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @cf.transact
    def resetar_senha(self, quem_faz: LoginUsuario, dados: ResetLoginUsuario) -> str:
        self.login(quem_faz)
        nova_senha = string_random()
        hash_com_sal = criar_hash(nova_senha)
        cf.execute("UPDATE usuario SET hash_com_sal = ? WHERE login = ?", [hash_com_sal, dados.login])
        return nova_senha

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @cf.transact
    def alterar_nivel_de_acesso(self, quem_faz: LoginUsuario, dados: UsuarioComNivel) -> None:
        self.login(quem_faz)
        cf.execute("UPDATE usuario SET fk_nivel_acesso = ? WHERE login = ?", [dados.nivel_acesso, dados.login])

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @cf.transact
    def listar_usuarios(self, quem_faz: LoginUsuario) -> ResultadoUsuario:
        self.login(quem_faz)
        raise NotImplementedError()

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    @cf.transact
    def criar_segredo(self, quem_faz: LoginUsuario, dados: SegredoSemPK) -> None:
        self.login(quem_faz)
        raise NotImplementedError()

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException
    @cf.transact
    def alterar_segredo(self, quem_faz: LoginUsuario, dados: SegredoComPK) -> None:
        self.login(quem_faz)
        raise NotImplementedError()

    # Pode lançar SegredoNaoExisteException
    @cf.transact
    def excluir_segredo(self, quem_faz: LoginUsuario, dados: SegredoPK) -> None:
        self.login(quem_faz)
        raise NotImplementedError()

    @cf.transact
    def listar_segredos(self, quem_faz: LoginUsuario) -> ResultadoPesquisa:
        self.login(quem_faz)
        raise NotImplementedError()

    # Pode lançar CategoriaNaoExisteException
    @cf.transact
    def pesquisar_segredos(self, quem_faz: LoginUsuario, dados: PesquisaSegredos) -> ResultadoPesquisa:
        self.login(quem_faz)
        raise NotImplementedError()

    # Pode lançar CategoriaJaExisteException
    @cf.transact
    def criar_categoria(self, quem_faz: LoginUsuario, dados: NomeCategoria) -> None:
        self.login(quem_faz)
        raise NotImplementedError()

    # Pode lançar CategoriaJaExisteException, CategoriaNaoExisteException
    @cf.transact
    def renomear_categoria(self, quem_faz: LoginUsuario, dados: RenomeCategoria) -> None:
        self.login(quem_faz)
        raise NotImplementedError()

    # Pode lançar CategoriaNaoExisteException
    @cf.transact
    def excluir_categoria(self, quem_faz: LoginUsuario, dados: NomeCategoria) -> None:
        self.login(quem_faz)
        raise NotImplementedError()