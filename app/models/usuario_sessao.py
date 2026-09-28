from datetime import datetime, timezone

from sqlalchemy import Index

from app.extensions import db


class UsuarioSessao(db.Model):
    __tablename__ = "usuario_sessao"

    __table_args__ = (
        Index(
            "ix_usuario_sessao_usuario_id",
            "usuario_id"
        ),
        Index(
            "ix_usuario_sessao_ultimo_acesso",
            "ultimo_acesso"
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

    dispositivo = db.Column(
        db.String(100),
        nullable=True
    )

    navegador = db.Column(
        db.String(100),
        nullable=True
    )

    sistema_operacional = db.Column(
        db.String(100),
        nullable=True
    )

    ip = db.Column(
        db.String(45),
        nullable=True
    )

    criada_em = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    ultimo_acesso = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    usuario = db.relationship(
        "Usuario",
        back_populates="sessoes"
    )