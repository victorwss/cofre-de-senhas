# Cofre de senhas

from enum import Enum
from dataclasses import dataclass
from validator import dataclass_validate
from validator import TypeValidationError

class NivelAcesso(Enum):
    BANIDO = 0,
    NORMAL = 1,
    CHAVEIRO_DEUS_SUPREMO = 2

    @staticmethod
    def por_codigo(codigo: int) -> NivelAcesso:
        for n in NivelAcesso:
            if n.value == codigo: return n
        raise IndexError(f"O código {codigo} não existe em NivelAcesso.")

class TipoPermissao(Enum):
    SOMENTE_LEITURA = 1,
    LEITURA_E_ESCRITA = 2,
    PROPRIETARIO = 3

    @staticmethod
    def por_codigo(codigo: int) -> TipoPermissao:
        for n in TipoPermissao:
            if n.value == codigo: return n
        raise IndexError(f"O código {codigo} não existe em TipoPermissao.")

class TipoSegredo(Enum):
    PUBLICO = 1,
    ENCONTRAVEL = 2,
    CONFIDENCIAL = 3

    @staticmethod
    def por_codigo(codigo: int) -> TipoSegredo:
        for n in TipoSegredo:
            if n.value == codigo: return n
        raise IndexError(f"O código {codigo} não existe em TipoSegredo.")

@dataclass_validate
@dataclass(frozen = True)
class SegredoChave:
    valor: int

@dataclass_validate
@dataclass(frozen = True)
class CampoSegredoChave:
    valor: int

@dataclass_validate
@dataclass(frozen = True)
class UsuarioChave:
    valor: int

@dataclass_validate
@dataclass(frozen = True)
class CategoriaChave:
    valor: int

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
class NovaSenha:
    senha: str

@dataclass_validate
@dataclass(frozen = True)
class ResetLoginUsuario:
    login: str

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

    def sem_chave(self, chave: SegredoChave) -> "SegredoSemChave":
        return SegredoSemChave(self.nome, self.descricao, self.tipo, self.campos, self.categorias, self.usuarios)

@dataclass_validate
@dataclass(frozen = True)
class CabecalhoSegredoComChave:
    chave: SegredoChave
    nome: str
    descricao: str
    tipo: TipoSegredo

@dataclass_validate
@dataclass(frozen = True)
class PesquisaSegredos:
    nome: str
    categorias: list[str]

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
class CategoriaComChave:
    chave: CategoriaChave
    nome: str

@dataclass_validate
@dataclass(frozen = True)
class ResultadoPesquisaDeSegredos:
    segredos: list[CabecalhoSegredoComChave]

@dataclass_validate
@dataclass(frozen = True)
class ResultadoListaDeUsuarios:
    lista: list[UsuarioComChave]

@dataclass_validate
@dataclass(frozen = True)
class ResultadoListaDeCategorias:
    lista: list[CategoriaComChave]

@dataclass_validate
@dataclass(frozen = True)
class VerificacaoSegredo:
    login: str
    chave: SegredoChave

class SenhaErradaException(Exception):
    pass

class UsuarioNaoLogadoException(Exception):
    pass

class UsuarioBanidoException(Exception):
    pass

class PermissaoNegadaException(Exception):
    pass

class UsuarioJaExisteException(Exception):
    pass

class UsuarioNaoExisteException(Exception):
    pass

class CategoriaJaExisteException(Exception):
    pass

class CategoriaNaoExisteException(Exception):
    pass

class SegredoNaoExisteException(Exception):
    pass

@dataclass_validate
@dataclass(frozen = True)
class Erro:
    mensagem: str
    tipo: str
    status: int