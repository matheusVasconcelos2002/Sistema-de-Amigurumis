from flask import Blueprint, jsonify, render_template, request, session, flash

from app.extensions import db
from app.models import Usuario
from app.services.preferencias_service import PreferenciasService
from app.utils.autenticacao import login_required


configuracoes_bp = Blueprint(
    "configuracoes",
    __name__,
    url_prefix="/configuracoes",
)


def _obter_usuario():
    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return None

    return db.session.scalar(
        db.select(Usuario).where(
            Usuario.id == usuario_id
        )
    )


@configuracoes_bp.route("/", methods=["GET"])
@login_required
def listar():

    usuario = _obter_usuario()

    if usuario is None:
        flash(
            "Usuário não encontrado.",
            "erro",
        )

        return render_template(
            "configuracoes.html",
            usuario=None,
            preferencias=None,
        )

    preferencias = PreferenciasService.buscar(
        usuario.id
    )

    if preferencias is None:
        preferencias = (
            PreferenciasService.criar_padrao(
                usuario.id
            )
        )

    return render_template(
        "configuracoes.html",
        usuario=usuario,
        preferencias=preferencias,
    )


@configuracoes_bp.route(
    "/preferencias",
    methods=["POST"],
)
@login_required
def salvar_preferencias():

    usuario = _obter_usuario()

    if usuario is None:
        return jsonify(
            {
                "sucesso": False,
                "mensagem": "Usuário não encontrado.",
            }
        ), 401

    dados = request.get_json(
        silent=True
    )

    if dados is None:
        dados = request.form

    tema = (
        dados.get("tema", "claro")
        or "claro"
    )

    cor_interface = (
        dados.get("cor_interface")
        or None
    )

    cor_texto = (
        dados.get("cor_texto")
        or None
    )

    try:

        preferencias = (
            PreferenciasService.atualizar(
                usuario_id=usuario.id,
                tema=tema,
                cor_interface=cor_interface,
                cor_texto=cor_texto,
            )
        )

    except ValueError as erro:

        return jsonify(
            {
                "sucesso": False,
                "mensagem": str(erro),
            }
        ), 400

    except Exception:

        return jsonify(
            {
                "sucesso": False,
                "mensagem": (
                    "Não foi possível salvar "
                    "as preferências."
                ),
            }
        ), 500

    return jsonify(
        {
            "sucesso": True,
            "mensagem": (
                "Preferências salvas com sucesso."
            ),
            "preferencias": {
                "tema": preferencias.tema.value,
                "cor_interface": (
                    preferencias.cor_interface
                ),
                "cor_texto": (
                    preferencias.cor_texto
                ),
            },
        }
    )


@configuracoes_bp.route(
    "/preferencias/restaurar",
    methods=["POST"],
)
@login_required
def restaurar_preferencias():

    usuario = _obter_usuario()

    if usuario is None:
        return jsonify(
            {
                "sucesso": False,
                "mensagem": "Usuário não encontrado.",
            }
        ), 401

    try:

        preferencias = (
            PreferenciasService.restaurar_padrao(
                usuario.id
            )
        )

    except Exception:

        return jsonify(
            {
                "sucesso": False,
                "mensagem": (
                    "Não foi possível restaurar "
                    "as preferências."
                ),
            }
        ), 500

    return jsonify(
        {
            "sucesso": True,
            "mensagem": (
                "Preferências restauradas."
            ),
            "preferencias": {
                "tema": preferencias.tema.value,
                "cor_interface": (
                    preferencias.cor_interface
                ),
                "cor_texto": (
                    preferencias.cor_texto
                ),
            },
        }
    )