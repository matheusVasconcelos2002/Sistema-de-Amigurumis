from functools import wraps

from flask import session, redirect, url_for, flash

from app.extensions import db
from app.models import UsuarioSessao


def login_required(funcao):

    @wraps(funcao)
    def funcao_protegida(*args, **kwargs):

        usuario_id = session.get("usuario_id")
        token_sessao = session.get("token_sessao")

        if not usuario_id or not token_sessao:
            session.clear()

            flash(
                "Você precisa estar conectado para acessar esta página.",
                "erro"
            )

            return redirect(url_for("auth.login"))

        sessao = db.session.scalar(
            db.select(UsuarioSessao).where(
                UsuarioSessao.usuario_id == usuario_id,
                UsuarioSessao.token == token_sessao
            )
        )

        if not sessao:
            session.clear()

            flash(
                "Sua sessão não é mais válida. Faça login novamente.",
                "erro"
            )

            return redirect(url_for("auth.login"))

        return funcao(*args, **kwargs)

    return funcao_protegida