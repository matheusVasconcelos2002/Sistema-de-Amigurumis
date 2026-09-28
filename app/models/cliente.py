from datetime import datetime, timezone

from sqlalchemy import Index

from app.extensions import db


class Cliente(db.Model):
    __tablename__ = "cliente"

    __table_args__ = (
        Index("ix_cliente_usuario_id", "usuario_id"),
        Index("ix_cliente_usuario_nome", "usuario_id", "nome"),
        Index("ix_cliente_usuario_excluido", "usuario_id", "excluido_em"),
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

    nome = db.Column(
        db.String(150),
        nullable=False
    )

    telefone = db.Column(
        db.String(20),
        nullable=False
    )

    cep = db.Column(
        db.String(8),
        nullable=True
    )

    estado = db.Column(
        db.String(2),
        nullable=False
    )

    cidade = db.Column(
        db.String(100),
        nullable=False
    )

    rua = db.Column(
        db.String(200),
        nullable=False
    )

    numero = db.Column(
        db.String(20),
        nullable=True
    )

    complemento = db.Column(
        db.String(150),
        nullable=True
    )

    bairro = db.Column(
        db.String(100),
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
        back_populates="clientes"
    )
    pedidos = db.relationship(
        "Pedido",
        back_populates="cliente"
    )