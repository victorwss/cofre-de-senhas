from abc import ABC, abstractmethod
from .model import *
from dataclasses import dataclass
from validator import dataclass_validate

class GerenciadorLogin(ABC):

    # Pode lançar SenhaErradaException
    @abstractmethod
    def login(self, chave: UsuarioChave) -> None:
        pass

    @abstractmethod
    def logout(self) -> None:
        pass

    # Pode lançar UsuarioNaoLogadoException.
    @abstractmethod
    @property
    def usuario_logado(self) -> UsuarioChave:
        pass

# Todos os métodos (exceto logout) podem lançar UsuarioNaoLogadoException ou UsuarioBanidoException.
class CofreDeSenhas(ABC):

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

    # Pode lançar CategoriaNaoExisteException
    @abstractmethod
    def pesquisar_segredos(self, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos:
        pass

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