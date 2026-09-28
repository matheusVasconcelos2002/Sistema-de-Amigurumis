import secrets
from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models import RecuperacaoSenha, Usuario


class RecuperacaoSenhaService:

    TEMPO_EXPIRACAO_MINUTOS = 30

    @staticmethod
    def criar_token(email):
        """
        Cria um token de recuperação de senha para o usuário.
        """

        email = (email or "").strip().lower()

        if not email:
            raise ValueError("O e-mail é obrigatório.")

        usuario = db.session.scalar(
            db.select(Usuario).where(
                Usuario.email == email
            )
        )

        if not usuario:
            raise ValueError(
                "Não foi possível localizar uma conta com este e-mail."
            )

        # Invalida tokens anteriores ainda não utilizados.
        tokens_anteriores = db.session.scalars(
            db.select(RecuperacaoSenha).where(
                RecuperacaoSenha.usuario_id == usuario.id,
                RecuperacaoSenha.usado.is_(False)
            )
        ).all()

        agora = datetime.now(timezone.utc)

        for token_anterior in tokens_anteriores:
            token_anterior.usado = True

        token = secrets.token_urlsafe(64)

        recuperacao = RecuperacaoSenha(
            usuario_id=usuario.id,
            token=token,
            expira_em=(
                agora
                + timedelta(
                    minutes=RecuperacaoSenhaService.TEMPO_EXPIRACAO_MINUTOS
                )
            ),
            usado=False,
            criado_em=agora
        )

        try:
            db.session.add(recuperacao)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return recuperacao

    @staticmethod
    def buscar_por_token(token):
        """
        Busca um token de recuperação pelo próprio token.
        """

        token = (token or "").strip()

        if not token:
            return None

        return db.session.scalar(
            db.select(RecuperacaoSenha).where(
                RecuperacaoSenha.token == token
            )
        )

    @staticmethod
    def validar_token(token):
        """
        Verifica se o token existe, ainda não foi utilizado
        e não expirou.
        """

        recuperacao = (
            RecuperacaoSenhaService.buscar_por_token(token)
        )

        if not recuperacao:
            raise ValueError(
                "O link de recuperação é inválido."
            )

        agora = datetime.now(timezone.utc)

        if recuperacao.usado:
            raise ValueError(
                "Este link de recuperação já foi utilizado."
            )

        if recuperacao.expira_em <= agora:
            raise ValueError(
                "Este link de recuperação expirou."
            )

        return recuperacao

    @staticmethod
    def marcar_como_usado(token):
        """
        Marca o token como utilizado depois que a senha
        foi alterada com sucesso.
        """

        recuperacao = (
            RecuperacaoSenhaService.validar_token(token)
        )

        recuperacao.usado = True

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return recuperacao