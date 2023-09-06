from typing import Any, cast, TypeVar
from flask import Flask, jsonify, redirect, request, session, url_for
from werkzeug import Response
from cofre_de_senhas.httpwrap import *
from cofre_de_senhas.service import *
from cofre_de_senhas.service_impl import *
from validator import dataclass_validate
from dataclasses import dataclass
#from werkzeug.datastructures import MultiDict

PORTA: int = 5000
app: Flask = Flask(__name__)
app.secret_key = ""

class GerenciadorLoginImpl(GerenciadorLogin):

    def login(self, usuario: UsuarioComChave) -> None:
        session["chave"] = usuario.chave

    def logout(self) -> None:
        session.pop("chave", None)

    # Pode lançar UsuarioNaoLogadoException.
    @property
    def usuario_logado(self) -> ChaveUsuario:
        if app.secret_key == "": return ChaveUsuario(-1)
        if "chave" not in session: raise UsuarioNaoLogadoException()
        return cast(ChaveUsuario, session["chave"])

gl: GerenciadorLogin = GerenciadorLoginImpl()
su: ServicoUsuario = ServicoUsuarioImpl(gl)
sc: ServicoCategoria = ServicoCategoriaImpl(gl)
ss: ServicoSegredo = ServicoSegredoImpl(gl)

#### Usuários

@app.route("/login", methods = ["POST"])
@empty_json
def login() -> None:
    read_body(LoginComSenha)
    su.login(read_body(LoginComSenha))

@app.route("/logout", methods = ["POST"])
@empty_json
def logout() -> None:
    bodyless()
    su.logout()

@app.route("/usuarios")
@jsoner
def listar_usuarios() -> ResultadoListaDeUsuarios:
    bodyless()
    return su.listar()

@app.route("/usuarios/<int:pk_usuario>")
@jsoner
def buscar_usuario_por_chave(pk_usuario: int) -> UsuarioComChave:
    bodyless()
    return su.buscar_por_chave(ChaveUsuario(pk_usuario))

@app.route("/usuarios/<nome>")
@jsoner
def buscar_usuario_por_login(nome: str) -> UsuarioComChave:
    bodyless()
    return su.buscar_por_login(LoginUsuario(nome))

@dataclass_validate
@dataclass(frozen = True)
class DadosNovoUsuario:
    senha: str
    nivel_acesso: str

@app.route("/usuarios/<nome>", methods = ["PUT"])
@jsoner
def criar_usuario(nome: str) -> UsuarioComChave:
    dados: DadosNovoUsuario = read_body(DadosNovoUsuario)
    try:
        p: NivelAcesso = NivelAcesso[dados.nivel_acesso]
    except:
        raise ConteudoIncompreensivelException()
    return su.criar(UsuarioNovo(nome, p, dados.senha))

@app.route("/trocar-senha", methods = ["POST"])
@empty_json
def trocar_senha() -> None:
    dados: TrocaSenha = read_body(TrocaSenha)
    return su.trocar_senha_por_chave(dados)

@dataclass_validate
@dataclass(frozen = True)
class DadosNovoNivel:
    nivel_acesso: str

@app.route("/usuarios/<nome>/alterar-nivel", methods = ["POST"])
@empty_json
def alterar_nivel(nome: str) -> None:
    dados: DadosNovoUsuario = read_body(DadosNovoUsuario)
    try:
        p: NivelAcesso = NivelAcesso[dados.nivel_acesso]
    except:
        raise ConteudoIncompreensivelException()
    su.alterar_nivel_por_login(UsuarioComNivel(nome, p))

@app.route("/usuarios/<nome>/resetar-senha", methods = ["POST"])
@jsoner
def resetar_senha(nome: str) -> SenhaAlterada:
    bodyless()
    return su.resetar_senha_por_login(ResetLoginUsuario(nome))

#### Categorias

@app.route("/categorias/<int:pk_categoria>")
@jsoner
def buscar_categoria_por_chave(pk_categoria: int) -> CategoriaComChave:
    bodyless()
    return sc.buscar_por_chave(ChaveCategoria(pk_categoria))

@app.route("/categorias/<nome>")
@jsoner
def buscar_categoria_por_nome(nome: str) -> CategoriaComChave:
    bodyless()
    return sc.buscar_por_nome(NomeCategoria(nome))

@app.route("/categorias/<nome>", methods = ["PUT"])
@jsoner
def criar_categoria(nome: str) -> CategoriaComChave:
    bodyless()
    return sc.criar(NomeCategoria(nome))

@app.route("/categorias/<nome>", methods = ["MOVE"])
@empty_json
def renomear_categoria(nome: str) -> None:
    bodyless()
    dest, overwrite = move()
    try:
        sc.renomear_por_nome(RenomeCategoria(nome, dest))
    except CategoriaJaExisteException as x:
        if not overwrite: raise PrecondicaoFalhouException()
        raise x

@app.route("/categorias")
@jsoner
def listar_categorias() -> ResultadoListaDeCategorias:
    bodyless()
    return sc.listar()

@app.route("/categorias/<nome>", methods = ["DELETE"])
@empty_json
def excluir_categoria(nome: str) -> None:
    bodyless()
    sc.excluir_por_nome(NomeCategoria(nome))

#### Segredos

@app.route("/segredos/", methods = ["PUT"])
@jsoner
def criar_segredo() -> SegredoComChave:
    dados: SegredoSemChave = read_body(SegredoSemChave)
    return ss.criar(dados)

@app.route("/segredos/<int:pk_segredo>", methods = ["PUT"])
@jsoner
def alterar_segredo(pk_segredo: int) -> SegredoComChave:
    dados: SegredoSemChave = read_body(SegredoSemChave)
    com_chave: SegredoComChave = dados.com_chave(ChaveSegredo(pk_segredo))
    ss.alterar_por_chave(com_chave)
    return com_chave

@app.route("/segredos/<int:pk_segredo>", methods = ["DELETE"])
@empty_json
def excluir_segredo(pk_segredo: int) -> None:
    bodyless()
    ss.excluir_por_chave(ChaveSegredo(pk_segredo))

@app.route("/segredos/<int:pk_segredo>")
@jsoner
def buscar_segredo_por_chave(pk_segredo: int) -> SegredoComChave:
    bodyless()
    return ss.buscar_por_chave(ChaveSegredo(pk_segredo))

@app.route("/segredos")
@jsoner
def listar_segredos() -> ResultadoPesquisaDeSegredos:
    bodyless()
    return ss.listar()

#### Front-end

@app.route("/")
def index() -> Response:
    bodyless()
    return redirect(url_for("static", filename = "index.html"))

@app.route("/map")
def map() -> str:
    x = ""
    for rule in app.url_map.iter_rules():
        #for method in rule.methods:
            f = "function xxx(" + ", ".join([str(arg) for arg in rule.arguments]) + ") {}"
            x += str(rule.endpoint)
            x += f
    return x

#### E aqui, a mágica acontece...

def servir() -> None:
    app.secret_key = ss.buscar_por_chave_sem_logar(ChaveSegredo(-1)).campos["Chave da sessão"]
    app.run(host = "0.0.0.0", port = PORTA, debug = True)