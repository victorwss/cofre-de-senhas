from typing import override
from cofre_de_senhas.erro import (
    SenhaErradaException, UsuarioNaoLogadoException, UsuarioBanidoException, PermissaoNegadaException,
    UsuarioJaExisteException, UsuarioNaoExisteException,
    CategoriaJaExisteException, CategoriaNaoExisteException, SegredoNaoExisteException
)
from sucesso import (
    Sucesso, Erro, Status, Ok,
    RequisicaoMalFormadaException, PrecondicaoFalhouException, ConteudoNaoReconhecidoException, ConteudoIncompreensivelException
)


def test_erro_500() -> None:
    class FooException(BaseException):
        pass

        def __str__(self) -> str:
            return "bababa"

    x: FooException = FooException()
    e: Erro = Erro.criar(x)

    assert not e.sucesso
    assert e.interno
    assert e.mensagem == "bababa"
    assert e.tipo == "FooException"
    assert e.status == 500


def test_erro_449() -> None:
    class FooException(BaseException, Status):
        pass

        def __str__(self) -> str:
            return "bababa"

        @override
        @property
        def status(self) -> int:
            return 449

    x: FooException = FooException()
    e: Erro = Erro.criar(x)

    assert not e.sucesso
    assert not e.interno
    assert e.mensagem == "bababa"
    assert e.tipo == "FooException"
    assert e.status == 449


def test_sucesso_1() -> None:
    s: Sucesso = Sucesso.criar("abacaxi")
    assert s.sucesso
    assert s.conteudo == "abacaxi"
    assert s.status == 200


def test_sucesso_2() -> None:
    s: Sucesso = Sucesso.criar([1, 2, 3])
    assert s.sucesso
    assert s.conteudo == [1, 2, 3]
    assert s.status == 200


def test_sucesso_3() -> None:
    s: Sucesso = Sucesso.criar([1, 2, 3], 256)
    assert s.sucesso
    assert s.conteudo == [1, 2, 3]
    assert s.status == 256


def test_sucesso_4() -> None:
    s: Sucesso = Sucesso.ok()
    assert s.sucesso
    assert s.conteudo == Ok()
    assert s.status == 200


def test_sucesso_5() -> None:
    s: Sucesso = Sucesso.ok(234)
    assert s.sucesso
    assert s.conteudo == Ok()
    assert s.status == 234


def verificar_excecao(x: Status, s: int) -> None:
    assert isinstance(x, Exception)
    assert x.status == s


def test_erro_400() -> None:
    verificar_excecao(RequisicaoMalFormadaException(), 400)


def test_erro_412() -> None:
    verificar_excecao(PrecondicaoFalhouException(), 412)


def test_erro_415() -> None:
    verificar_excecao(ConteudoNaoReconhecidoException(), 415)


def test_erro_422() -> None:
    verificar_excecao(ConteudoIncompreensivelException(), 422)


def test_senha_errada() -> None:
    verificar_excecao(SenhaErradaException(), 401)


def test_usuario_nao_logado() -> None:
    verificar_excecao(UsuarioNaoLogadoException(), 401)


def test_usuario_banido() -> None:
    verificar_excecao(UsuarioBanidoException(), 403)


def test_permissao_negada() -> None:
    verificar_excecao(PermissaoNegadaException(), 403)


def test_usuario_ja_existe() -> None:
    verificar_excecao(UsuarioJaExisteException(), 409)


def test_usuario_nao_existe() -> None:
    verificar_excecao(UsuarioNaoExisteException(), 404)


def test_categoria_ja_existe() -> None:
    verificar_excecao(CategoriaJaExisteException(), 409)


def test_categoria_nao_existe() -> None:
    verificar_excecao(CategoriaNaoExisteException(), 404)


def test_segredo_nao_existe() -> None:
    verificar_excecao(SegredoNaoExisteException(), 404)
