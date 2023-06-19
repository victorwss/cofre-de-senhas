from typing import Any, cast
from flask import Flask, headers, request, session
from cofre_de_senhas.httpwrap import *
from cofre_de_senhas.cofre_enum import *
from cofre_de_senhas.service import *
from cofre_de_senhas.service_impl import *
#from dacite import from_dict
#from werkzeug.datastructures import MultiDict

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

app.secret_key = ss.buscar_por_chave(ChaveSegredo(-1)).campos["Chave da sessão"]

#### Usuários

@app.route("/login", methods = ["POST"])
@empty_json
def login() -> None:
    read_body(LoginComSenha)
    su.login(read_body(LoginComSenha))

@app.route("/logout", methods = ["POST"])
@empty_json
def logout() -> None:
    su.logout()

@app.route("/usuarios")
@jsoner
def listar_usuarios() -> ResultadoListaDeUsuarios:
    return su.listar()

@app.route("/usuarios/<int:pk_usuario>")
@jsoner
def buscar_usuario_por_chave(pk_usuario: int) -> UsuarioComChave:
    return su.buscar_por_chave(ChaveUsuario(pk_usuario))

@app.route("/usuarios/<nome>")
@jsoner
def buscar_usuario_por_login(nome: str) -> UsuarioComChave:
    return su.buscar_por_login(LoginUsuario(nome))

#### Categorias

@app.route("/categorias/<int:pk_categoria>")
@jsoner
def buscar_categoria_por_chave(pk_categoria: int) -> CategoriaComChave:
    return sc.buscar_por_chave(ChaveCategoria(pk_categoria))

@app.route("/categorias/<nome>")
@jsoner
def buscar_categoria_por_nome(nome: str) -> CategoriaComChave:
    return sc.buscar_por_nome(NomeCategoria(nome))

@app.route("/categorias/<nome>", methods = ["PUT"])
@jsoner
def criar_categoria(nome: str) -> CategoriaComChave:
    return sc.criar(NomeCategoria(nome))

@app.route("/categorias/<nome>", methods = ["MOVE"])
@empty_json
def renomear_categoria(nome: str) -> None:
    dest: str | None = request.headers.get("Destination")
    if dest is None: raise RequisicaoMalFormadaException()
    overwrite: str | None = request.headers.get("Overwrite")
    if overwrite not in [None, "F", "T"]: raise RequisicaoMalFormadaException()
    try:
        sc.renomear(RenomeCategoria(nome, dest))
    except CategoriaJaExisteException as x:
        if overwrite == "F": raise PrecondicaoFalhouException()
        raise x

@app.route("/categorias")
@jsoner
def listar_categorias() -> ResultadoListaDeCategorias:
    return sc.listar()

@app.route("/categorias/<nome>", methods = ["DELETE"])
@empty_json
def excluir_categoria(nome: str) -> None:
    sc.excluir(NomeCategoria(nome))

def servir() -> None:
    app.run(host = "0.0.0.0", port = 5000)