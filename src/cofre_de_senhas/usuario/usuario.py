import hasher
from typing import Self
from validator import dataclass_validate
from dataclasses import dataclass, replace
from cofre_de_senhas.erro import *
from cofre_de_senhas.dao import UsuarioDAO, UsuarioPK, DadosUsuario, DadosUsuarioComPermissao, DadosUsuarioSemPK, LoginUsuario as LoginUsuarioDAO
from cofre_de_senhas.service import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cofre_de_senhas.segredo.segredo import Segredo

@dataclass_validate
@dataclass(frozen = True)
class Permissao:
    usuario: "Usuario"
    tipo: TipoPermissao

@dataclass_validate
@dataclass(frozen = True)
class Usuario:
    pk_usuario: int
    login: str
    nivel_acesso: NivelAcesso
    hash_com_sal: str

    # Propriedades e métodos de instância.

    def __validar_senha(self, senha: str) -> None:
        if not hasher.comparar_hash(self.hash_com_sal, senha): raise SenhaErradaException()

    def __redefinir_senha(self, nova_senha: str) -> "Usuario":
        return replace(self, hash_com_sal = hasher.criar_hash(nova_senha)).__salvar()

    def __trocar_senha(self, dados: TrocaSenha) -> "Usuario":
        self.__validar_senha(dados.antiga)
        return self.__redefinir_senha(dados.nova)

    def __resetar_senha(self) -> tuple["Usuario", str]:
        nova_senha: str = hasher.string_random(20)
        return self.__redefinir_senha(nova_senha), nova_senha

    def __alterar_nivel_de_acesso(self, novo_nivel_acesso: NivelAcesso) -> "Usuario":
        return replace(self, nivel_acesso = novo_nivel_acesso).__salvar()

    #def __excluir(self) -> Self:
    #    UsuarioDAO.instance().deletar_por_pk(self.__pk)
    #    return self

    # Exportado para a classe Segredo.
    @property
    def is_admin(self) -> bool:
        return self.nivel_acesso == NivelAcesso.CHAVEIRO_DEUS_SUPREMO

    @property
    def __is_permitido(self) -> bool:
        return self.nivel_acesso != NivelAcesso.DESATIVADO

    def __permitir_admin(self) -> Self:
        if not self.is_admin: raise PermissaoNegadaException()
        return self

    def __permitir_acesso(self) -> Self:
        if not self.__is_permitido: raise PermissaoNegadaException()
        return self

    def __salvar(self) -> Self:
        UsuarioDAO.instance().salvar_com_pk(self.__down)
        return self

    @property
    def __chave(self) -> ChaveUsuario:
        return ChaveUsuario(self.pk_usuario)

    # Exportado para a classe Segredo.
    @property
    def pk(self) -> UsuarioPK:
        return UsuarioPK(self.pk_usuario)

    @property
    def __up(self) -> UsuarioComChave:
        return UsuarioComChave(self.__chave, self.login, self.nivel_acesso)

    @property
    def __down(self) -> DadosUsuario:
        return DadosUsuario(self.pk_usuario, self.login, self.nivel_acesso.value, self.hash_com_sal)

    # Métodos estáticos de fábrica.

    @staticmethod
    def servicos() -> "Usuario.Servico":
        return Usuario.Servico.instance()

    @staticmethod
    def __promote(dados: DadosUsuario) -> "Usuario":
        return Usuario(dados.pk_usuario, dados.login, NivelAcesso(dados.fk_nivel_acesso), dados.hash_com_sal)

    @staticmethod
    def __encontrar_por_chave(chave: ChaveUsuario) -> "Usuario | None":
        dados: DadosUsuario | None = UsuarioDAO.instance().buscar_por_pk(UsuarioPK(chave.valor))
        if dados is None: return None
        return Usuario.__promote(dados)

    @staticmethod
    def __encontrar_existente_por_chave(chave: ChaveUsuario) -> "Usuario":
        encontrado: Usuario | None = Usuario.__encontrar_por_chave(chave)
        if encontrado is None: raise UsuarioNaoExisteException()
        return encontrado

    # Exportado para a classe Segredo.
    @staticmethod
    def verificar_acesso(chave: ChaveUsuario) -> "Usuario":
        return Usuario.__encontrar_existente_por_chave(chave).__permitir_acesso()

    # Exportado para a classe Categoria.
    @staticmethod
    def verificar_acesso_admin(chave: ChaveUsuario) -> "Usuario":
        return Usuario.__encontrar_existente_por_chave(chave).__permitir_admin()

    @staticmethod
    def __encontrar_por_login(login: str) -> "Usuario | None":
        dados: DadosUsuario | None = UsuarioDAO.instance().buscar_por_login(LoginUsuarioDAO(login))
        if dados is None: return None
        return Usuario.__promote(dados)

    @staticmethod
    def __encontrar_existente_por_login(login: str) -> "Usuario":
        encontrado: Usuario | None = Usuario.__encontrar_por_login(login)
        if encontrado is None: raise UsuarioNaoExisteException()
        return encontrado

    @staticmethod
    def __nao_existente_por_login(login: str) -> None:
        talvez: Usuario | None = Usuario.__encontrar_por_login(login)
        if talvez is not None: raise UsuarioJaExisteException()

    @staticmethod
    def __listar() -> list["Usuario"]:
        return [Usuario.__promote(u) for u in UsuarioDAO.instance().listar()]

    @staticmethod
    def __mapear_todos(dados: list[DadosUsuario]) -> dict[str, Usuario]:
        return {u.login: Usuario.__promote(u) for u in dados}

    # Exportado para a classe Segredo.
    @staticmethod
    def listar_por_logins(logins: set[str]) -> dict[str, "Usuario"]:
        dl: list[LoginUsuarioDAO] = LoginUsuarioDAO.para_todos(logins)
        dados: list[DadosUsuario] = UsuarioDAO.instance().listar_por_logins(dl)
        r: dict[str, Usuario] = Usuario.__mapear_todos(dados)

        if len(r) != len(logins):
            for login in logins:
                if login not in r:
                    raise UsuarioNaoExisteException(login)

        return r

    # Exportado para a classe Segredo.
    @staticmethod
    def listar_por_permissao(segredo: "Segredo.Cabecalho") -> dict[str, "Permissao"]:
        lista1: list[DadosUsuarioComPermissao] = UsuarioDAO.instance().listar_por_permissao(segredo.pk)
        lista2: list[Permissao] = [Permissao(Usuario.__promote(dados.sem_permissoes), TipoPermissao(dados.fk_tipo_permissao)) for dados in lista1]
        return {permissao.usuario.login: permissao for permissao in lista2}

    class Servico:

        __me: "Usuario.Servico | None" = None

        def __init__(self) -> None:
            if Usuario.Servico.__me: raise Exception()

        @staticmethod
        def instance() -> "Usuario.Servico":
            if not Usuario.Servico.__me:
                Usuario.Servico.__me = Usuario.Servico()
            return Usuario.Servico.__me

        def trocar_senha_por_chave(self, quem_faz: ChaveUsuario, dados: TrocaSenha) -> None:
            Usuario.verificar_acesso(quem_faz).__trocar_senha(dados)

        def alterar_nivel_por_login(self, quem_faz: ChaveUsuario, dados: UsuarioComNivel) -> None:
            Usuario.verificar_acesso_admin(quem_faz)
            Usuario.__encontrar_existente_por_login(dados.login).__alterar_nivel_de_acesso(dados.nivel_acesso)

        def login(self, quem_faz: LoginComSenha) -> UsuarioComChave:
            dados: DadosUsuario | None = UsuarioDAO.instance().buscar_por_login(LoginUsuarioDAO(quem_faz.login))
            if dados is None: raise SenhaErradaException()
            cadastrado: Usuario = Usuario.__promote(dados)
            cadastrado.__validar_senha(quem_faz.senha)
            return cadastrado.__permitir_acesso().__up

        def buscar_por_chave(self, quem_faz: ChaveUsuario, chave: ChaveUsuario) -> UsuarioComChave:
            Usuario.verificar_acesso(quem_faz)
            return Usuario.__encontrar_existente_por_chave(chave).__up

        def resetar_senha_por_login(self, quem_faz: ChaveUsuario, dados: ResetLoginUsuario) -> SenhaAlterada:
            Usuario.verificar_acesso_admin(quem_faz)
            t: tuple[Usuario, str] = Usuario.__encontrar_existente_por_login(dados.login).__resetar_senha()
            return SenhaAlterada(t[0].__chave, t[0].login, t[1])

        def buscar_por_login(self, quem_faz: ChaveUsuario, dados: LoginUsuario) -> UsuarioComChave:
            Usuario.verificar_acesso(quem_faz)
            return Usuario.__encontrar_existente_por_login(dados.login).__up

        def criar_admin(self, dados: LoginComSenha) -> UsuarioComChave:
            return self.__criar_interno(dados.com_nivel(NivelAcesso.CHAVEIRO_DEUS_SUPREMO))

        def criar(self, quem_faz: ChaveUsuario, dados: UsuarioNovo) -> UsuarioComChave:
            Usuario.verificar_acesso_admin(quem_faz)
            return self.__criar_interno(dados)

        def __criar_interno(self, dados: UsuarioNovo) -> UsuarioComChave:
            Usuario.__nao_existente_por_login(dados.login)
            hash_com_sal: str = hasher.criar_hash(dados.senha)
            pk: UsuarioPK = UsuarioDAO.instance().criar(DadosUsuarioSemPK(dados.login, dados.nivel_acesso.value, hash_com_sal))
            return Usuario(pk.pk_usuario, dados.login, dados.nivel_acesso, hash_com_sal).__up

        def listar(self, quem_faz: ChaveUsuario) -> ResultadoListaDeUsuarios:
            Usuario.verificar_acesso_admin(quem_faz)
            return ResultadoListaDeUsuarios([x.__up for x in Usuario.__listar()])