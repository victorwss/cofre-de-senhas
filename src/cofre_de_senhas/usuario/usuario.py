import hasher
from typing import Self, TypeAlias
from validator import dataclass_validate
from dataclasses import dataclass, replace
from ..erro import (
    SenhaErradaException, UsuarioBanidoException, LoginExpiradoException, PermissaoNegadaException,
    UsuarioNaoExisteException, UsuarioJaExisteException,
    ValorIncorretoException
)
from ..dao import UsuarioDAO, UsuarioPK, DadosUsuario, DadosUsuarioComPermissao, DadosUsuarioSemPK, LoginUsuarioUK
from ..service import (
    TipoPermissao,
    UsuarioComChave, ChaveUsuario, NivelAcesso, UsuarioComNivel,
    UsuarioNovo, RenomeUsuario, LoginComSenha, LoginUsuario, TrocaSenha, SenhaAlterada, ResetLoginUsuario, ResultadoListaDeUsuarios
)
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from cofre_de_senhas.segredo.segredo import Segredo


_UBE: TypeAlias = UsuarioBanidoException
_PNE: TypeAlias = PermissaoNegadaException
_UNEE: TypeAlias = UsuarioNaoExisteException
_UJEE: TypeAlias = UsuarioJaExisteException
_SEE: TypeAlias = SenhaErradaException
_LEE: TypeAlias = LoginExpiradoException
_VIE: TypeAlias = ValorIncorretoException


@dataclass_validate
@dataclass(frozen = True)
class Usuario:
    pk_usuario: int
    login: str
    nivel_acesso: NivelAcesso
    hash_com_sal: str

    # Propriedades e métodos de instância.

    def _validar_senha(self, senha: str) -> bool:
        return hasher.comparar_hash(self.hash_com_sal, senha)

    # Exportado para a classe Segredo.
    @property
    def is_admin(self) -> bool:
        return self.nivel_acesso == NivelAcesso.CHAVEIRO_DEUS_SUPREMO

    @property
    def _is_banido(self) -> bool:
        return self.nivel_acesso == NivelAcesso.DESATIVADO

    def _permitir_admin(self) -> Self | _UBE | _PNE:
        if self._is_banido:
            return UsuarioBanidoException()
        if not self.is_admin:
            return PermissaoNegadaException()
        return self

    def _permitir_acesso(self) -> Self | _UBE:
        if self._is_banido:
            return UsuarioBanidoException()
        return self

    @property
    def _chave(self) -> ChaveUsuario:
        return ChaveUsuario(self.pk_usuario)

    # Exportado para a classe Segredo.
    @property
    def pk(self) -> UsuarioPK:
        return UsuarioPK(self.pk_usuario)

    @property
    def _up(self) -> UsuarioComChave:
        return UsuarioComChave(self._chave, self.login, self.nivel_acesso)

    @property
    def _down(self) -> DadosUsuario:
        return DadosUsuario(self.pk_usuario, self.login, self.nivel_acesso.value, self.hash_com_sal)

    # Métodos estáticos de fábrica.

    @staticmethod
    def _promote(dados: DadosUsuario) -> "Usuario":
        return Usuario(dados.pk_usuario, dados.login, NivelAcesso(dados.fk_nivel_acesso), dados.hash_com_sal)

    @staticmethod
    def _mapear_todos(dados: list[DadosUsuario]) -> dict[str, "Usuario"]:
        return {u.login: Usuario._promote(u) for u in dados}


@dataclass_validate
@dataclass(frozen = True)
class Permissao:
    usuario: Usuario
    tipo: TipoPermissao


