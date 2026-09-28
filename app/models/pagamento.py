from datetime import datetime, timezone

from app.extensions import db
from app.models.enums import StatusPagamento


class Pagamento(db.Model):
    __tablename__ = "pagamento"


    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    item_pedido_id = db.Column(
        db.Integer,
        db.ForeignKey("item_pedido.id"),
        nullable=False,
        unique=True
    )

    status = db.Column(
        db.Enum(
            StatusPagamento,
            name="status_pagamento",
            native_enum=True,
            values_callable=lambda enum_cls: [
                item.value for item in enum_cls
            ],
        ),
        nullable=False,
        default=StatusPagamento.PENDENTE
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

    item_pedido = db.relationship(
        "ItemPedido",
        back_populates="pagamento"
    )

    movimentacoes = db.relationship(
        "MovimentacaoPagamento",
        back_populates="pagamento",
        cascade="all, delete-orphan"
    )