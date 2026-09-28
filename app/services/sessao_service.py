import secrets
from datetime import datetime

from flask import request

from app.extensions import db
from app.models import UsuarioSessao


class SessaoService:

    @staticmethod
    def criar(usuario):
        token = secrets.token_urlsafe(64)

        sessao = UsuarioSessao(
            usuario_id=usuario.id,
            token=token,
            dispositivo=SessaoService.obter_dispositivo(),
            navegador=SessaoService.obter_navegador(),
            sistema_operacional=SessaoService.obter_sistema_operacional(),
            ip=SessaoService.obter_ip(),
            ultimo_acesso=datetime.now()
        )

        try:
            db.session.add(sessao)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return sessao

    @staticmethod
    def obter_dispositivo():
        user_agent = request.user_agent

        if user_agent.platform in ["iphone", "android"]:
            return "Celular"

        if user_agent.platform in ["ipad", "tablet"]:
            return "Tablet"

        return "Computador"

    @staticmethod
    def obter_navegador():
        return request.user_agent.browser or "Desconhecido"

    @staticmethod
    def obter_sistema_operacional():
        plataforma = request.user_agent.platform

        if not plataforma:
            return "Desconhecido"

        sistemas = {
            "windows": "Windows",
            "macos": "macOS",
            "linux": "Linux",
            "android": "Android",
            "iphone": "iOS",
            "ipad": "iPadOS"
        }

        return sistemas.get(
            plataforma.lower(),
            plataforma
        )

    @staticmethod
    def obter_ip():
        return request.remote_addr or "Desconhecido"

    @staticmethod
    def buscar_por_token(token):
        """
        Busca uma sessão pelo token.
        """

        if not token:
            return None

        return db.session.scalar(
            db.select(UsuarioSessao).where(
                UsuarioSessao.token == token
            )
        )

    @staticmethod
    def encerrar(sessao):
        try:
            db.session.delete(sessao)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def encerrar_todas(usuario_id):
        sessoes = db.session.scalars(
            db.select(UsuarioSessao).where(
                UsuarioSessao.usuario_id == usuario_id
            )
        ).all()

        try:
            for sessao in sessoes:
                db.session.delete(sessao)

            db.session.commit()

        except Exception:
            db.session.rollback()
            raise