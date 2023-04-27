import hashlib
from typing import Self, TypeGuard
from dataclasses import dataclass, replace
from .bd import cf
from .cofre_enum import *
from .dao import *
from .dao_impl import *
from .service import *

udao = UsuarioDAOImpl(cf)

@dataclass(frozen = True)
class SenhaAlterada:
    usuario: "Usuario"
    nova_senha: str

@dataclass(frozen = True)
class Usuario:
    pk_usuario: int
    login: str
    nivel_acesso: NivelAcesso
    hash_com_sal: str

    def trocar_senha(self, nova_senha: str) -> Usuario:
        return replace(self, hash_com_sal = Usuario.__criar_hash(nova_senha)).__salvar()

    def resetar_senha(self) -> SenhaAlterada:
        nova_senha: str = Usuario.__string_random()
        return SenhaAlterada(self.trocar_senha(nova_senha), nova_senha)

    def alterar_nivel_de_acesso(self, novo_nivel_acesso: NivelAcesso) -> Usuario:
        return replace(self, nivel_acesso = novo_nivel_acesso).__salvar()

    def excluir(self) -> Self:
        udao.deletar_por_pk(self.pk)
        return self

    @property
    def is_admin(self) -> bool:
        return self.nivel_acesso == NivelAcesso.CHAVEIRO_DEUS_SUPREMO

    @property
    def is_permitido(self) -> bool:
        return self.nivel_acesso != NivelAcesso.BANIDO

    def permitir_admin(self) -> Self:
        if not self.is_admin: raise PermissaoNegadaException()
        return self

    def permitir_acesso(self) -> Self:
        if not self.is_permitido: raise PermissaoNegadaException()
        return self

    def __salvar(self) -> Self:
        udao.salvar(self.__down)
        return self

    @property
    def chave(self) -> UsuarioChave:
        return UsuarioChave(self.pk_usuario)

    @property
    def pk(self) -> UsuarioPK:
        return UsuarioPK(self.pk_usuario)

    @property
    def up(self) -> UsuarioComChave:
        return UsuarioComChave(self.chave, self.login, self.nivel_acesso)

    @property
    def __down(self) -> DadosUsuario:
        return DadosUsuario(self.pk_usuario, self.login, self.nivel_acesso.value, self.hash_com_sal)

    @staticmethod
    def __promote(dados: DadosUsuario) -> Usuario:
        return Usuario(dados.pk_usuario, dados.login, NivelAcesso.por_codigo(dados.fk_nivel_acesso), dados.hash_com_sal)

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

    @staticmethod
    def fazer_login(quem_faz: LoginUsuario) -> Usuario:
        dados: DadosUsuario | None = udao.buscar_por_login(quem_faz.login)
        if dados is None: raise SenhaErradaException()
        cadastrado: Usuario = Usuario.__promote(dados)
        if not cadastrado.__comparar_hash(quem_faz.senha): raise SenhaErradaException()
        return cadastrado.permitir_acesso()

    @staticmethod
    def encontrar_por_chave(chave: UsuarioChave) -> Usuario | None:
        dados: DadosUsuario | None = udao.buscar_por_pk(UsuarioPK(chave.valor))
        if dados is None: return None
        return Usuario.__promote(dados)

    @staticmethod
    def encontrar_existente_por_chave(chave: UsuarioChave) -> Usuario:
        encontrado: Usuario | None = Usuario.encontrar_por_chave(chave)
        if encontrado is None: raise UsuarioNaoExisteException()
        return encontrado

    @staticmethod
    def encontrar_por_login(login: str) -> Usuario | None:
        dados: DadosUsuario | None = udao.buscar_por_login(login)
        if dados is None: return None
        return Usuario.__promote(dados)

    @staticmethod
    def encontrar_existente_por_login(login: str) -> Usuario:
        encontrado: Usuario | None = Usuario.encontrar_por_login(login)
        if encontrado is None: raise UsuarioNaoExisteException()
        return encontrado

    @staticmethod
    def nao_existente_por_login(login: str) -> None:
        talvez: Usuario | None = Usuario.encontrar_por_login(login)
        if talvez is not None: raise UsuarioJaExisteException()

    @staticmethod
    def criar(login: str, nivel: NivelAcesso, senha: str) -> Usuario:
        Usuario.nao_existente_por_login(login)
        hash_com_sal: str = Usuario.__criar_hash(senha)
        pk: UsuarioPK = udao.criar(DadosUsuarioSemPK(login, nivel.value, hash_com_sal))
        return Usuario(pk.pk_usuario, login, nivel, hash_com_sal)

    @staticmethod
    def listar() -> list[Usuario]:
        return [Usuario.__promote(u) for u in udao.listar()]

    @staticmethod
    def listar_por_login(logins: set[str]) -> dict[str, Usuario]:
        def filtragem(p: str) -> TypeGuard[tuple[str, Usuario]]:
            return p in logins
        usuarios: dict[str, Usuario] = {usuario.login: usuario for usuario in Usuario.listar()}
        return dict(filter(filtragem, usuarios))