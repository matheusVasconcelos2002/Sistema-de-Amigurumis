from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.extensions import db
from app.models import Usuario
from app.services.amigurumi_service import AmigurumiService
from app.services.midia_service import MidiaService
from app.utils.autenticacao import login_required


amigurumis_bp = Blueprint(
    "amigurumis",
    __name__,
    url_prefix="/amigurumis",
)


def _usuario_atual():
    """
    Retorna o usuário atualmente autenticado.
    """
    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return None

    return db.session.get(
        Usuario,
        usuario_id,
    )


# =========================================================
# LISTAR AMIGURUMIS
# =========================================================

@amigurumis_bp.route("/")
@login_required
def listar():
    usuario_id = session["usuario_id"]

    usuario = _usuario_atual()

    amigurumis_ativos = (
        AmigurumiService.listar_ativos(
            usuario_id=usuario_id,
        )
    )

    amigurumis_excluidos = (
        AmigurumiService.listar_excluidos(
            usuario_id=usuario_id,
        )
    )

    return render_template(
        "amigurumis.html",
        usuario=usuario,
        amigurumis_ativos=amigurumis_ativos,
        amigurumis_excluidos=amigurumis_excluidos,
    )


# =========================================================
# NOVO AMIGURUMI
# =========================================================

@amigurumis_bp.route(
    "/novo",
    methods=["GET", "POST"],
)
@login_required
def novo():
    usuario_id = session["usuario_id"]
    usuario = _usuario_atual()

    if request.method == "POST":

        produto = request.form.get(
            "produto",
            "",
        ).strip()

        imagem = request.files.get(
            "imagem",
        )

        try:
            amigurumi = (
                AmigurumiService.cadastrar(
                    usuario_id=usuario_id,
                    produto=produto,
                )
            )

            # A imagem inicial é opcional.
            # Se existir, ela entra na mesma galeria
            # usada pelas demais imagens e vídeos.
            if imagem and imagem.filename:

                MidiaService.adicionar_midias(
                    usuario_id=usuario_id,
                    amigurumi_id=amigurumi.id,
                    arquivos=[imagem],
                )

            flash(
                "Amigurumi cadastrado com sucesso!",
                "sucesso",
            )

            return redirect(
                url_for(
                    "amigurumis.galeria",
                    amigurumi_id=amigurumi.id,
                )
            )

        except ValueError as erro:

            flash(
                str(erro),
                "erro",
            )

            return render_template(
                "adicionar_amigurumis.html",
                usuario=usuario,
                dados=request.form,
            )

        except Exception:

            db.session.rollback()

            flash(
                "Não foi possível cadastrar o amigurumi. "
                "Tente novamente.",
                "erro",
            )

            return render_template(
                "adicionar_amigurumis.html",
                usuario=usuario,
                dados=request.form,
            )

    return render_template(
        "adicionar_amigurumis.html",
        usuario=usuario,
        dados={},
    )


# =========================================================
# EDITAR AMIGURUMI
# =========================================================

@amigurumis_bp.route(
    "/<int:amigurumi_id>/editar",
    methods=["GET", "POST"],
)
@login_required
def editar(amigurumi_id):
    usuario_id = session["usuario_id"]
    usuario = _usuario_atual()

    amigurumi = (
        AmigurumiService.buscar_por_id(
            usuario_id=usuario_id,
            amigurumi_id=amigurumi_id,
        )
    )

    if not amigurumi:

        flash(
            "Amigurumi não encontrado.",
            "erro",
        )

        return redirect(
            url_for(
                "amigurumis.listar",
            )
        )

    if request.method == "POST":

        produto = request.form.get(
            "produto",
            "",
        ).strip()

        imagem = request.files.get(
            "imagem",
        )

        try:

            amigurumi = (
                AmigurumiService.atualizar(
                    usuario_id=usuario_id,
                    amigurumi_id=amigurumi_id,
                    produto=produto,
                )
            )

            # A imagem selecionada na edição é adicionada
            # à galeria; nenhuma mídia antiga é apagada.
            if imagem and imagem.filename:

                MidiaService.adicionar_midias(
                    usuario_id=usuario_id,
                    amigurumi_id=amigurumi_id,
                    arquivos=[imagem],
                )

            flash(
                "Amigurumi atualizado com sucesso!",
                "sucesso",
            )

            return redirect(
                url_for(
                    "amigurumis.galeria",
                    amigurumi_id=amigurumi_id,
                )
            )

        except ValueError as erro:

            flash(
                str(erro),
                "erro",
            )

            return render_template(
                "editar_amigurumis.html",
                usuario=usuario,
                amigurumi=amigurumi,
                dados=request.form,
            )

        except Exception:

            db.session.rollback()

            flash(
                "Não foi possível atualizar o amigurumi. "
                "Tente novamente.",
                "erro",
            )

            return render_template(
                "editar_amigurumis.html",
                usuario=usuario,
                amigurumi=amigurumi,
                dados=request.form,
            )

    return render_template(
        "editar_amigurumis.html",
        usuario=usuario,
        amigurumi=amigurumi,
        dados={},
    )


