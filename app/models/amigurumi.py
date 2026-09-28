from datetime import datetime, timezone

from sqlalchemy import Index

from app.extensions import db


class Amigurumi(db.Model):
    __tablename__ = "amigurumi"

    __table_args__ = (
        Index("ix_amigurumi_usuario_id", "usuario_id"),
        Index("ix_amigurumi_usuario_produto", "usuario_id", "produto"),
        Index("ix_amigurumi_usuario_excluido", "usuario_id", "excluido_em"),
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

    produto = db.Column(
        db.String(150),
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
        back_populates="amigurumis"
    )
    midias = db.relationship(
        "MidiaAmigurumi",
        back_populates="amigurumi",
        cascade="all, delete-orphan"
    )

    itens_pedido = db.relationship(
        "ItemPedido",
        back_populates="amigurumi"
    )