class ServicosImpl:

    def __init__(self, dao: UsuarioDAO) -> None:
        self.__dao: UsuarioDAO = dao

    def __redefinir_senha(self, u1: Usuario, nova_senha: str) -> Usuario:
        return self.__salvar(replace(u1, hash_com_sal = hasher.criar_hash(nova_senha)))

    def __renomear(self, u1: Usuario, novo_login: str) -> Usuario:
        return self.__salvar(replace(u1, login = novo_login))

    def __trocar_senha(self, u1: Usuario, dados: TrocaSenha) -> Usuario | _SEE:
        if not u1._validar_senha(dados.antiga):
            return SenhaErradaException()
        return self.__redefinir_senha(u1, dados.nova)

    def __resetar_senha(self, u1: Usuario) -> tuple[Usuario, str]:
        nova_senha: str = hasher.string_random(20)
        return self.__redefinir_senha(u1, nova_senha), nova_senha

    def __alterar_nivel_de_acesso(self, u1: Usuario, novo_nivel_acesso: NivelAcesso) -> Usuario:
        return self.__salvar(replace(u1, nivel_acesso = novo_nivel_acesso))

    # def __excluir(self, u1: Usuario) -> Usuario:
    #     self.__dao.deletar_por_pk(u1.pk)
    #     return u1

    def __salvar(self, u1: Usuario) -> Usuario:
        self.__dao.salvar_com_pk(u1._down)
        return u1

    def __encontrar_por_chave(self, chave: ChaveUsuario) -> Usuario | None:
        dados: DadosUsuario | None = self.__dao.buscar_por_pk(UsuarioPK(chave.valor))
        if dados is None:
            return None
        return Usuario._promote(dados)

    def __encontrar_existente_por_chave(self, chave: ChaveUsuario) -> Usuario | _UNEE:
        encontrado: Usuario | None = self.__encontrar_por_chave(chave)
        if encontrado is None:
            return UsuarioNaoExisteException()
        return encontrado

    # Exportado para a classe Segredo.
    def verificar_acesso(self, chave: ChaveUsuario) -> Usuario | _LEE | _UBE:
        x: Usuario | _UNEE = self.__encontrar_existente_por_chave(chave)
        if isinstance(x, _UNEE):
            return LoginExpiradoException()
        return x._permitir_acesso()

    # Exportado para a classe Categoria.
    def verificar_acesso_admin(self, chave: ChaveUsuario) -> Usuario | _LEE | _UBE | _PNE:
        x: Usuario | _UNEE = self.__encontrar_existente_por_chave(chave)
        if isinstance(x, _UNEE):
            return LoginExpiradoException()
        return x._permitir_admin()

    def __encontrar_por_login(self, login: str) -> Usuario | None:
        dados: DadosUsuario | None = self.__dao.buscar_por_login(LoginUsuarioUK(login))
        if dados is None:
            return None
        return Usuario._promote(dados)

    def __encontrar_existente_por_login(self, login: str) -> Usuario | _UNEE:
        encontrado: Usuario | None = self.__encontrar_por_login(login)
        if encontrado is None:
            return UsuarioNaoExisteException()
        return encontrado

    def __nao_existente_por_login(self, login: str) -> None | _UJEE:
        talvez: Usuario | None = self.__encontrar_por_login(login)
        if talvez is not None:
            return UsuarioJaExisteException()
        return None

    def __listar_interno(self) -> list[Usuario]:
        return [Usuario._promote(u) for u in self.__dao.listar()]

    def __criar_interno(self, dados: UsuarioNovo) -> UsuarioComChave | _UJEE | _VIE:
        u1: None | _UJEE = self.__nao_existente_por_login(dados.login)
        if u1 is not None:
            return u1
        login: str = dados.login
        t: int = len(login)
        if not (4 <= t <= 50):
            return ValorIncorretoException()
        hash_com_sal: str = hasher.criar_hash(dados.senha)
        pk: UsuarioPK = self.__dao.criar(DadosUsuarioSemPK(dados.login, dados.nivel_acesso.value, hash_com_sal))
        return Usuario(pk.pk_usuario, dados.login, dados.nivel_acesso, hash_com_sal)._up

    # Exportado para a classe Segredo.
    def listar_por_logins(self, logins: set[str]) -> dict[str, Usuario] | _UNEE:
        dl: list[LoginUsuarioUK] = LoginUsuarioUK.para_todos(list(logins))
        dados: list[DadosUsuario] = self.__dao.listar_por_logins(dl)
        r: dict[str, Usuario] = Usuario._mapear_todos(dados)

        if len(r) != len(logins):
            for login in logins:
                if login not in r:
                    return UsuarioNaoExisteException(login)
            assert False, "A exceção UsuarioNaoExisteException deveria ter sido lançada."

        return r

    # Exportado para a classe Segredo.
    def listar_por_permissao(self, segredo: "Segredo.Cabecalho") -> dict[str, Permissao]:
        lista1: list[DadosUsuarioComPermissao] = self.__dao.listar_por_permissao(segredo.pk)
        lista2: list[Permissao] = [Permissao(Usuario._promote(dados.sem_permissoes), TipoPermissao(dados.fk_tipo_permissao)) for dados in lista1]
        return {permissao.usuario.login: permissao for permissao in lista2}

    def __trocar_senha_por_chave(self, quem_faz: ChaveUsuario, dados: TrocaSenha) -> None | _LEE | _UBE | _SEE:
        u1: Usuario | _LEE | _UBE = self.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        u2: Usuario | _SEE = self.__trocar_senha(u1, dados)
        if not isinstance(u2, Usuario):
            return u2
        return None

    def __alterar_nivel_por_login(self, quem_faz: ChaveUsuario, dados: UsuarioComNivel) -> None | _UNEE | _UBE | _PNE | _LEE:
        u1: Usuario | _LEE | _UBE | _PNE = self.verificar_acesso_admin(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        u2: Usuario | _UNEE = self.__encontrar_existente_por_login(dados.login)
        if not isinstance(u2, Usuario):
            return u2
        self.__alterar_nivel_de_acesso(u2, dados.nivel_acesso)
        return None

    def __renomear_por_login(self, quem_faz: ChaveUsuario, dados: RenomeUsuario) -> None | _UNEE | _UJEE | _UBE | _PNE | _LEE | _VIE:
        u1: Usuario | _LEE | _UBE | _PNE = self.verificar_acesso_admin(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        u2: Usuario | _UNEE = self.__encontrar_existente_por_login(dados.antigo)
        if not isinstance(u2, Usuario):
            return u2
        t: int = len(dados.novo)
        if not (4 <= t <= 50):
            return ValorIncorretoException()
        u3: None | _UJEE = self.__nao_existente_por_login(dados.novo)
        if u3 is not None:
            return u3
        self.__renomear(u2, dados.novo)
        return None

    def __login(self, quem_faz: LoginComSenha) -> UsuarioComChave | _UBE | _SEE:
        dados: DadosUsuario | None = self.__dao.buscar_por_login(LoginUsuarioUK(quem_faz.login))
        if dados is None:
            return SenhaErradaException()
        cadastrado: Usuario = Usuario._promote(dados)
        if cadastrado._is_banido:
            return UsuarioBanidoException()
        if not cadastrado._validar_senha(quem_faz.senha):
            return SenhaErradaException()
        return cadastrado._up

    def __buscar_por_chave(self, quem_faz: ChaveUsuario, chave: ChaveUsuario) -> UsuarioComChave | _UNEE | _UBE | _LEE:
        u1: Usuario | _LEE | _UBE = self.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        u2: Usuario | _UNEE = self.__encontrar_existente_por_chave(chave)
        if not isinstance(u2, Usuario):
            return u2
        return u2._up

    def __resetar_senha_por_login(self, quem_faz: ChaveUsuario, dados: ResetLoginUsuario) -> SenhaAlterada | _UNEE | _UBE | _PNE | _LEE:
        u1: Usuario | _LEE | _UBE | _PNE = self.verificar_acesso_admin(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        u2: Usuario | _UNEE = self.__encontrar_existente_por_login(dados.login)
        if not isinstance(u2, Usuario):
            return u2
        t: tuple[Usuario, str] = self.__resetar_senha(u2)
        return SenhaAlterada(t[0]._chave, t[0].login, t[1])

    def __buscar_por_login(self, quem_faz: ChaveUsuario, dados: LoginUsuario) -> UsuarioComChave | _UNEE | _UBE | _LEE:
        u1: Usuario | _LEE | _UBE = self.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        u2: Usuario | _UNEE = self.__encontrar_existente_por_login(dados.login)
        if not isinstance(u2, Usuario):
            return u2
        return u2._up

    def __criar_admin(self, dados: LoginComSenha) -> UsuarioComChave | _UJEE | _VIE:
        return self.__criar_interno(dados.com_nivel(NivelAcesso.CHAVEIRO_DEUS_SUPREMO))

    def __criar(self, quem_faz: ChaveUsuario, dados: UsuarioNovo) -> UsuarioComChave | _LEE | _UBE | _PNE | _UJEE | _VIE:
        u1: Usuario | _LEE | _UBE | _PNE = self.verificar_acesso_admin(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        return self.__criar_interno(dados)

    def __listar(self, quem_faz: ChaveUsuario) -> ResultadoListaDeUsuarios | _LEE | _UBE:
        u1: Usuario | _LEE | _UBE = self.verificar_acesso(quem_faz)
        if not isinstance(u1, Usuario):
            return u1
        return ResultadoListaDeUsuarios([x._up for x in self.__listar_interno()])

    def trocar_senha_por_chave(self, quem_faz: ChaveUsuario, dados: TrocaSenha) -> None | _LEE | _UBE | _SEE:
        return self.__trocar_senha_por_chave(quem_faz, dados)

    def renomear(self, quem_faz: ChaveUsuario, dados: RenomeUsuario) -> None | _UNEE | _UJEE | _UBE | _PNE | _LEE | _VIE:
        return self.__renomear_por_login(quem_faz, dados)

    def alterar_nivel_por_login(self, quem_faz: ChaveUsuario, dados: UsuarioComNivel) -> None | _UNEE | _UBE | _PNE | _LEE:
        return self.__alterar_nivel_por_login(quem_faz, dados)

    def login(self, quem_faz: LoginComSenha) -> UsuarioComChave | _UBE | _SEE:
        return self.__login(quem_faz)

    def buscar_por_chave(self, quem_faz: ChaveUsuario, chave: ChaveUsuario) -> UsuarioComChave | _UNEE | _UBE | _LEE:
        return self.__buscar_por_chave(quem_faz, chave)

    def resetar_senha_por_login(self, quem_faz: ChaveUsuario, dados: ResetLoginUsuario) -> SenhaAlterada | _UNEE | _UBE | _PNE | _LEE:
        return self.__resetar_senha_por_login(quem_faz, dados)

    def buscar_por_login(self, quem_faz: ChaveUsuario, dados: LoginUsuario) -> UsuarioComChave | _UNEE | _UBE | _LEE:
        return self.__buscar_por_login(quem_faz, dados)

    def criar_admin(self, dados: LoginComSenha) -> UsuarioComChave | _UJEE | _VIE:
        return self.__criar_admin(dados)

    def criar(self, quem_faz: ChaveUsuario, dados: UsuarioNovo) -> UsuarioComChave | _LEE | _UBE | _PNE | _UJEE | _VIE:
        return self.__criar(quem_faz, dados)

    def listar(self, quem_faz: ChaveUsuario) -> ResultadoListaDeUsuarios | _LEE | _UBE:
        return self.__listar(quem_faz)
