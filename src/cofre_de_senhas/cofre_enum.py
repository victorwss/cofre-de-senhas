# Cofre de senhas

from enum import Enum

class NivelAcesso(Enum):
    BANIDO = 0
    NORMAL = 1
    CHAVEIRO_DEUS_SUPREMO = 2

    @staticmethod
    def por_codigo(codigo: int) -> "NivelAcesso":
        for n in NivelAcesso:
            if n.value == codigo: return n
        raise IndexError(f"O código {codigo} não existe em NivelAcesso.")

class TipoPermissao(Enum):
    SOMENTE_LEITURA = 1
    LEITURA_E_ESCRITA = 2
    PROPRIETARIO = 3

    @staticmethod
    def por_codigo(codigo: int) -> "TipoPermissao":
        for n in TipoPermissao:
            if n.value == codigo: return n
        raise IndexError(f"O código {codigo} não existe em TipoPermissao.")

class TipoSegredo(Enum):
    PUBLICO = 1
    ENCONTRAVEL = 2
    CONFIDENCIAL = 3

    @staticmethod
    def por_codigo(codigo: int) -> "TipoSegredo":
        for n in TipoSegredo:
            if n.value == codigo: return n
        raise IndexError(f"O código {codigo} não existe em TipoSegredo.")