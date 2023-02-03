# Todos os métodos podem lançar SenhaErradaException ou UsuarioBanidoException.

import sqlite3
from contextlib import closing
import hashlib

class DAO:
    def login(quem_faz: LoginUsuario) -> None:
        with conectar() as con, a.cursor() as cur:

def string_random():
    import random
    import string
    letters = string.ascii_letters
    return "".join(random.choice(letters) for i in range(10))

def criar_hash(senha):
    sal = string_random()
    return sal + hashlib.sha3_224((sal + senha).encode("utf-8")).hexdigest()

def comparar_hash(senha, hash):
    sal = hash[0:10]
    return sal + hashlib.sha3_224((sal + senha).encode("utf-8")).hexdigest() == hash

FuncT = TypeVar("FuncT", bound = Callable[..., Any])
FuncC = TypeVar("FuncC", bound = Callable[[], Conexao])

def trace(func: FuncT) -> FuncT:
    @wraps(func)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        print(f"Calling {func} - Args: {args} - Kwargs: {kwargs}")
        try:
            r = func(*args, **kwargs)
            print(f"Call of {func} returned {r}")
            return r
        except x:
            print(f"Call of {func} raised {x}")
            raise x
    return cast(FuncT, wrapped)

def conectado(func: FuncT, FuncC) -> FuncT:
    @wraps(func)
    def wrapped(*args: Any, **kwargs: Any) -> Any:

class CofreDeSenhasImpl(CofreDeSenhas):

    def __conectar(self):
        return sqlite3.connect("banco.db")

    def __verificar_login(self, con, cur, quem_faz: LoginUsuario) -> None:
        cur.execute("SELECT hash_com_sal FROM usuario WHERE login = ?", [quem_faz.login])
        tupla = cur.fetchone()
        if tupla is None:
            raise SenhaErradaException
        hash_com_sal = tupla[0]
        if not comparar_hash(quem_faz.senha, hash_com_sal):
            raise SenhaErradaException

    # Pode lançar PermissaoNegadaException, UsuarioJaExisteException
    def criar_usuario(self, quem_faz: LoginUsuario, dados: UsuarioComNivel) -> None:
        with closing(self.__conectar()) as con, closing(con.cursor()) as cur:
            self.__verificar_login(con, cur, quem_faz)
            hash_com_sal = criar_hash(dados.senha)
            cur.execute("INSERT INTO usuario(login, fk_nivel_acesso, hash_com_sal) VALUES (?, ?, ?)", [dados.login, dados.nivel_acesso, hash_com_sal])
            con.commit()

    def login(self, quem_faz: LoginUsuario) -> None:
        with closing(self.__conectar()) as con, closing(con.cursor()) as cur:
            self.__verificar_login(con, cur, quem_faz)

    def trocar_senha(self, quem_faz: LoginUsuario, dados: NovaSenha) -> None:
        with closing(self.__conectar()) as con, closing(con.cursor()) as cur:
            self.__verificar_login(con, cur, quem_faz)
            hash_com_sal = criar_hash(dados.senha)
            cur.execute("UPDATE usuario SET hash_com_sal = ? WHERE login = ?", [hash_com_sal, quem_faz.login])
            con.commit()

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def resetar_senha(self, quem_faz: LoginUsuario, dados: ResetLoginUsuario) -> str:
        with closing(self.__conectar()) as con, closing(con.cursor()) as cur:
            self.__verificar_login(con, cur, quem_faz)
            nova_senha = string_random()
            hash_com_sal = criar_hash(nova_senha)
            cur.execute("UPDATE usuario SET hash_com_sal = ? WHERE login = ?", [hash_com_sal, dados.login])
            con.commit()
            return nova_senha

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def alterar_nivel_de_acesso(self, quem_faz: LoginUsuario, dados: UsuarioComNivel) -> None:
        with closing(self.__conectar()) as con, closing(con.cursor()) as cur:
            self.__verificar_login(con, cur, quem_faz)
            hash_com_sal = criar_hash(dados.senha)
            cur.execute("UPDATE usuario SET fk_nivel_acesso = ? WHERE login = ?", [dados.nivel_acesso, dados.login])
            con.commit()

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def listar_usuarios(self, quem_faz: LoginUsuario) -> ResultadoUsuario:
        pass

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    def criar_segredo(self, quem_faz: LoginUsuario, dados: SegredoSemPK) -> None:
        pass

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException
    def alterar_segredo(self, quem_faz: LoginUsuario, dados: SegredoComPK) -> None:
        pass

    # Pode lançar SegredoNaoExisteException
    def excluir_segredo(self, quem_faz: LoginUsuario, dados: SegredoPK) -> None:
        pass

    def listar_segredos(self, quem_faz: LoginUsuario) -> ResultadoPesquisa:
        pass

    # Pode lançar CategoriaNaoExisteException
    def pesquisar_segredos(self, quem_faz: LoginUsuario, dados: PesquisaSegredos) -> ResultadoPesquisa:
        pass

    # Pode lançar CategoriaJaExisteException
    def criar_categoria(self, quem_faz: LoginUsuario, dados: NomeCategoria) -> None:
        pass

    # Pode lançar CategoriaJaExisteException, CategoriaNaoExisteException
    def renomear_categoria(self, quem_faz: LoginUsuario, dados: RenomeCategoria) -> None:
        pass

    # Pode lançar CategoriaNaoExisteException
    def excluir_categoria(self, quem_faz: LoginUsuario, dados: NomeCategoria) -> None:
        pass