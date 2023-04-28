from typing import Self, TypeGuard
from validator import dataclass_validate
from dataclasses import dataclass, replace
from cofre_de_senhas.bd.raiz import cf
from cofre_de_senhas.cofre_enum import TipoSegredo, TipoPermissao
from cofre_de_senhas.dao import *
from cofre_de_senhas.service import *
from cofre_de_senhas.usuario.usuario import Usuario, Permissao
from cofre_de_senhas.categoria.categoria import Categoria
from cofre_de_senhas.segredo.segredo_dao_impl import SegredoDAOImpl

dao = SegredoDAOImpl(cf)

@dataclass_validate
@dataclass(frozen = True)
class Segredo:
    pk_segredo: int
    nome: str
    descricao: str
    tipo_segredo: TipoSegredo
    usuarios: dict[str, Permissao] | None
    categorias: dict[str, Categoria] | None
    campos: dict[str, str] | None

    def excluir(self) -> Self:
        dao.deletar_por_pk(self.pk)
        return self

    def __salvar(self) -> Self:
        dao.salvar(self.__down)
        return self

    @property
    def chave(self) -> SegredoChave:
        return SegredoChave(self.pk_segredo)

    @property
    def pk(self) -> SegredoPK:
        return SegredoPK(self.pk_segredo)

    @property
    def up(self) -> CabecalhoSegredoComChave:
        return CabecalhoSegredoComChave(SegredoChave(self.pk_segredo), self.nome, self.descricao, self.tipo_segredo)

    @property
    def up_eager(self) -> CabecalhoSegredoComChave:
        permissoes: dict[str, TipoPermissao] = {k: self.usuarios[k].tipo for k in self.usuarios.keys()}
        return SegredoComChave(SegredoChave(self.pk_segredo), self.nome, self.descricao, self.tipo_segredo, permissoes, self.categorias.keys(), self.campos)

    @property
    def __down(self) -> DadosSegredo:
        return DadosSegredo(self.pk_segredo, self.nome, self.descricao, self.tipo_segredo.value)

    @staticmethod
    def __promote(dados: DadosSegredo) -> "Segredo":
        return Segredo(dados.pk_segredo, dados.nome, dados.descricao, TipoSegredo.por_codigo(dados.fk_tipo_segredo), None, None, None)

    @staticmethod
    def __promote_eager(dados: DadosSegredo) -> "Segredo":
        s: Segredo = Segredo.__promote(dados)
        campos: dict[str, str] = {c.pk_chave: c.valor for c in dao.ler_campos_segredo(s.pk)}
        usuarios: dict[str, Permissao] = Usuario.listar_por_permissao(s)
        categorias: dict[str, Categoria] = Categoria.listar_por_segredo(s.pk)
        return Segredo(dados.pk_segredo, dados.nome, dados.descricao, TipoSegredo.por_codigo(dados.fk_tipo_segredo), usuarios, categorias, campos)

    @staticmethod
    def encontrar_por_chave(chave: SegredoChave) -> "Segredo" | None:
        dados: DadosSegredo | None = dao.buscar_por_pk(SegredoPK(chave.valor))
        if dados is None: return None
        return Segredo.__promote_eager(dados)

    @staticmethod
    def encontrar_existente_por_chave(chave: SegredoChave) -> "Segredo":
        encontrado: Segredo | None = Segredo.encontrar_por_chave(chave)
        if encontrado is None: raise SegredoNaoExisteException()
        return encontrado

    def __alterar_dados_segredo(self) -> None:
        assert self.usuarios is not None
        assert self.categorias is not None
        assert self.campos is not None

        spk: SegredoPK = self.pk
        dao.limpar_segredo(spk)

        for descricao in self.campos.keys():
            valor: str = self.campos[descricao]
            dao.criar_campo_segredo(spk, descricao, valor)

        for permissao in self.usuarios.values():
            dao.criar_permissao(permissao.usuario.pk, spk, permissao.tipo.value)

        for categoria in self.categorias.values():
            dao.criar_categoria_segredo(spk, categoria.pk)

    @staticmethod
    def criar(quem_faz: Usuario, dados: SegredoSemChave) -> None:
        if not quem_faz.is_admin and dados.usuarios[quem_faz.login] != TipoPermissao.PROPRIETARIO: raise PermissaoNegadaException()

        usuarios: dict[str, Usuario] = Usuario.listar_por_login({*dados.usuarios})
        categorias: dict[str, Categoria] = Categoria.listar_por_nomes(dados.categorias)

        rowid: SegredoPK = dao.criar(DadosSegredoSemPK(dados.nome, dados.descricao, dados.tipo.value))

        Segredo.__alterar_dados_segredo(dados.com_chave(SegredoChave(rowid.pk_segredo)), usuarios, categorias)

    @staticmethod
    def listar() -> list["Segredo"]:
        return [Segredo.__promote(s) for s in dao.listar()]

    @staticmethod
    def alterar_segredo(dados: SegredoComChave) -> None:
        segredo: Segredo = Segredo.encontrar_existente_por_chave(dados.chave) # Pode lançar SegredoNaoExisteException
        segredo.__salvar()
        segredo.__alterar_dados_segredo()

    @staticmethod
    def excluir_segredo(quem_faz: Usuario, dados: SegredoChave) -> None:
        spk: SegredoPK = SegredoPK(dados.valor)
        segredo: Segredo = Segredo.encontrar_existente_por_chave(dados) # Pode lançar SegredoNaoExisteException

        if not quem_faz.is_admin:
            tipo_permissao: int | None = dao.buscar_permissao(spk, quem_faz.login)
            if tipo_permissao is None: raise PermissaoNegadaException()
            permissao: TipoPermissao = TipoPermissao.por_codigo(tipo_permissao)
            if permissao not in [TipoPermissao.LEITURA_E_ESCRITA, TipoPermissao.PROPRIETARIO]: raise PermissaoNegadaException()

        segredo.excluir()

    @staticmethod
    def listar_segredos_visiveis(quem_faz: Usuario) -> list["Segredo"]:
        return [Segredo.__promote(s) for s in dao.listar_visiveis(quem_faz.login)]

    @staticmethod
    def listar_segredos(quem_faz: Usuario) -> list["Segredo"]:
        if quem_faz.is_admin: return Segredo.listar()
        return Segredo.listar_segredos_visiveis(quem_faz)

    @staticmethod
    def buscar_segredo(quem_faz: Usuario, chave: SegredoChave) -> SegredoComChave:
        segredo: Segredo = encontrar_existente_por_chave(chave)
        if not quem_faz.is_admin and quem_faz.login not in segredo.usuarios.keys(): raise SegredoNaoExisteException()
        return segredo.up_eager

    @staticmethod
    def pesquisar_segredos(quem_faz: Usuario, dados: PesquisaSegredos) -> ResultadoPesquisaDeSegredos:
        raise NotImplementedError()
