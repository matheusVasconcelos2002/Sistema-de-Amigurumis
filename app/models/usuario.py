from datetime import datetime, timezone

from app.extensions import db


class Usuario(db.Model):
    __tablename__ = "usuario"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    nome = db.Column(
        db.String(150),
        nullable=False
    )

    email = db.Column(
        db.String(255),
        nullable=False,
        unique=True
    )

    telefone = db.Column(
        db.String(20),
        nullable=False
    )

    senha_hash = db.Column(
        db.String(255),
        nullable=False
    )

    foto_perfil = db.Column(
        db.String(500),
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

    clientes = db.relationship(
        "Cliente",
        back_populates="usuario"
    )

    amigurumis = db.relationship(
        "Amigurumi",
        back_populates="usuario"
    )
    midias_amigurumi = db.relationship(
        "MidiaAmigurumi",
        back_populates="usuario"
    )

    pedidos = db.relationship(
        "Pedido",
        back_populates="usuario"
    )

    anotacoes = db.relationship(
        "Anotacao",
        back_populates="usuario"
    )

    sessoes = db.relationship(
        "UsuarioSessao",
        back_populates="usuario"
    )

    recuperacoes_senha = db.relationship(
        "RecuperacaoSenha",
        back_populates="usuario"
    )

    preferencias = db.relationship(
        "PreferenciasUsuario",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan"
    )