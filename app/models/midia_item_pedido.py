from datetime import datetime, timezone

from sqlalchemy import Index

from app.extensions import db
from app.models.enums import TipoMidia


class MidiaItemPedido(db.Model):
    __tablename__ = "midia_item_pedido"

    __table_args__ = (
        Index(
            "ix_midia_item_pedido_item_pedido_id",
            "item_pedido_id"
        ),
        Index(
            "ix_midia_item_pedido_item_tipo",
            "item_pedido_id",
            "tipo"
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    item_pedido_id = db.Column(
        db.Integer,
        db.ForeignKey("item_pedido.id"),
        nullable=False
    )

    tipo = db.Column(
        db.Enum(
            TipoMidia,
            name="tipo_midia",
            native_enum=True,
            values_callable=lambda enum_cls: [
                item.value for item in enum_cls
            ],
        ),
        nullable=False
    )

    arquivo = db.Column(
        db.String(500),
        nullable=False
    )

    nome_original = db.Column(
        db.String(255),
        nullable=True
    )

    tamanho_bytes = db.Column(
        db.BigInteger,
        nullable=True
    )

    criado_em = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    item_pedido = db.relationship(
        "ItemPedido",
        back_populates="midias"
    )