# =========================================================
# GALERIA
# =========================================================

@amigurumis_bp.route(
    "/<int:amigurumi_id>/galeria",
)
@login_required
def galeria(amigurumi_id):
    usuario_id = session["usuario_id"]
    usuario = _usuario_atual()

    amigurumi = (
        AmigurumiService.buscar_por_id(
            usuario_id=usuario_id,
            amigurumi_id=amigurumi_id,
        )
    )

    if not amigurumi:

        flash(
            "Amigurumi não encontrado.",
            "erro",
        )

        return redirect(
            url_for(
                "amigurumis.listar",
            )
        )

    return render_template(
        "galeria_amigurumis.html",
        usuario=usuario,
        amigurumi=amigurumi,
    )


# =========================================================
# ADICIONAR MÍDIAS À GALERIA
# =========================================================

@amigurumis_bp.route(
    "/<int:amigurumi_id>/midias",
    methods=["POST"],
)
@login_required
def adicionar_midias(amigurumi_id):
    usuario_id = session["usuario_id"]

    arquivos = request.files.getlist(
        "midias",
    )

    try:

        MidiaService.adicionar_midias(
            usuario_id=usuario_id,
            amigurumi_id=amigurumi_id,
            arquivos=arquivos,
        )

        flash(
            "Mídias adicionadas com sucesso!",
            "sucesso",
        )

    except ValueError as erro:

        flash(
            str(erro),
            "erro",
        )

    except Exception:

        db.session.rollback()

        flash(
            "Não foi possível adicionar as mídias. "
            "Tente novamente.",
            "erro",
        )

    return redirect(
        url_for(
            "amigurumis.galeria",
            amigurumi_id=amigurumi_id,
        )
    )


# =========================================================
# EXCLUIR MÍDIA
# =========================================================

@amigurumis_bp.route(
    "/<int:amigurumi_id>/midias/<int:midia_id>/excluir",
    methods=["POST"],
)
@login_required
def excluir_midia(
    amigurumi_id,
    midia_id,
):
    usuario_id = session["usuario_id"]

    try:

        MidiaService.excluir(
            usuario_id=usuario_id,
            amigurumi_id=amigurumi_id,
            midia_id=midia_id,
        )

        flash(
            "Mídia excluída com sucesso.",
            "sucesso",
        )

    except ValueError as erro:

        flash(
            str(erro),
            "erro",
        )

    except Exception:

        db.session.rollback()

        flash(
            "Não foi possível excluir a mídia. "
            "Tente novamente.",
            "erro",
        )

    return redirect(
        url_for(
            "amigurumis.galeria",
            amigurumi_id=amigurumi_id,
        )
    )


# =========================================================
# EXCLUIR AMIGURUMI
# =========================================================

@amigurumis_bp.route(
    "/<int:amigurumi_id>/excluir",
    methods=["POST"],
)
@login_required
def excluir(amigurumi_id):
    usuario_id = session["usuario_id"]

    try:

        AmigurumiService.excluir(
            usuario_id=usuario_id,
            amigurumi_id=amigurumi_id,
        )

        flash(
            "Amigurumi movido para os excluídos.",
            "sucesso",
        )

    except ValueError as erro:

        flash(
            str(erro),
            "erro",
        )

    return redirect(
        url_for(
            "amigurumis.listar",
        )
    )


# =========================================================
# RESTAURAR AMIGURUMI
# =========================================================

@amigurumis_bp.route(
    "/<int:amigurumi_id>/restaurar",
    methods=["POST"],
)
@login_required
def restaurar(amigurumi_id):
    usuario_id = session["usuario_id"]

    try:

        AmigurumiService.restaurar(
            usuario_id=usuario_id,
            amigurumi_id=amigurumi_id,
        )

        flash(
            "Amigurumi restaurado com sucesso!",
            "sucesso",
        )

    except ValueError as erro:

        flash(
            str(erro),
            "erro",
        )

    return redirect(
        url_for(
            "amigurumis.listar",
        )
    )
