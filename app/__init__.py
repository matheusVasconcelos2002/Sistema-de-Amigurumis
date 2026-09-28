from flask import Flask, session

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

    @app.context_processor
    def disponibilizar_usuario_logado():
        usuario = None

        usuario_id = session.get("usuario_id")

        if usuario_id:
            usuario = db.session.get(Usuario, usuario_id)

        return {
            "usuario": usuario
        }

    migrate.init_app(app, db)

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.clientes import clientes_bp
    app.register_blueprint(clientes_bp)

    from app.routes.amigurumis import amigurumis_bp
    app.register_blueprint(amigurumis_bp)

    from app.routes.pedidos import pedidos_bp
    app.register_blueprint(pedidos_bp)

    from app.routes.pagamentos import pagamentos_bp
    app.register_blueprint(pagamentos_bp)

    from app.routes.anotacoes import anotacoes_bp
    app.register_blueprint(anotacoes_bp)

    from app.routes.relatorios import relatorios_bp
    app.register_blueprint(relatorios_bp)

    from app.routes.configuracoes import configuracoes_bp
    app.register_blueprint(configuracoes_bp)

    from app.routes.sessoes import sessoes_bp
    app.register_blueprint(sessoes_bp)

    from app.routes.perfil import perfil_bp
    app.register_blueprint(perfil_bp)

    from app.routes.suporte import suporte_bp
    app.register_blueprint(suporte_bp)

    return app