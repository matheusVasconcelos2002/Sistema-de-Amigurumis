from datetime import datetime, timezone

from sqlalchemy import Index

from app.extensions import db


class RecuperacaoSenha(db.Model):
    __tablename__ = "recuperacao_senha"

    __table_args__ = (
        Index(
            "ix_recuperacao_senha_usuario_id",
            "usuario_id"
        ),
        Index(
            "ix_recuperacao_senha_expira_em",
            "expira_em"
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id"),
        nullable=False
    )

    token = db.Column(
        db.String(255),
        nullable=False,
        unique=True
    )

    expira_em = db.Column(
        db.DateTime(timezone=True),
        nullable=False
    )

    usado = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    criado_em = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    usuario = db.relationship(
        "Usuario",
        back_populates="recuperacoes_senha"
    )