from datetime import datetime, timezone

from sqlalchemy import Index

from app.extensions import db
from app.models.enums import TipoMidia


class MidiaAmigurumi(db.Model):
    __tablename__ = "midia_amigurumi"

    __table_args__ = (
        Index("ix_midia_amigurumi_amigurumi_id", "amigurumi_id"),
        Index("ix_midia_amigurumi_usuario_id", "usuario_id"),
        Index(
            "ix_midia_amigurumi_amigurumi_tipo",
            "amigurumi_id",
            "tipo"
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    amigurumi_id = db.Column(
        db.Integer,
        db.ForeignKey("amigurumi.id"),
        nullable=False
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id"),
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

    amigurumi = db.relationship(
        "Amigurumi",
        back_populates="midias"
    )

    usuario = db.relationship(
        "Usuario",
        back_populates="midias_amigurumi"
    )