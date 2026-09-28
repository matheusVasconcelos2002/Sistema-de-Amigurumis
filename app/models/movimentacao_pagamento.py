from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Index

from app.extensions import db
from app.models.enums import TipoMovimentacaoPagamento


class MovimentacaoPagamento(db.Model):
    __tablename__ = "movimentacao_pagamento"

    __table_args__ = (
        CheckConstraint(
            "valor > 0",
            name="ck_movimentacao_pagamento_valor_positivo"
        ),
        Index(
            "ix_movimentacao_pagamento_pagamento_id",
            "pagamento_id"
        ),
        Index(
            "ix_movimentacao_pagamento_tipo",
            "tipo"
        ),
        Index(
            "ix_movimentacao_pagamento_data",
            "data_movimentacao"
        ),
        Index(
            "ix_movimentacao_pagamento_pagamento_data",
            "pagamento_id",
            "data_movimentacao"
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    pagamento_id = db.Column(
        db.Integer,
        db.ForeignKey("pagamento.id"),
        nullable=False
    )

    tipo = db.Column(
        db.Enum(
            TipoMovimentacaoPagamento,
            name="tipo_movimentacao_pagamento",
            native_enum=True,
            values_callable=lambda enum_cls: [
                item.value for item in enum_cls
            ],
        ),
        nullable=False
    )

    valor = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    data_movimentacao = db.Column(
        db.DateTime(timezone=True),
        nullable=False
    )

    observacao = db.Column(
        db.String(500),
        nullable=True
    )

    criado_em = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    pagamento = db.relationship(
        "Pagamento",
        back_populates="movimentacoes"
    )