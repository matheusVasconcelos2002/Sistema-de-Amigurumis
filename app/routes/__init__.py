from flask import Flask

from config import Config
from app.extensions import db, migrate


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    from app.models import (
        Usuario,
        Cliente,
        Amigurumi,
        MidiaAmigurumi,
        Pedido,
        ItemPedido,
        MidiaItemPedido,
        Pagamento,
        MovimentacaoPagamento,
        Anotacao,
        UsuarioSessao,
        RecuperacaoSenha,
        PreferenciasUsuario,
    )

    migrate.init_app(app, db)

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.clientes import clientes_bp
    app.register_blueprint(clientes_bp)

    return app