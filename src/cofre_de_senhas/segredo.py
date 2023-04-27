from typing import Self, TypeGuard
from dataclasses import dataclass, replace
from .bd import cf
from .cofre_enum import *
from .dao import *
from .dao_impl import *
from .service import *
from .usuario import *
from .categoria import *

sdao = SegredoDAOImpl(cf)

@dataclass(frozen = True)
class Segredo:
    pk_segredo: int
    nome: str
    descricao: str
    tipo_segredo: TipoSegredo

    @staticmethod
    def __confirmar_que_segredo_ja_existe(chave: SegredoPK) -> SegredoPK:
        u: SegredoPK | None = sdao.buscar_pk_segredo(chave)
        if u is None: raise SegredoNaoExisteException()
        return u

    @staticmethod
    def __alterar_dados_segredo(dados: SegredoComChave, usuarios: dict[str, Usuario], categorias: dict[str, Categoria]) -> None:

        spk: SegredoPK = SegredoPK(dados.chave.valor)
        sdao.limpar_segredo(spk)

        for descricao in dados.campos.keys():
            valor: str = dados.campos[descricao]
            sdao.criar_campo_segredo(spk, descricao, valor)

        for login in dados.usuarios.keys():
            upk: UsuarioPK = usuarios[login].pk
            permissao: TipoPermissao = dados.usuarios[login]
            sdao.criar_permissao(upk, spk, permissao.value)

        for nome in dados.categorias:
            cpk: CategoriaPK = categorias[nome].pk
            sdao.criar_categoria_segredo(spk, cpk)

    @staticmethod
    def criar_segredo(quem_faz: Usuario, dados: SegredoSemChave) -> None:
        if not quem_faz.is_admin and dados.usuarios[quem_faz.login] != TipoPermissao.PROPRIETARIO: raise PermissaoNegadaException

        usuarios: dict[str, Usuario] = Usuario.listar_por_login({*dados.usuarios})
        categorias: dict[str, Categoria] = Categoria.listar_por_nomes(dados.categorias)

        rowid: SegredoPK = sdao.criar_segredo(dados.nome, dados.descricao, dados.tipo.value)

        Segredo.__alterar_dados_segredo(dados.com_chave(SegredoChave(rowid.pk_segredo)), usuarios, categorias)

    @staticmethod
    def alterar_segredo(dados: SegredoComChave) -> None:
        spk: SegredoPK = SegredoPK(dados.chave.valor)
        Segredo.__confirmar_que_segredo_ja_existe(spk) # Pode lançar SegredoNaoExisteException
        usuarios: dict[str, Usuario] = Usuario.listar_por_login({*dados.usuarios})
        categorias: dict[str, Categoria] = Categoria.listar_por_nomes(dados.categorias)

        sdao.alterar_segredo(spk, dados.nome, dados.descricao, dados.tipo.value)

        Segredo.__alterar_dados_segredo(dados, usuarios, categorias)

    @staticmethod
    def excluir_segredo(quem_faz: Usuario, dados: SegredoChave) -> None:
        spk: SegredoPK = SegredoPK(dados.valor)
        Segredo.__confirmar_que_segredo_ja_existe(spk) # Pode lançar SegredoNaoExisteException

        if not quem_faz.is_admin:
            tipo_permissao: int | None = sdao.buscar_permissao(spk, quem_faz.login)
            if tipo_permissao is None: raise PermissaoNegadaException
            permissao: TipoPermissao = TipoPermissao.por_codigo(tipo_permissao)
            if permissao not in [TipoPermissao.LEITURA_E_ESCRITA, TipoPermissao.PROPRIETARIO]: raise PermissaoNegadaException

        sdao.deletar_segredo(spk)

    @staticmethod
    def listar_segredos(quem_faz: Usuario) -> list[CabecalhoDeSegredo]:
        if quem_faz.is_admin:
            return sdao.listar_todos_segredos()
        else:
            return sdao.listar_segredos_visiveis(quem_faz.login)

    @staticmethod
    def buscar_segredo(quem_faz: Usuario, chave: SegredoChave) -> SegredoComChave:
        spk: SegredoPK = SegredoPK(chave.valor)

        cabecalho: CabecalhoDeSegredo | None = sdao.ler_cabecalho_segredo(spk)
        if cabecalho is None: raise SegredoNaoExisteException()

        tipo: TipoSegredo = cabecalho.fk_tipo_segredo

        campos: dict[str, str] = {elemento.chave: elemento.valor for elemento in sdao.ler_campos_segredo(spk)}
        categorias: set[str] = {elemento.nome for elemento in Categoria.listar_por_segredo(spk)}
        usuarios: dict[str, TipoPermissao] = {elemento.login: elemento.permissao for elemento in sdao.ler_login_com_permissoes(spk)}

        if not quem_faz.is_admin and quem_faz.login not in usuarios: raise SegredoNaoExisteException()

        return SegredoComChave(chave, cabecalho.nome, cabecalho.descricao, tipo, campos, categorias, usuarios)

    @staticmethod
    def pesquisar_segredos(quem_faz: Usuario, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos:
        raise NotImplementedError()
