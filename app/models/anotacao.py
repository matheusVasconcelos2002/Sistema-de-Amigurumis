from datetime import datetime, timezone

from sqlalchemy import Index

from app.extensions import db


class Anotacao(db.Model):
    __tablename__ = "anotacao"

    __table_args__ = (
        Index(
            "ix_anotacao_usuario_id",
            "usuario_id"
        ),
        Index(
            "ix_anotacao_usuario_excluido",
            "usuario_id",
            "excluido_em"
        ),
        Index(
            "ix_anotacao_usuario_atualizado",
            "usuario_id",
            "atualizado_em"
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

    titulo = db.Column(
        db.String(200),
        nullable=False
    )

    conteudo = db.Column(
        db.Text,
        nullable=False
    )

    excluido_em = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    criado_em = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    atualizado_em = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    usuario = db.relationship(
        "Usuario",
        back_populates="anotacoes"
    )