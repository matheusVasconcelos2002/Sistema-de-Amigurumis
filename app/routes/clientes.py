from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)

from app.services.cliente_service import ClienteService
from app.utils.autenticacao import login_required


clientes_bp = Blueprint(
    "clientes",
    __name__,
    url_prefix="/clientes"
)


@clientes_bp.route("/")
@login_required
def listar():
    """
    Exibe os clientes ativos e excluídos
    pertencentes ao usuário logado.
    """

    usuario_id = session["usuario_id"]

    clientes_ativos = ClienteService.listar_ativos(
        usuario_id
    )

    clientes_excluidos = ClienteService.listar_excluidos(
        usuario_id
    )

    return render_template(
        "clientes.html",
        clientes=clientes_ativos,
        clientes_excluidos=clientes_excluidos,
    )


@clientes_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    """
    Exibe o formulário e cadastra um novo cliente.
    """

    usuario_id = session["usuario_id"]

    if request.method == "POST":

        nome = request.form.get("nome", "")
        telefone = request.form.get("telefone", "")
        cep = request.form.get("cep", "")
        estado = request.form.get("estado", "")
        cidade = request.form.get("cidade", "")
        rua = request.form.get("rua", "")
        numero = request.form.get("numero", "")
        complemento = request.form.get("complemento", "")
        bairro = request.form.get("bairro", "")

        try:

            ClienteService.cadastrar(
                usuario_id=usuario_id,
                nome=nome,
                telefone=telefone,
                cep=cep,
                estado=estado,
                cidade=cidade,
                rua=rua,
                numero=numero,
                complemento=complemento,
                bairro=bairro,
            )

            flash(
                "Cliente cadastrado com sucesso!",
                "sucesso"
            )

            return redirect(
                url_for("clientes.listar")
            )

        except ValueError as erro:

            flash(
                str(erro),
                "erro"
            )

            return render_template(
                "adicionar_cliente.html",
                cliente=None,
                dados=request.form,
            )

    return render_template(
        "adicionar_cliente.html",
        cliente=None,
        dados={},
    )


@clientes_bp.route(
    "/<int:cliente_id>/editar",
    methods=["GET", "POST"]
)
@login_required
def editar(cliente_id):
    """
    Exibe o formulário e atualiza um cliente ativo.
    """

    usuario_id = session["usuario_id"]

    cliente = ClienteService.buscar_por_id(
        usuario_id=usuario_id,
        cliente_id=cliente_id
    )

    if not cliente:

        flash(
            "Cliente não encontrado.",
            "erro"
        )

        return redirect(
            url_for("clientes.listar")
        )

    if request.method == "POST":

        nome = request.form.get("nome", "")
        telefone = request.form.get("telefone", "")
        cep = request.form.get("cep", "")
        estado = request.form.get("estado", "")
        cidade = request.form.get("cidade", "")
        rua = request.form.get("rua", "")
        numero = request.form.get("numero", "")
        complemento = request.form.get("complemento", "")
        bairro = request.form.get("bairro", "")

        try:

            ClienteService.atualizar(
                usuario_id=usuario_id,
                cliente_id=cliente_id,
                nome=nome,
                telefone=telefone,
                cep=cep,
                estado=estado,
                cidade=cidade,
                rua=rua,
                numero=numero,
                complemento=complemento,
                bairro=bairro,
            )

            flash(
                "Cliente atualizado com sucesso!",
                "sucesso"
            )

            return redirect(
                url_for("clientes.listar")
            )

        except ValueError as erro:

            flash(
                str(erro),
                "erro"
            )

            return render_template(
                "editar_clientes.html",
                cliente=cliente,
                dados=request.form,
            )

    return render_template(
        "editar_clientes.html",
        cliente=cliente,
        dados={},
    )


@clientes_bp.route(
    "/<int:cliente_id>/excluir",
    methods=["POST"]
)
@login_required
def excluir(cliente_id):
    """
    Move o cliente para a lixeira.
    """

    usuario_id = session["usuario_id"]

    try:

        ClienteService.excluir(
            usuario_id=usuario_id,
            cliente_id=cliente_id
        )

        flash(
            "Cliente movido para a lixeira.",
            "sucesso"
        )

    except ValueError as erro:

        flash(
            str(erro),
            "erro"
        )

    return redirect(
        url_for("clientes.listar")
    )


@clientes_bp.route(
    "/<int:cliente_id>/restaurar",
    methods=["POST"]
)
@login_required
def restaurar(cliente_id):
    """
    Restaura um cliente da lixeira.
    """

    usuario_id = session["usuario_id"]

    try:

        ClienteService.restaurar(
            usuario_id=usuario_id,
            cliente_id=cliente_id
        )

        flash(
            "Cliente restaurado com sucesso!",
            "sucesso"
        )

    except ValueError as erro:

        flash(
            str(erro),
            "erro"
        )

    return redirect(
        url_for("clientes.listar")
    )