from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)

from app.extensions import db
from app.models import Usuario
from app.services.anotacao_service import AnotacaoService
from app.utils.autenticacao import login_required


anotacoes_bp = Blueprint(
    "anotacoes",
    __name__,
    url_prefix="/anotacoes",
)


def _obter_usuario():
    """
    Obtém o usuário autenticado através do usuario_id
    armazenado na sessão.
    """

    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return None

    return db.session.scalar(
        db.select(Usuario).where(
            Usuario.id == usuario_id
        )
    )


@anotacoes_bp.route("/")
@login_required
def listar():
    """
    Exibe as anotações ativas e as anotações
    que estão na lixeira.
    """

    usuario = _obter_usuario()

    if not usuario:
        session.clear()
        return redirect(url_for("auth.login"))

    usuario_id = usuario.id

    anotacoes = AnotacaoService.listar_ativas(
        usuario_id
    )

    anotacoes_excluidas = AnotacaoService.listar_excluidas(
        usuario_id
    )

    return render_template(
        "anotacoes.html",
        usuario=usuario,
        anotacoes=anotacoes,
        anotacoes_excluidas=anotacoes_excluidas,
        anotacao_edicao=None,
        titulo="",
        conteudo="",
    )


@anotacoes_bp.route("/nova", methods=["GET", "POST"])
@login_required
def nova():
    """
    Cria uma nova anotação.
    """

    usuario = _obter_usuario()

    if not usuario:
        session.clear()
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        titulo = request.form.get(
            "titulo",
            ""
        )

        conteudo = request.form.get(
            "conteudo",
            ""
        )

        try:

            AnotacaoService.cadastrar(
                usuario_id=usuario.id,
                titulo=titulo,
                conteudo=conteudo,
            )

            flash(
                "Anotação criada com sucesso.",
                "sucesso",
            )

            return redirect(
                url_for("anotacoes.listar")
            )

        except ValueError as erro:

            flash(
                str(erro),
                "erro",
            )

            anotacoes = AnotacaoService.listar_ativas(
                usuario.id
            )

            anotacoes_excluidas = AnotacaoService.listar_excluidas(
                usuario.id
            )

            return render_template(
                "anotacoes.html",
                usuario=usuario,
                anotacoes=anotacoes,
                anotacoes_excluidas=anotacoes_excluidas,
                anotacao_edicao=None,
                titulo=titulo,
                conteudo=conteudo,
            )

    return redirect(
        url_for("anotacoes.listar")
    )


@anotacoes_bp.route(
    "/<int:anotacao_id>/editar",
    methods=["GET", "POST"],
)
@login_required
def editar(anotacao_id):
    """
    Edita uma anotação ativa.
    """

    usuario = _obter_usuario()

    if not usuario:
        session.clear()
        return redirect(url_for("auth.login"))

    anotacao = AnotacaoService.buscar_por_id(
        usuario_id=usuario.id,
        anotacao_id=anotacao_id,
    )

    if not anotacao:

        flash(
            "Anotação não encontrada.",
            "erro",
        )

        return redirect(
            url_for("anotacoes.listar")
        )

    if anotacao.excluido_em is not None:

        flash(
            "Não é possível editar uma anotação que está na lixeira.",
            "erro",
        )

        return redirect(
            url_for("anotacoes.listar")
        )

    if request.method == "POST":

        titulo = request.form.get(
            "titulo",
            ""
        )

        conteudo = request.form.get(
            "conteudo",
            ""
        )

        try:

            AnotacaoService.atualizar(
                usuario_id=usuario.id,
                anotacao_id=anotacao_id,
                titulo=titulo,
                conteudo=conteudo,
            )

            flash(
                "Anotação atualizada com sucesso.",
                "sucesso",
            )

            return redirect(
                url_for("anotacoes.listar")
            )

        except ValueError as erro:

            flash(
                str(erro),
                "erro",
            )

            anotacoes = AnotacaoService.listar_ativas(
                usuario.id
            )

            anotacoes_excluidas = AnotacaoService.listar_excluidas(
                usuario.id
            )

            return render_template(
                "anotacoes.html",
                usuario=usuario,
                anotacoes=anotacoes,
                anotacoes_excluidas=anotacoes_excluidas,
                anotacao_edicao=anotacao,
                titulo=titulo,
                conteudo=conteudo,
            )

    anotacoes = AnotacaoService.listar_ativas(
        usuario.id
    )

    anotacoes_excluidas = AnotacaoService.listar_excluidas(
        usuario.id
    )

    return render_template(
        "anotacoes.html",
        usuario=usuario,
        anotacoes=anotacoes,
        anotacoes_excluidas=anotacoes_excluidas,
        anotacao_edicao=anotacao,
        titulo=anotacao.titulo,
        conteudo=anotacao.conteudo,
    )


@anotacoes_bp.route(
    "/<int:anotacao_id>/excluir",
    methods=["POST"],
)
@login_required
def excluir(anotacao_id):
    """
    Move uma anotação para a lixeira.
    """

    usuario = _obter_usuario()

    if not usuario:
        session.clear()
        return redirect(url_for("auth.login"))

    try:

        AnotacaoService.excluir(
            usuario_id=usuario.id,
            anotacao_id=anotacao_id,
        )

        flash(
            "Anotação movida para a lixeira.",
            "sucesso",
        )

    except ValueError as erro:

        flash(
            str(erro),
            "erro",
        )

    return redirect(
        url_for("anotacoes.listar")
    )


@anotacoes_bp.route(
    "/<int:anotacao_id>/restaurar",
    methods=["POST"],
)
@login_required
def restaurar(anotacao_id):
    """
    Restaura uma anotação da lixeira.
    """

    usuario = _obter_usuario()

    if not usuario:
        session.clear()
        return redirect(url_for("auth.login"))

    try:

        AnotacaoService.restaurar(
            usuario_id=usuario.id,
            anotacao_id=anotacao_id,
        )

        flash(
            "Anotação restaurada com sucesso.",
            "sucesso",
        )

    except ValueError as erro:

        flash(
            str(erro),
            "erro",
        )

    return redirect(
        url_for("anotacoes.listar")
    )