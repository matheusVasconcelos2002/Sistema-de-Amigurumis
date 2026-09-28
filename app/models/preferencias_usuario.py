from datetime import datetime, timezone

from app.extensions import db
from app.models.enums import TemaInterface


class PreferenciasUsuario(db.Model):
    __tablename__ = "preferencias_usuario"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id"),
        nullable=False,
        unique=True
    )

    tema = db.Column(
        db.Enum(
            TemaInterface,
            name="tema_interface",
            native_enum=True,
            values_callable=lambda enum_cls: [
                item.value for item in enum_cls
            ],
        ),
        nullable=False,
        default=TemaInterface.CLARO
    )

    cor_interface = db.Column(
        db.String(30),
        nullable=True
    )

    cor_texto = db.Column(
        db.String(30),
        nullable=True
    )

    atualizado_em = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    usuario = db.relationship(
        "Usuario",
        back_populates="preferencias"
    )