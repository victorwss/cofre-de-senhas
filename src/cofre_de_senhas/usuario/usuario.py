import hasher
from typing import Self, TypeAlias
from validator import dataclass_validate
from dataclasses import dataclass, replace
from ..erro import (
    SenhaErradaException, UsuarioBanidoException, LoginExpiradoException, PermissaoNegadaException,
    UsuarioNaoExisteException, UsuarioJaExisteException,
)
from ..dao import UsuarioDAO, UsuarioPK, DadosUsuario, DadosUsuarioComPermissao, DadosUsuarioSemPK, LoginUsuarioUK
from ..service import (
    TipoPermissao,
    UsuarioComChave, ChaveUsuario, NivelAcesso, UsuarioComNivel,
    UsuarioNovo, LoginComSenha, LoginUsuario, TrocaSenha, SenhaAlterada, ResetLoginUsuario, ResultadoListaDeUsuarios,
)
from typing import TYPE_CHECKING


if TYPE_CHECKING:  # pragma: no cover
    from cofre_de_senhas.segredo.segredo import Segredo


_UBE: TypeAlias = UsuarioBanidoException
_PNE: TypeAlias = PermissaoNegadaException
_UNEE: TypeAlias = UsuarioNaoExisteException
_UJEE: TypeAlias = UsuarioJaExisteException
_SEE: TypeAlias = SenhaErradaException
_LEE: TypeAlias = LoginExpiradoException


