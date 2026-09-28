from datetime import datetime, timezone

from sqlalchemy import Index

from app.extensions import db
from app.models.enums import FormaRecebimento


class Pedido(db.Model):
    __tablename__ = "pedido"

    __table_args__ = (
        Index("ix_pedido_usuario_id", "usuario_id"),
        Index("ix_pedido_cliente_id", "cliente_id"),
        Index("ix_pedido_data_pedido", "data_pedido"),
        Index("ix_pedido_forma_recebimento", "forma_recebimento"),
        Index(
            "ix_pedido_usuario_data",
            "usuario_id",
            "data_pedido"
        ),
        Index(
            "ix_pedido_usuario_cliente",
            "usuario_id",
            "cliente_id"
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

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("cliente.id"),
        nullable=False
    )

    nome = db.Column(
        db.String(200),
        nullable=False
    )

    data_pedido = db.Column(
        db.Date,
        nullable=False
    )

    forma_recebimento = db.Column(
        db.Enum(
            FormaRecebimento,
            name="forma_recebimento",
            native_enum=True,
            values_callable=lambda enum_cls: [
                item.value for item in enum_cls
            ],
        ),
        nullable=False,
        default=FormaRecebimento.A_DEFINIR
    )

    cliente_nome_snapshot = db.Column(
        db.String(150),
        nullable=False
    )

    cliente_telefone_snapshot = db.Column(
        db.String(20),
        nullable=False
    )

    endereco_cep = db.Column(
        db.String(8),
        nullable=True
    )

    endereco_estado = db.Column(
        db.String(2),
        nullable=True
    )

    endereco_cidade = db.Column(
        db.String(100),
        nullable=True
    )

    endereco_rua = db.Column(
        db.String(200),
        nullable=True
    )

    endereco_numero = db.Column(
        db.String(20),
        nullable=True
    )

    endereco_complemento = db.Column(
        db.String(150),
        nullable=True
    )

    endereco_bairro = db.Column(
        db.String(100),
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
        back_populates="pedidos"
    )

    cliente = db.relationship(
        "Cliente",
        back_populates="pedidos"
    )

    itens = db.relationship(
        "ItemPedido",
        back_populates="pedido",
        cascade="all, delete-orphan"
    )