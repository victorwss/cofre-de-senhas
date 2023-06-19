from typing import cast
from flask import Flask, request, session
from cofre_de_senhas.httpwrap import *
from cofre_de_senhas.cofre_enum import *
from cofre_de_senhas.service import *
from cofre_de_senhas.service_impl import *
from dacite import from_dict
#from werkzeug.datastructures import MultiDict

app: Flask = Flask(__name__)
app.secret_key = ""

#_T = TypeVar("_T")
#def read_body(target: type[_T]) -> _T:
#    content_type: str = cast(str, request.headers.get("Content-Type"))
#    if (content_type == "application/json"):
#        json = request.json
#    else:
#        json = request.form
#    return from_dict(data_class = target, data = json)

class GerenciadorLoginImpl(GerenciadorLogin):

    def login(self, chave: UsuarioChave) -> None:
        session["chave"] = chave

    def logout(self) -> None:
        session.pop("chave", None)

    # Pode lançar UsuarioNaoLogadoException.
    @property
    def usuario_logado(self) -> UsuarioChave:
        if app.secret_key == "": return UsuarioChave(-1)
        if "chave" not in session: raise UsuarioNaoLogadoException()
        return cast(UsuarioChave, session["chave"])

gl: GerenciadorLogin = GerenciadorLoginImpl()
su: ServicoUsuario = ServicoUsuarioImpl(gl)
sc: ServicoCategoria = ServicoCategoriaImpl(gl)
ss: ServicoSegredo = ServicoSegredoImpl(gl)

app.secret_key = ss.buscar_segredo_por_chave(SegredoChave(-1)).campos["Chave da sessão"]

@app.route("/login", methods = ["POST"])
@empty_json
def login() -> None:
    raise Exception("TO DO")

@app.route("/categorias/<int:pk_categoria>")
@jsoner
def buscar_categoria_por_chave(pk_categoria: int) -> CategoriaComChave:
    return sc.buscar_categoria_por_chave(CategoriaChave(pk_categoria))

@app.route("/categorias/<nome>")
@jsoner
def buscar_categoria_por_nome(nome: str) -> CategoriaComChave:
    return sc.buscar_categoria_por_nome(NomeCategoria(nome))

@app.route("/categorias/<nome>", methods = ["PUT"])
@jsoner
def criar_categoria(nome: str) -> CategoriaComChave:
    return sc.criar_categoria(NomeCategoria(nome))

@app.route("/categorias")
@jsoner
def listar_categorias() -> ResultadoListaDeCategorias:
    return sc.listar_categorias()

@app.route("/categorias/<nome>", methods = ["DELETE"])
@empty_json
def excluir_categoria(nome: str) -> None:
    sc.excluir_categoria(NomeCategoria(nome))

def servir() -> None:
    app.run(host = "0.0.0.0", port = 5000)