@dataclass_validate
@dataclass(frozen = True)
class Usuario:
    pk_usuario: int
    login: str
    nivel_acesso: NivelAcesso
    hash_com_sal: str

    # Propriedades e métodos de instância.

    def __validar_senha(self, senha: str) -> bool:
        return hasher.comparar_hash(self.hash_com_sal, senha)

    def __redefinir_senha(self, nova_senha: str) -> "Usuario":
        return replace(self, hash_com_sal = hasher.criar_hash(nova_senha)).__salvar()

    def __trocar_senha(self, dados: TrocaSenha) -> "Usuario | _SEE":
        if not self.__validar_senha(dados.antiga):
            return SenhaErradaException()
        return self.__redefinir_senha(dados.nova)

    def __resetar_senha(self) -> tuple["Usuario", str]:
        nova_senha: str = hasher.string_random(20)
        return self.__redefinir_senha(nova_senha), nova_senha

    def __alterar_nivel_de_acesso(self, novo_nivel_acesso: NivelAcesso) -> "Usuario":
        return replace(self, nivel_acesso = novo_nivel_acesso).__salvar()

    # def __excluir(self) -> Self:
    #     UsuarioDAO.instance().deletar_por_pk(self.__pk)
    #     return self

    # Exportado para a classe Segredo.
    @property
    def is_admin(self) -> bool:
        return self.nivel_acesso == NivelAcesso.CHAVEIRO_DEUS_SUPREMO

    @property
    def __is_banido(self) -> bool:
        return self.nivel_acesso == NivelAcesso.DESATIVADO

    def __permitir_admin(self) -> Self | _UBE | _PNE:
        if self.__is_banido:
            return UsuarioBanidoException()
        if not self.is_admin:
            return PermissaoNegadaException()
        return self

    def __permitir_acesso(self) -> Self | _UBE:
        if self.__is_banido:
            return UsuarioBanidoException()
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
    def _up(self) -> UsuarioComChave:
        return UsuarioComChave(self.__chave, self.login, self.nivel_acesso)

    @property
    def __down(self) -> DadosUsuario:
        return DadosUsuario(self.pk_usuario, self.login, self.nivel_acesso.value, self.hash_com_sal)

    # Métodos estáticos de fábrica.

    @staticmethod
    def __promote(dados: DadosUsuario) -> "Usuario":
        return Usuario(dados.pk_usuario, dados.login, NivelAcesso(dados.fk_nivel_acesso), dados.hash_com_sal)

    @staticmethod
    def __encontrar_por_chave(chave: ChaveUsuario) -> "Usuario | None":
        dados: DadosUsuario | None = UsuarioDAO.instance().buscar_por_pk(UsuarioPK(chave.valor))
        if dados is None:
            return None
        return Usuario.__promote(dados)

    @staticmethod
    def __encontrar_existente_por_chave(chave: ChaveUsuario) -> "Usuario | _UNEE":
        encontrado: Usuario | None = Usuario.__encontrar_por_chave(chave)
        if encontrado is None:
            return UsuarioNaoExisteException()
        return encontrado

    # Exportado para a classe Segredo.
    @staticmethod
    def verificar_acesso(chave: ChaveUsuario) -> "Usuario | _LEE | _UBE":
        x: Usuario | _UNEE = Usuario.__encontrar_existente_por_chave(chave)
        if isinstance(x, _UNEE):
            return LoginExpiradoException()
        return x.__permitir_acesso()

    # Exportado para a classe Categoria.
    @staticmethod
    def verificar_acesso_admin(chave: ChaveUsuario) -> "Usuario | _LEE | _UBE | _PNE":
        x: Usuario | _UNEE = Usuario.__encontrar_existente_por_chave(chave)
        if isinstance(x, _UNEE):
            return LoginExpiradoException()
        return x.__permitir_admin()

    @staticmethod
    def __encontrar_por_login(login: str) -> "Usuario | None":
        dados: DadosUsuario | None = UsuarioDAO.instance().buscar_por_login(LoginUsuarioUK(login))
        if dados is None:
            return None
        return Usuario.__promote(dados)

    @staticmethod
    def __encontrar_existente_por_login(login: str) -> "Usuario | _UNEE":
        encontrado: Usuario | None = Usuario.__encontrar_por_login(login)
        if encontrado is None:
            return UsuarioNaoExisteException()
        return encontrado

    @staticmethod
    def __nao_existente_por_login(login: str) -> None | _UJEE:
        talvez: Usuario | None = Usuario.__encontrar_por_login(login)
        if talvez is not None:
            return UsuarioJaExisteException()
        return None

    @staticmethod
    def __listar_interno() -> list["Usuario"]:
        return [Usuario.__promote(u) for u in UsuarioDAO.instance().listar()]

    @staticmethod
    def __mapear_todos(dados: list[DadosUsuario]) -> dict[str, "Usuario"]:
        return {u.login: Usuario.__promote(u) for u in dados}

    @staticmethod
    def __criar_interno(dados: UsuarioNovo) -> UsuarioComChave | _UJEE:
        u1: None | _UJEE = Usuario.__nao_existente_por_login(dados.login)
        if u1 is not None:
            return u1
        hash_com_sal: str = hasher.criar_hash(dados.senha)
        pk: UsuarioPK = UsuarioDAO.instance().criar(DadosUsuarioSemPK(dados.login, dados.nivel_acesso.value, hash_com_sal))
        return Usuario(pk.pk_usuario, dados.login, dados.nivel_acesso, hash_com_sal)._up

    # Exportado para a classe Segredo.
    @staticmethod
    def listar_por_logins(logins: set[str]) -> dict[str, "Usuario"] | _UNEE:
        dl: list[LoginUsuarioUK] = LoginUsuarioUK.para_todos(logins)
        dados: list[DadosUsuario] = UsuarioDAO.instance().listar_por_logins(dl)
        r: dict[str, Usuario] = Usuario.__mapear_todos(dados)

        if len(r) != len(logins):
            for login in logins:
                if login not in r:
                    return UsuarioNaoExisteException(login)

        return r

    # Exportado para a classe Segredo.
    @staticmethod
    def listar_por_permissao(segredo: "Segredo.Cabecalho") -> dict[str, "Permissao"]:
        lista1: list[DadosUsuarioComPermissao] = UsuarioDAO.instance().listar_por_permissao(segredo.pk)
        lista2: list[Permissao] = [Permissao(Usuario.__promote(dados.sem_permissoes), TipoPermissao(dados.fk_tipo_permissao)) for dados in lista1]
        return {permissao.usuario.login: permissao for permissao in lista2}

    @staticmethod
    def _trocar_senha_por_chave(quem_faz: ChaveUsuario, dados: TrocaSenha) -> None | _LEE | _UBE | _SEE:
        u1: Usuario | _LEE | _UBE = Usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        u2: Usuario | _SEE = u1.__trocar_senha(dados)
        if not isinstance(u2, Usuario):
            return u2
        return None

    @staticmethod
    def _alterar_nivel_por_login(quem_faz: ChaveUsuario, dados: UsuarioComNivel) -> None | _UNEE | _UBE | _PNE | _LEE:
        u1: Usuario | _LEE | _UBE | _PNE = Usuario.verificar_acesso_admin(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        u2: Usuario | _UNEE = Usuario.__encontrar_existente_por_login(dados.login)
        if not isinstance(u2, Usuario):
            return u2
        u2.__alterar_nivel_de_acesso(dados.nivel_acesso)
        return None

    @staticmethod
    def _login(quem_faz: LoginComSenha) -> UsuarioComChave | _UBE | _SEE:
        dados: DadosUsuario | None = UsuarioDAO.instance().buscar_por_login(LoginUsuarioUK(quem_faz.login))
        if dados is None:
            return SenhaErradaException()
        cadastrado: Usuario = Usuario.__promote(dados)
        if cadastrado.__is_banido:
            return UsuarioBanidoException()
        if not cadastrado.__validar_senha(quem_faz.senha):
            return SenhaErradaException()
        return cadastrado._up

    @staticmethod
    def _buscar_por_chave(quem_faz: ChaveUsuario, chave: ChaveUsuario) -> UsuarioComChave | _UNEE | _UBE | _LEE:
        u1: Usuario | _LEE | _UBE = Usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        u2: Usuario | _UNEE = Usuario.__encontrar_existente_por_chave(chave)
        if not isinstance(u2, Usuario):
            return u2
        return u2._up

    @staticmethod
    def _resetar_senha_por_login(quem_faz: ChaveUsuario, dados: ResetLoginUsuario) -> SenhaAlterada | _UNEE | _UBE | _PNE | _LEE:
        u1: Usuario | _LEE | _UBE | _PNE = Usuario.verificar_acesso_admin(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        u2: Usuario | _UNEE = Usuario.__encontrar_existente_por_login(dados.login)
        if not isinstance(u2, Usuario):
            return u2
        t: tuple[Usuario, str] = u2.__resetar_senha()
        return SenhaAlterada(t[0].__chave, t[0].login, t[1])

    @staticmethod
    def _buscar_por_login(quem_faz: ChaveUsuario, dados: LoginUsuario) -> UsuarioComChave | _UNEE | _UBE | _LEE:
        u1: Usuario | _LEE | _UBE = Usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        u2: Usuario | _UNEE = Usuario.__encontrar_existente_por_login(dados.login)
        if not isinstance(u2, Usuario):
            return u2
        return u2._up

    @staticmethod
    def _criar_admin(dados: LoginComSenha) -> UsuarioComChave | _UJEE:
        return Usuario.__criar_interno(dados.com_nivel(NivelAcesso.CHAVEIRO_DEUS_SUPREMO))

    @staticmethod
    def _criar(quem_faz: ChaveUsuario, dados: UsuarioNovo) -> UsuarioComChave | _LEE | _UBE | _PNE | _UJEE:
        u1: Usuario | _LEE | _UBE | _PNE = Usuario.verificar_acesso_admin(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        return Usuario.__criar_interno(dados)

    @staticmethod
    def _listar(quem_faz: ChaveUsuario) -> ResultadoListaDeUsuarios | _LEE | _UBE:
        u1: Usuario | _LEE | _UBE = Usuario.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        return ResultadoListaDeUsuarios([x._up for x in Usuario.__listar_interno()])


class Servicos:

    def __init__(self) -> None:
        raise Exception()

    @staticmethod
    def trocar_senha_por_chave(quem_faz: ChaveUsuario, dados: TrocaSenha) -> None | _LEE | _UBE | _SEE:
        return Usuario._trocar_senha_por_chave(quem_faz, dados)

    @staticmethod
    def alterar_nivel_por_login(quem_faz: ChaveUsuario, dados: UsuarioComNivel) -> None | _UNEE | _UBE | _PNE | _LEE:
        return Usuario._alterar_nivel_por_login(quem_faz, dados)

    @staticmethod
    def login(quem_faz: LoginComSenha) -> UsuarioComChave | _UBE | _SEE:
        return Usuario._login(quem_faz)

    @staticmethod
    def buscar_por_chave(quem_faz: ChaveUsuario, chave: ChaveUsuario) -> UsuarioComChave | _UNEE | _UBE | _LEE:
        return Usuario._buscar_por_chave(quem_faz, chave)

    @staticmethod
    def resetar_senha_por_login(quem_faz: ChaveUsuario, dados: ResetLoginUsuario) -> SenhaAlterada | _UNEE | _UBE | _PNE | _LEE:
        return Usuario._resetar_senha_por_login(quem_faz, dados)

    @staticmethod
    def buscar_por_login(quem_faz: ChaveUsuario, dados: LoginUsuario) -> UsuarioComChave | _UNEE | _UBE | _LEE:
        return Usuario._buscar_por_login(quem_faz, dados)

    @staticmethod
    def criar_admin(dados: LoginComSenha) -> UsuarioComChave | _UJEE:
        return Usuario._criar_admin(dados)

    @staticmethod
    def criar(quem_faz: ChaveUsuario, dados: UsuarioNovo) -> UsuarioComChave | _LEE | _UBE | _PNE | _UJEE:
        return Usuario._criar(quem_faz, dados)

    @staticmethod
    def listar(quem_faz: ChaveUsuario) -> ResultadoListaDeUsuarios | _LEE | _UBE:
        return Usuario._listar(quem_faz)


@dataclass_validate
@dataclass(frozen = True)
class Permissao:
    usuario: Usuario
    tipo: TipoPermissao
