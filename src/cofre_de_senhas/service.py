from abc import ABC
from abc import abstractmethod
from .model import *

# Todos os métodos podem lançar SenhaErradaException ou UsuarioBanidoException.
class CofreDeSenhas(ABC):

    @abstractmethod
    def login(self, quem_faz: LoginUsuario) -> NivelAcesso:
        pass

    # Pode lançar PermissaoNegadaException, UsuarioJaExisteException
    @abstractmethod
    def criar_usuario(self, quem_faz: LoginUsuario, dados: UsuarioNovo) -> None:
        pass

    @abstractmethod
    def trocar_senha(self, quem_faz: LoginUsuario, dados: NovaSenha) -> None:
        pass

    @abstractmethod
    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    def resetar_senha(self, quem_faz: LoginUsuario, dados: ResetLoginUsuario) -> str:
        pass

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @abstractmethod
    def alterar_nivel_de_acesso(self, quem_faz: LoginUsuario, dados: UsuarioComNivel) -> None:
        pass

    # Pode lançar PermissaoNegadaException, UsuarioNaoExisteException
    @abstractmethod
    def listar_usuarios(self, quem_faz: LoginUsuario) -> ResultadoListaDeUsuarios:
        pass

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException
    @abstractmethod
    def criar_segredo(self, quem_faz: LoginUsuario, dados: SegredoSemPK) -> None:
        pass

    # Pode lançar UsuarioNaoExisteException, CategoriaNaoExisteException, SegredoNaoExisteException
    @abstractmethod
    def alterar_segredo(self, quem_faz: LoginUsuario, dados: SegredoComPK) -> None:
        pass

    # Pode lançar SegredoNaoExisteException
    @abstractmethod
    def excluir_segredo(self, quem_faz: LoginUsuario, dados: SegredoPK) -> None:
        pass

    @abstractmethod
    def listar_segredos(self, quem_faz: LoginUsuario) -> ResultadoPesquisaDeSegredos:
        pass

    # Pode lançar SegredoNaoExisteException
    @abstractmethod
    def buscar_segredo(self, quem_faz: LoginUsuario, pk: SegredoPK) -> SegredoComPK:
        pass

    # Pode lançar CategoriaNaoExisteException
    @abstractmethod
    def pesquisar_segredos(self, quem_faz: LoginUsuario, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos:
        pass

    # Pode lançar CategoriaJaExisteException
    @abstractmethod
    def criar_categoria(self, quem_faz: LoginUsuario, dados: NomeCategoria) -> None:
        pass

    # Pode lançar CategoriaJaExisteException, CategoriaNaoExisteException
    @abstractmethod
    def renomear_categoria(self, quem_faz: LoginUsuario, dados: RenomeCategoria) -> None:
        pass

    # Pode lançar CategoriaNaoExisteException
    @abstractmethod
    def excluir_categoria(self, quem_faz: LoginUsuario, dados: NomeCategoria) -> None:
        pass