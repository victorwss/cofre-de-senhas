from typing import Self, TypeGuard
from dataclasses import dataclass, replace
from cofre_de_senhas.bd.raiz import cf
from cofre_de_senhas.cofre_enum import TipoSegredo, TipoPermissao
from cofre_de_senhas.dao import *
from cofre_de_senhas.service import *
from cofre_de_senhas.usuario.usuario import Usuario
from cofre_de_senhas.categoria.categoria import Categoria
from cofre_de_senhas.segredo.segredo_dao_impl import SegredoDAOImpl

dao = SegredoDAOImpl(cf)

@dataclass(frozen = True)
class Segredo:
    pk_segredo: int
    nome: str
    descricao: str
    tipo_segredo: TipoSegredo

    @property
    def up(self) -> CabecalhoSegredoComChave:
        return CabecalhoSegredoComChave(SegredoChave(self.pk_segredo), self.nome, self.descricao, self.tipo_segredo)

    #@property
    #def __down(self) -> DadosCategoria:
    #    return DadosCategoria(self.pk_categoria, self.nome)

    @staticmethod
    def __promote(dados: CabecalhoDeSegredo) -> "Segredo":
        return Segredo(dados.pk_segredo, dados.nome, dados.descricao, TipoSegredo.por_codigo(dados.fk_tipo_segredo))

    @staticmethod
    def __confirmar_que_segredo_ja_existe(chave: SegredoPK) -> SegredoPK:
        u: SegredoPK | None = dao.buscar_pk_segredo(chave)
        if u is None: raise SegredoNaoExisteException()
        return u

    @staticmethod
    def __alterar_dados_segredo(dados: SegredoComChave, usuarios: dict[str, Usuario], categorias: dict[str, Categoria]) -> None:

        spk: SegredoPK = SegredoPK(dados.chave.valor)
        dao.limpar_segredo(spk)

        for descricao in dados.campos.keys():
            valor: str = dados.campos[descricao]
            dao.criar_campo_segredo(spk, descricao, valor)

        for login in dados.usuarios.keys():
            upk: UsuarioPK = usuarios[login].pk
            permissao: TipoPermissao = dados.usuarios[login]
            dao.criar_permissao(upk, spk, permissao)

        for nome in dados.categorias:
            cpk: CategoriaPK = categorias[nome].pk
            dao.criar_categoria_segredo(spk, cpk)

    @staticmethod
    def criar_segredo(quem_faz: Usuario, dados: SegredoSemChave) -> None:
        if not quem_faz.is_admin and dados.usuarios[quem_faz.login] != TipoPermissao.PROPRIETARIO: raise PermissaoNegadaException()

        usuarios: dict[str, Usuario] = Usuario.listar_por_login({*dados.usuarios})
        categorias: dict[str, Categoria] = Categoria.listar_por_nomes(dados.categorias)

        rowid: SegredoPK = dao.criar_segredo(dados.nome, dados.descricao, dados.tipo)

        Segredo.__alterar_dados_segredo(dados.com_chave(SegredoChave(rowid.pk_segredo)), usuarios, categorias)

    @staticmethod
    def alterar_segredo(dados: SegredoComChave) -> None:
        spk: SegredoPK = SegredoPK(dados.chave.valor)
        Segredo.__confirmar_que_segredo_ja_existe(spk) # Pode lançar SegredoNaoExisteException
        usuarios: dict[str, Usuario] = Usuario.listar_por_login({*dados.usuarios})
        categorias: dict[str, Categoria] = Categoria.listar_por_nomes(dados.categorias)

        dao.alterar_segredo(spk, dados.nome, dados.descricao, dados.tipo)

        Segredo.__alterar_dados_segredo(dados, usuarios, categorias)

    @staticmethod
    def excluir_segredo(quem_faz: Usuario, dados: SegredoChave) -> None:
        spk: SegredoPK = SegredoPK(dados.valor)
        Segredo.__confirmar_que_segredo_ja_existe(spk) # Pode lançar SegredoNaoExisteException

        if not quem_faz.is_admin:
            tipo_permissao: int | None = dao.buscar_permissao(spk, quem_faz.login)
            if tipo_permissao is None: raise PermissaoNegadaException()
            permissao: TipoPermissao = TipoPermissao.por_codigo(tipo_permissao)
            if permissao not in [TipoPermissao.LEITURA_E_ESCRITA, TipoPermissao.PROPRIETARIO]: raise PermissaoNegadaException()

        dao.deletar_segredo(spk)

    @staticmethod
    def listar() -> list["Segredo"]:
        return [Segredo.__promote(s) for s in dao.listar_todos_segredos()]

    @staticmethod
    def listar_segredos_visiveis(quem_faz: Usuario) -> list["Segredo"]:
        return [Segredo.__promote(s) for s in dao.listar_segredos_visiveis(quem_faz.login)]

    @staticmethod
    def listar_segredos(quem_faz: Usuario) -> list["Segredo"]:
        if quem_faz.is_admin: return Segredo.listar()
        return Segredo.listar_segredos_visiveis(quem_faz)

    @staticmethod
    def buscar_segredo(quem_faz: Usuario, chave: SegredoChave) -> SegredoComChave:
        spk: SegredoPK = SegredoPK(chave.valor)

        cabecalho: CabecalhoDeSegredo | None = dao.ler_cabecalho_segredo(spk)
        if cabecalho is None: raise SegredoNaoExisteException()

        tipo: TipoSegredo = TipoSegredo.por_codigo(cabecalho.fk_tipo_segredo)

        campos: dict[str, str] = {elemento.pk_chave: elemento.valor for elemento in dao.ler_campos_segredo(spk)}
        categorias: set[str] = {elemento.nome for elemento in Categoria.listar_por_segredo(spk)}
        usuarios: dict[str, TipoPermissao] = {elemento.login: TipoPermissao.por_codigo(elemento.permissao) for elemento in dao.ler_login_com_permissoes(spk)}

        if not quem_faz.is_admin and quem_faz.login not in usuarios: raise SegredoNaoExisteException()

        return SegredoComChave(chave, cabecalho.nome, cabecalho.descricao, tipo, campos, categorias, usuarios)

    @staticmethod
    def pesquisar_segredos(quem_faz: Usuario, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos:
        raise NotImplementedError()
