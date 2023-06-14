from abc import ABC, abstractmethod
from dataclasses import dataclass
from validator import dataclass_validate
from cofre_de_senhas.cofre_enum import NivelAcesso, TipoPermissao, TipoSegredo
from cofre_de_senhas.erro import *

@dataclass_validate
@dataclass(frozen = True)
class UsuarioChave:
    valor: int

@dataclass_validate
@dataclass(frozen = True)
class ResetLoginUsuario:
    login: str

@dataclass_validate
@dataclass(frozen = True)
class SegredoChave:
    valor: int

@dataclass_validate
@dataclass(frozen = True)
class SegredoSemChave:
    nome: str
    descricao: str
    tipo: TipoSegredo
    campos: dict[str, str]
    categorias: set[str]
    usuarios: dict[str, TipoPermissao]

    def com_chave(self, chave: SegredoChave) -> "SegredoComChave":
        return SegredoComChave(chave, self.nome, self.descricao, self.tipo, self.campos, self.categorias, self.usuarios)

@dataclass_validate
@dataclass(frozen = True)
class SegredoComChave:
    chave: SegredoChave
    nome: str
    descricao: str
    tipo: TipoSegredo
    campos: dict[str, str]
    categorias: set[str]
    usuarios: dict[str, TipoPermissao]

#    @property
#    def sem_chave(self, chave: SegredoChave) -> "SegredoSemChave":
#        return SegredoSemChave(self.nome, self.descricao, self.tipo, self.campos, self.categorias, self.usuarios)

@dataclass_validate
@dataclass(frozen = True)
class NomeCategoria:
    nome: str

@dataclass_validate
@dataclass(frozen = True)
class RenomeCategoria:
    antigo: str
    novo: str

@dataclass_validate
@dataclass(frozen = True)
class LoginUsuario:
    login: str
    senha: str

@dataclass_validate
@dataclass(frozen = True)
class UsuarioNovo:
    login: str
    nivel_acesso: NivelAcesso
    senha: str

@dataclass_validate
@dataclass(frozen = True)
class NovaSenha:
    senha: str

@dataclass_validate
@dataclass(frozen = True)
class UsuarioComNivel:
    login: str
    nivel_acesso: NivelAcesso

@dataclass_validate
@dataclass(frozen = True)
class UsuarioComChave:
    chave: UsuarioChave
    login: str
    nivel_acesso: NivelAcesso

@dataclass_validate
@dataclass(frozen = True)
class CategoriaChave:
    valor: int

@dataclass_validate
@dataclass(frozen = True)
class CabecalhoSegredoComChave:
    chave: SegredoChave
    nome: str
    descricao: str
    tipo: TipoSegredo

@dataclass_validate
@dataclass(frozen = True)
class ResultadoPesquisaDeSegredos:
    segredos: list[CabecalhoSegredoComChave]

@dataclass_validate
@dataclass(frozen = True)
class CategoriaComChave:
    chave: CategoriaChave
    nome: str

@dataclass_validate
@dataclass(frozen = True)
class ResultadoListaDeCategorias:
    lista: list[CategoriaComChave]

@dataclass_validate
@dataclass(frozen = True)
class ResultadoListaDeUsuarios:
    lista: list[UsuarioComChave]

@dataclass_validate
@dataclass(frozen = True)
class PesquisaSegredos:
    nome: str
    categorias: list[str]

class GerenciadorLogin(ABC):

    # Pode lançar SenhaErradaException
    @abstractmethod
    def login(self, chave: UsuarioChave) -> None:
        pass

    @abstractmethod
    def logout(self) -> None:
        pass

    # Pode lançar UsuarioNaoLogadoException.
    @property
    @abstractmethod
    def usuario_logado(self) -> UsuarioChave:
        pass

class ServicoBD(ABC):

    @abstractmethod
    def criar_bd(self, dados: LoginUsuario) -> None:
        pass

# Todos os métodos (exceto logout) podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
class ServicoUsuario(ABC):

    # Pode lançar SenhaErradaException
    @abstractmethod
    def login(self, quem_faz: LoginUsuario) -> None:
        pass

    @abstractmethod
    def logout(self) -> None:
        pass

    # Pode lançar PermissaoNegadaException, UsuarioJaExisteException
    @abstractmethod
    def criar_usuario(self, dados: UsuarioNovo) -> None:
        pass

    @abstractmethod
    def trocar_senha(self, dados: NovaSenha) -> None:
        pass

    @abstractmethod
    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def resetar_senha(self, dados: ResetLoginUsuario) -> str:
        pass

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @abstractmethod
    def alterar_nivel_de_acesso(self, dados: UsuarioComNivel) -> None:
        pass

    # Pode lançar UsuarioNaoExisteException
    @abstractmethod
    def buscar_usuario_por_login(self, login: str) -> UsuarioComChave:
        pass

    # Pode lançar UsuarioNaoExisteException
    @abstractmethod
    def buscar_usuario_por_chave(self, chave: UsuarioChave) -> UsuarioComChave:
        pass

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @abstractmethod
    def listar_usuarios(self) -> ResultadoListaDeUsuarios:
        pass

class ServicoSegredo(ABC):

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    @abstractmethod
    def criar_segredo(self, dados: SegredoSemChave) -> None:
        pass

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException
    @abstractmethod
    def alterar_segredo(self, dados: SegredoComChave) -> None:
        pass

    # Pode lançar SegredoNaoExisteException
    @abstractmethod
    def excluir_segredo(self, dados: SegredoChave) -> None:
        pass

    @abstractmethod
    def listar_segredos(self) -> ResultadoPesquisaDeSegredos:
        pass

    # Pode lançar SegredoNaoExisteException
    @abstractmethod
    def buscar_segredo_por_chave(self, chave: SegredoChave) -> SegredoComChave:
        pass

    # Não implementado ainda! Pode lançar SegredoNaoExisteException
    @abstractmethod
    def pesquisar_segredos(self, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos:
        pass

class ServicoCategoria(ABC):

    # Pode lançar CategoriaNaoExisteException
    @abstractmethod
    def buscar_categoria_por_nome(self, nome: str) -> CategoriaComChave:
        pass

    # Pode lançar CategoriaNaoExisteException
    @abstractmethod
    def buscar_categoria_por_chave(self, chave: CategoriaChave) -> CategoriaComChave:
        pass

    # Pode lançar CategoriaJaExisteException
    @abstractmethod
    def criar_categoria(self, dados: NomeCategoria) -> None:
        pass

    # Pode lançar CategoriaJaExisteException, CategoriaNaoExisteException
    @abstractmethod
    def renomear_categoria(self, dados: RenomeCategoria) -> None:
        pass

    # Pode lançar CategoriaNaoExisteException
    @abstractmethod
    def excluir_categoria(self, dados: NomeCategoria) -> None:
        pass

    @abstractmethod
    def listar_categorias(self) -> ResultadoListaDeCategorias:
        pass