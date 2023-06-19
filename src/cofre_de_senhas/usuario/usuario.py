import hashlib
from typing import Self, TypeGuard
from validator import dataclass_validate
from dataclasses import dataclass, replace
from cofre_de_senhas.bd.raiz import cf
from cofre_de_senhas.erro import *
from cofre_de_senhas.cofre_enum import NivelAcesso, TipoPermissao
from cofre_de_senhas.dao import *
from cofre_de_senhas.service import *
from cofre_de_senhas.usuario.usuario_dao_impl import UsuarioDAOImpl

dao = UsuarioDAOImpl(cf)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cofre_de_senhas.segredo.segredo import Segredo

@dataclass_validate
@dataclass(frozen = True)
class SenhaAlterada:
    usuario: "Usuario"
    nova_senha: str

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

    def __trocar_senha(self, nova_senha: str) -> "Usuario":
        return replace(self, hash_com_sal = Usuario.__criar_hash(nova_senha)).__salvar()

    def __resetar_senha(self) -> SenhaAlterada:
        nova_senha: str = Usuario.__string_random()
        return SenhaAlterada(self.__trocar_senha(nova_senha), nova_senha)

    def __alterar_nivel_de_acesso(self, novo_nivel_acesso: NivelAcesso) -> "Usuario":
        return replace(self, nivel_acesso = novo_nivel_acesso).__salvar()

    #def __excluir(self) -> Self:
    #    dao.deletar_por_pk(self.__pk)
    #    return self

    # Exportado para a classe Segredo.
    @property
    def is_admin(self) -> bool:
        return self.nivel_acesso == NivelAcesso.CHAVEIRO_DEUS_SUPREMO

    @property
    def __is_permitido(self) -> bool:
        return self.nivel_acesso != NivelAcesso.BANIDO

    def __permitir_admin(self) -> Self:
        if not self.is_admin: raise PermissaoNegadaException()
        return self

    def __permitir_acesso(self) -> Self:
        if not self.__is_permitido: raise PermissaoNegadaException()
        return self

    def __salvar(self) -> Self:
        dao.salvar(self.__down)
        return self

    @property
    def __chave(self) -> UsuarioChave:
        return UsuarioChave(self.pk_usuario)

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

    # Métodos internos.

    @staticmethod
    def __string_random() -> str:
        import random
        import string
        letters = string.ascii_letters
        return "".join(random.choice(letters) for i in range(10))

    @staticmethod
    def __criar_hash(senha: str) -> str:
        sal = Usuario.__string_random()
        return sal + hashlib.sha3_224((sal + senha).encode("utf-8")).hexdigest()

    def __comparar_hash(self, senha: str) -> bool:
        sal = self.hash_com_sal[0:10]
        return sal + hashlib.sha3_224((sal + senha).encode("utf-8")).hexdigest() == self.hash_com_sal

    # Métodos estáticos de fábrica.

    @staticmethod
    def servicos() -> Usuario.Servico:
        return Usuario.Servico.instance()

    @staticmethod
    def __promote(dados: DadosUsuario) -> "Usuario":
        return Usuario(dados.pk_usuario, dados.login, NivelAcesso.por_codigo(dados.fk_nivel_acesso), dados.hash_com_sal)

    @staticmethod
    def __encontrar_por_chave(chave: UsuarioChave) -> "Usuario | None":
        dados: DadosUsuario | None = dao.buscar_por_pk(UsuarioPK(chave.valor))
        if dados is None: return None
        return Usuario.__promote(dados)

    @staticmethod
    def __encontrar_existente_por_chave(chave: UsuarioChave) -> "Usuario":
        encontrado: Usuario | None = Usuario.__encontrar_por_chave(chave)
        if encontrado is None: raise UsuarioNaoExisteException()
        return encontrado

    # Exportado para a classe Segredo.
    @staticmethod
    def verificar_acesso(chave: UsuarioChave) -> "Usuario":
        return Usuario.__encontrar_existente_por_chave(chave).__permitir_acesso()

    # Exportado para a classe Categoria.
    @staticmethod
    def verificar_acesso_admin(chave: UsuarioChave) -> "Usuario":
        return Usuario.__encontrar_existente_por_chave(chave).__permitir_admin()

    @staticmethod
    def __encontrar_por_login(login: str) -> "Usuario | None":
        dados: DadosUsuario | None = dao.buscar_por_login(login)
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
        return [Usuario.__promote(u) for u in dao.listar()]

    # Exportado para a classe Segredo.
    @staticmethod
    def listar_por_login(logins: set[str]) -> dict[str, "Usuario"]:
        # TO DO: Implementação ruim.

        usuarios1: dict[str, Usuario] = {usuario.login: usuario for usuario in Usuario.__listar()}
        usuarios2: dict[str, Usuario] = {}

        for n in logins:
            if n not in usuarios1: raise UsuarioNaoExisteException(n)
            usuarios2[n] = usuarios1[n]

        return usuarios2

    # Exportado para a classe Segredo.
    @staticmethod
    def listar_por_permissao(segredo: "Segredo.Cabecalho") -> dict[str, "Permissao"]:
        lista1: list[DadosUsuarioComPermissao] = dao.listar_por_permissao(segredo.pk)
        lista2: list[Permissao] = [Permissao(Usuario.__promote(dados.sem_permissoes), TipoPermissao.por_codigo(dados.fk_tipo_permissao)) for dados in lista1]
        return {permissao.usuario.login: permissao for permissao in lista2}

    class Servico:

        __me: "Usuario.Servico" = Usuario.Servico()

        def __init__(self) -> None:
            if Usuario.Servico.__me: raise Exception()

        @staticmethod
        def instance() -> "Usuario.Servico":
            return Usuario.Servico.__me

        def redefinir_senha(self, quem_faz: UsuarioChave, dados: NovaSenha) -> None:
            Usuario.verificar_acesso(quem_faz).__trocar_senha(dados.senha)

        def alterar_nivel(self, quem_faz: UsuarioChave, dados: UsuarioComNivel) -> None:
            Usuario.verificar_acesso_admin(quem_faz)
            Usuario.__encontrar_existente_por_login(dados.login).__alterar_nivel_de_acesso(dados.nivel_acesso)

        def fazer_login(self, quem_faz: LoginComSenha) -> UsuarioChave:
            dados: DadosUsuario | None = dao.buscar_por_login(quem_faz.login)
            if dados is None: raise SenhaErradaException()
            cadastrado: Usuario = Usuario.__promote(dados)
            if not cadastrado.__comparar_hash(quem_faz.senha): raise SenhaErradaException()
            return cadastrado.__permitir_acesso().__chave

        def buscar_existente_por_chave(self, quem_faz: UsuarioChave, chave: UsuarioChave) -> UsuarioComChave:
            Usuario.verificar_acesso(quem_faz)
            return Usuario.__encontrar_existente_por_chave(chave).__up

        def resetar_senha_por_login(self, quem_faz: UsuarioChave, dados: ResetLoginUsuario) -> str:
            Usuario.verificar_acesso_admin(quem_faz)
            return Usuario.__encontrar_existente_por_login(dados.login).__resetar_senha().nova_senha

        def buscar_por_login(self, quem_faz: UsuarioChave, login: str) -> UsuarioComChave:
            Usuario.verificar_acesso(quem_faz)
            return Usuario.__encontrar_existente_por_login(login).__up

        def criar_admin(self, dados: LoginComSenha) -> UsuarioComChave:
            return self.__criar_interno(dados.com_nivel(NivelAcesso.CHAVEIRO_DEUS_SUPREMO))

        def criar(self, quem_faz: UsuarioChave, dados: UsuarioNovo) -> UsuarioComChave:
            Usuario.verificar_acesso_admin(quem_faz)
            return self.__criar_interno(dados)

        def __criar_interno(self, dados: UsuarioNovo) -> UsuarioComChave:
            Usuario.__nao_existente_por_login(dados.login)
            hash_com_sal: str = Usuario.__criar_hash(dados.senha)
            pk: UsuarioPK = dao.criar(DadosUsuarioSemPK(dados.login, dados.nivel_acesso.value, hash_com_sal))
            return Usuario(pk.pk_usuario, dados.login, dados.nivel_acesso, hash_com_sal).__up

        def listar_todos(self, quem_faz: UsuarioChave) -> ResultadoListaDeUsuarios:
            Usuario.verificar_acesso_admin(quem_faz)
            return ResultadoListaDeUsuarios([x.__up for x in Usuario.__listar()])