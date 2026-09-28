from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Index

from app.extensions import db
from app.models.enums import StatusItemPedido


class ItemPedido(db.Model):
    __tablename__ = "item_pedido"

    __table_args__ = (
        CheckConstraint(
            "quantidade > 0",
            name="ck_item_pedido_quantidade_positiva"
        ),
        CheckConstraint(
            "tamanho > 0",
            name="ck_item_pedido_tamanho_positivo"
        ),
        CheckConstraint(
            "preco_unitario > 0",
            name="ck_item_pedido_preco_unitario_positivo"
        ),
        Index(
            "ix_item_pedido_pedido_id",
            "pedido_id"
        ),
        Index(
            "ix_item_pedido_amigurumi_id",
            "amigurumi_id"
        ),
        Index(
            "ix_item_pedido_status",
            "status"
        ),
        Index(
            "ix_item_pedido_data_prevista_entrega",
            "data_prevista_entrega"
        ),
        Index(
            "ix_item_pedido_pedido_status",
            "pedido_id",
            "status"
        ),
        Index(
            "ix_item_pedido_amigurumi_status",
            "amigurumi_id",
            "status"
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    pedido_id = db.Column(
        db.Integer,
        db.ForeignKey("pedido.id"),
        nullable=False
    )

    amigurumi_id = db.Column(
        db.Integer,
        db.ForeignKey("amigurumi.id"),
        nullable=False
    )

    quantidade = db.Column(
        db.Integer,
        nullable=False
    )

    tamanho = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    tipo = db.Column(
        db.String(100),
        nullable=False
    )

    preco_unitario = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    data_prevista_entrega = db.Column(
        db.Date,
        nullable=False
    )

    data_entrega = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    status = db.Column(
        db.Enum(
            StatusItemPedido,
            name="status_item_pedido",
            native_enum=True,
            values_callable=lambda enum_cls: [
                item.value for item in enum_cls
            ],
        ),
        nullable=False,
        default=StatusItemPedido.A_FAZER
    )

    motivo_cancelamento = db.Column(
        db.Text,
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

    pedido = db.relationship(
        "Pedido",
        back_populates="itens"
    )

    amigurumi = db.relationship(
        "Amigurumi",
        back_populates="itens_pedido"
    )

    midias = db.relationship(
        "MidiaItemPedido",
        back_populates="item_pedido",
        cascade="all, delete-orphan"
    )

    pagamento = db.relationship(
        "Pagamento",
        back_populates="item_pedido",
        uselist=False,
        cascade="all, delete-orphan"
    )