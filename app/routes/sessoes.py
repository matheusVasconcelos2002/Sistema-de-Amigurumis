from flask import Blueprint, jsonify, render_template, session, flash

from app.extensions import db
from app.models import Usuario, UsuarioSessao
from app.services.sessao_service import SessaoService
from app.utils.autenticacao import login_required


sessoes_bp = Blueprint(
    "sessoes",
    __name__,
    url_prefix="/sessoes",
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


def _obter_sessao_atual():
    token = session.get(
        "token_sessao"
    )

    if not token:
        return None

    return SessaoService.buscar_por_token(
        token
    )


def _serializar_sessao(
    sessao,
    sessao_atual_id=None,
):

    return {
        "id": sessao.id,
        "dispositivo": (
            sessao.dispositivo
            or "Desconhecido"
        ),
        "navegador": (
            sessao.navegador
            or "Desconhecido"
        ),
        "sistema_operacional": (
            sessao.sistema_operacional
            or "Desconhecido"
        ),
        "ip": (
            sessao.ip
            or "Desconhecido"
        ),
        "criada_em": (
            sessao.criada_em.strftime(
                "%d/%m/%Y %H:%M"
            )
            if sessao.criada_em
            else "-"
        ),
        "ultimo_acesso": (
            sessao.ultimo_acesso.strftime(
                "%d/%m/%Y %H:%M"
            )
            if sessao.ultimo_acesso
            else "-"
        ),
        "atual": (
            sessao.id == sessao_atual_id
        ),
    }


@sessoes_bp.route("/", methods=["GET"])
@login_required
def listar():

    usuario = _obter_usuario()

    if usuario is None:
        flash(
            "Usuário não encontrado.",
            "erro",
        )

        return render_template(
            "sessoes.html",
            usuario=None,
            sessoes=[],
        )

    sessao_atual = (
        _obter_sessao_atual()
    )

    sessoes = db.session.scalars(
        db.select(UsuarioSessao)
        .where(
            UsuarioSessao.usuario_id
            == usuario.id
        )
        .order_by(
            UsuarioSessao.ultimo_acesso.desc()
        )
    ).all()

    sessao_atual_id = (
        sessao_atual.id
        if sessao_atual
        else None
    )

    sessoes_serializadas = [
        _serializar_sessao(
            sessao,
            sessao_atual_id,
        )
        for sessao in sessoes
    ]

    return render_template(
        "sessoes.html",
        usuario=usuario,
        sessoes=sessoes_serializadas,
    )


@sessoes_bp.route(
    "/<int:sessao_id>/encerrar",
    methods=["POST"],
)
@login_required
def encerrar(sessao_id):

    usuario = _obter_usuario()

    if usuario is None:
        return jsonify(
            {
                "sucesso": False,
                "mensagem": "Usuário não encontrado.",
            }
        ), 401

    sessao = db.session.scalar(
        db.select(UsuarioSessao).where(
            UsuarioSessao.id == sessao_id,
            UsuarioSessao.usuario_id
            == usuario.id,
        )
    )

    if sessao is None:
        return jsonify(
            {
                "sucesso": False,
                "mensagem": (
                    "Sessão não encontrada."
                ),
            }
        ), 404

    sessao_atual = (
        _obter_sessao_atual()
    )

    if (
        sessao_atual
        and sessao.id == sessao_atual.id
    ):
        return jsonify(
            {
                "sucesso": False,
                "mensagem": (
                    "Para encerrar a sessão atual, "
                    "utilize a opção Sair."
                ),
            }
        ), 400

    try:

        SessaoService.encerrar(
            sessao
        )

    except Exception:

        return jsonify(
            {
                "sucesso": False,
                "mensagem": (
                    "Não foi possível "
                    "encerrar a sessão."
                ),
            }
        ), 500

    return jsonify(
        {
            "sucesso": True,
            "mensagem": (
                "Sessão encerrada com sucesso."
            ),
        }
    )


@sessoes_bp.route(
    "/encerrar-outras",
    methods=["POST"],
)
@login_required
def encerrar_outras():

    usuario = _obter_usuario()

    if usuario is None:
        return jsonify(
            {
                "sucesso": False,
                "mensagem": "Usuário não encontrado.",
            }
        ), 401

    sessao_atual = (
        _obter_sessao_atual()
    )

    token_atual = session.get(
        "token_sessao"
    )

    try:

        consulta = (
            db.select(UsuarioSessao)
            .where(
                UsuarioSessao.usuario_id
                == usuario.id
            )
        )

        sessoes = db.session.scalars(
            consulta
        ).all()

        encerradas = 0

        for sessao in sessoes:

            if (
                token_atual
                and sessao.token
                == token_atual
            ):
                continue

            db.session.delete(
                sessao
            )

            encerradas += 1

        db.session.commit()

    except Exception:

        db.session.rollback()

        return jsonify(
            {
                "sucesso": False,
                "mensagem": (
                    "Não foi possível "
                    "encerrar as outras sessões."
                ),
            }
        ), 500

    return jsonify(
        {
            "sucesso": True,
            "mensagem": (
                f"{encerradas} sessão(ões) "
                "encerrada(s) com sucesso."
            ),
            "quantidade": encerradas,
        }
    )