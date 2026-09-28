from flask import Blueprint, render_template, session

from app.extensions import db
from app.models import Usuario
from app.services.suporte_service import SuporteService
from app.utils.autenticacao import login_required


suporte_bp = Blueprint(
    "suporte",
    __name__,
    url_prefix="/suporte"
)


def _obter_usuario():
    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return None

    return db.session.scalar(
        db.select(Usuario).where(Usuario.id == usuario_id)
    )


@suporte_bp.route("/", methods=["GET"])
@login_required
def listar():
    usuario = _obter_usuario()

    if usuario is None:
        return render_template(
            "suporte.html",
            usuario=None,
            suporte=SuporteService.obter_dados(),
        )

    return render_template(
        "suporte.html",
        usuario=usuario,
        suporte=SuporteService.obter_dados(),
    )