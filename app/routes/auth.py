import os

from datetime import datetime, timedelta, timezone
import secrets

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app
)

from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Usuario, RecuperacaoSenha
from app.services.usuario_service import UsuarioService
from app.services.sessao_service import SessaoService
from app.services.email_service import EmailService
from itsdangerous import URLSafeSerializer, BadSignature


auth_bp = Blueprint("auth", __name__)

auth_bp = Blueprint("auth", __name__)


# =========================================================
# ÚLTIMA CONTA UTILIZADA NO LOGIN
# =========================================================

NOME_COOKIE_ULTIMA_CONTA = "ultima_conta_login"
TEMPO_COOKIE_ULTIMA_CONTA = 60 * 60 * 24 * 30  # 30 dias


def _criar_token_ultima_conta(usuario_id):
    """
    Cria um identificador assinado para lembrar
    qual foi a última conta utilizada neste navegador.
    """

    serializer = URLSafeSerializer(
        current_app.config["SECRET_KEY"],
        salt="ultima-conta-login"
    )

    return serializer.dumps({
        "usuario_id": usuario_id
    })


def _obter_usuario_ultima_conta():
    """
    Recupera a última conta utilizada neste navegador.

    Se o cookie não existir, estiver inválido ou o usuário
    não existir mais no banco, retorna None.
    """

    token = request.cookies.get(NOME_COOKIE_ULTIMA_CONTA)

    if not token:
        return None

    try:
        serializer = URLSafeSerializer(
            current_app.config["SECRET_KEY"],
            salt="ultima-conta-login"
        )

        dados = serializer.loads(token)

        usuario_id = dados.get("usuario_id")

        if not usuario_id:
            return None

        usuario = db.session.get(
            Usuario,
            usuario_id
        )

        return usuario

    except (BadSignature, ValueError, TypeError):
        return None

# =========================================================
# CADASTRO
# =========================================================

@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form.get("nome", "")
        email = request.form.get("email", "")
        telefone = request.form.get("telefone", "")
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")

        try:

            UsuarioService.cadastrar(
                nome=nome,
                email=email,
                telefone=telefone,
                senha=senha,
                confirmar_senha=confirmar_senha
            )

            flash(
                "Conta criada com sucesso!",
                "sucesso"
            )

            return redirect(
                url_for("auth.login")
            )

        except ValueError as erro:

            flash(
                str(erro),
                "erro"
            )

            return render_template(
                "cadastro.html",
                nome=nome,
                email=email,
                telefone=telefone
            )

    return render_template(
        "cadastro.html"
    )


# =========================================================
# LOGIN
# =========================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "")
        senha = request.form.get("senha", "")

        try:

            usuario = UsuarioService.autenticar(
                email=email,
                senha=senha
            )

            sessao_usuario = SessaoService.criar(
                usuario
            )

            session.clear()

            session["usuario_id"] = usuario.id
            session["token_sessao"] = sessao_usuario.token

            flash(
                f"Bem-vindo, {usuario.nome}!",
                "sucesso"
            )

            resposta = redirect(
                url_for("main.dashboard")
            )

            # -------------------------------------------------
            # LEMBRA A ÚLTIMA CONTA UTILIZADA
            # -------------------------------------------------

            token_ultima_conta = _criar_token_ultima_conta(
                usuario.id
            )

            resposta.set_cookie(
                NOME_COOKIE_ULTIMA_CONTA,
                token_ultima_conta,
                max_age=TEMPO_COOKIE_ULTIMA_CONTA,
                httponly=True,
                samesite="Lax"
            )

            return resposta

        except ValueError as erro:

            flash(
                str(erro),
                "erro"
            )

            usuario_lembrado = _obter_usuario_ultima_conta()

            return render_template(
                "login.html",
                email=email,
                usuario_lembrado=usuario_lembrado
            )

    # ---------------------------------------------------------
    # GET = ABRIU A TELA DE LOGIN
    # ---------------------------------------------------------

    usuario_lembrado = _obter_usuario_ultima_conta()

    return render_template(
        "login.html",
        email="",
        usuario_lembrado=usuario_lembrado
    )

# =========================================================
# RECUPERAR SENHA
# =========================================================

@auth_bp.route("/recuperar-senha", methods=["GET", "POST"])
def recuperar_senha():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        # -------------------------------------------------
        # E-mail vazio
        # -------------------------------------------------

        if not email:

            flash(
                "Informe seu e-mail.",
                "erro"
            )

            return render_template(
                "recuperar_senha.html",
                email=email
            )

        # -------------------------------------------------
        # Procura o usuário
        # -------------------------------------------------

        usuario = db.session.scalar(
            db.select(Usuario).where(
                Usuario.email == email
            )
        )

        # -------------------------------------------------
        # Não revela se o e-mail está cadastrado
        # -------------------------------------------------

        if usuario is None:

            return redirect(
                url_for("auth.email_enviado")
            )

        # -------------------------------------------------
        # Remove tokens antigos ainda não utilizados
        # -------------------------------------------------

        try:

            db.session.execute(
                db.delete(RecuperacaoSenha).where(
                    RecuperacaoSenha.usuario_id == usuario.id,
                    RecuperacaoSenha.usado.is_(False)
                )
            )

            # -------------------------------------------------
            # Gera novo token
            # -------------------------------------------------

            token = secrets.token_urlsafe(32)

            agora = datetime.now(timezone.utc)

            expira_em = agora + timedelta(
                minutes=15
            )

            recuperacao = RecuperacaoSenha(
                usuario_id=usuario.id,
                token=token,
                expira_em=expira_em,
                usado=False,
                criado_em=agora
            )

            db.session.add(
                recuperacao
            )

            db.session.commit()

        except Exception:

            db.session.rollback()

            flash(
                "Não foi possível iniciar a recuperação da senha. "
                "Tente novamente.",
                "erro"
            )

            return render_template(
                "recuperar_senha.html",
                email=email
            )

        # -------------------------------------------------
        # Monta o link de recuperação
        # -------------------------------------------------

        url_sistema = os.getenv(
            "URL_SISTEMA",
            ""
        ).strip()

        if not url_sistema:

            # Se o endereço do sistema não estiver configurado,
            # não enviamos um link potencialmente incorreto.

            try:

                db.session.delete(
                    recuperacao
                )

                db.session.commit()

            except Exception:

                db.session.rollback()

            flash(
                "O endereço do sistema não está configurado. "
                "Entre em contato com o suporte.",
                "erro"
            )

            return render_template(
                "recuperar_senha.html",
                email=email
            )

        caminho_nova_senha = url_for(
            "auth.nova_senha",
            token=token
        )

        link = (
            f"{url_sistema.rstrip('/')}"
            f"{caminho_nova_senha}"
        )

        # -------------------------------------------------
        # Envia o e-mail
        # -------------------------------------------------

        try:

            EmailService.enviar_recuperacao(
                destinatario=usuario.email,
                nome=usuario.nome,
                link=link
            )

        except Exception as erro:

            # -------------------------------------------------
            # DEBUG TEMPORÁRIO
            # -------------------------------------------------
            # Enquanto estamos testando o envio, mostramos
            # o erro no terminal para facilitar o diagnóstico.
            # Depois podemos remover este print.

            print(
                f"ERRO AO ENVIAR E-MAIL DE RECUPERAÇÃO: {erro}"
            )

            # -------------------------------------------------
            # Se o envio falhar, invalidamos o token criado.
            # -------------------------------------------------

            try:

                db.session.delete(
                    recuperacao
                )

                db.session.commit()

            except Exception:

                db.session.rollback()

            flash(
                "Não foi possível enviar o e-mail de recuperação. "
                "Verifique as configurações de e-mail e tente novamente.",
                "erro"
            )

            return render_template(
                "recuperar_senha.html",
                email=email
            )

        # -------------------------------------------------
        # E-mail enviado com sucesso
        # -------------------------------------------------

        return redirect(
            url_for("auth.email_enviado")
        )

    return render_template(
        "recuperar_senha.html",
        email=""
    )


# =========================================================
# TELA DE CONFIRMAÇÃO DO ENVIO
# =========================================================

@auth_bp.route("/email-enviado")
def email_enviado():

    return render_template(
        "email_enviado.html"
    )


# =========================================================
# VERIFICAR CÓDIGO
# =========================================================

@auth_bp.route("/verificar-codigo", methods=["GET", "POST"])
def verificar_codigo():

    return render_template(
        "verificar_codigo.html"
    )


# =========================================================
# NOVA SENHA
# =========================================================

@auth_bp.route("/nova-senha/<token>", methods=["GET", "POST"])
def nova_senha(token):

    # -----------------------------------------------------
    # Procura o token
    # -----------------------------------------------------

    recuperacao = db.session.scalar(
        db.select(RecuperacaoSenha).where(
            RecuperacaoSenha.token == token
        )
    )

    # -----------------------------------------------------
    # Token inexistente
    # -----------------------------------------------------

    if recuperacao is None:

        flash(
            "O link de recuperação é inválido.",
            "erro"
        )

        return redirect(
            url_for("auth.recuperar_senha")
        )

    # -----------------------------------------------------
    # Token já utilizado
    # -----------------------------------------------------

    if recuperacao.usado:

        flash(
            "Este link de recuperação já foi utilizado.",
            "erro"
        )

        return redirect(
            url_for("auth.recuperar_senha")
        )

    # -----------------------------------------------------
    # Verifica expiração
    # -----------------------------------------------------

    agora = datetime.now(timezone.utc)

    if recuperacao.expira_em <= agora:

        flash(
            "Este link de recuperação expirou. "
            "Solicite um novo link.",
            "erro"
        )

        return redirect(
            url_for("auth.recuperar_senha")
        )

    # -----------------------------------------------------
    # POST = usuário enviou a nova senha
    # -----------------------------------------------------

    if request.method == "POST":

        senha = request.form.get(
            "senha",
            ""
        )

        confirmar_senha = request.form.get(
            "confirmar_senha",
            ""
        )

        # ---------------------------------------------
        # Validação da senha
        # ---------------------------------------------

        if not senha:

            flash(
                "Informe a nova senha.",
                "erro"
            )

            return render_template(
                "nova_senha.html",
                token=token
            )

        if len(senha) < 8:

            flash(
                "A senha deve possuir pelo menos 8 caracteres.",
                "erro"
            )

            return render_template(
                "nova_senha.html",
                token=token
            )

        if senha != confirmar_senha:

            flash(
                "As senhas não coincidem.",
                "erro"
            )

            return render_template(
                "nova_senha.html",
                token=token
            )

        # ---------------------------------------------
        # Procura o usuário
        # ---------------------------------------------

        usuario = db.session.scalar(
            db.select(Usuario).where(
                Usuario.id == recuperacao.usuario_id
            )
        )

        if usuario is None:

            flash(
                "Não foi possível localizar a conta.",
                "erro"
            )

            return redirect(
                url_for("auth.recuperar_senha")
            )

        # ---------------------------------------------
        # Atualiza a senha
        # ---------------------------------------------

        try:

            usuario.senha_hash = generate_password_hash(
                senha
            )

            recuperacao.usado = True

            db.session.commit()

        except Exception:

            db.session.rollback()

            flash(
                "Não foi possível alterar sua senha. "
                "Tente novamente.",
                "erro"
            )

            return render_template(
                "nova_senha.html",
                token=token
            )

        # ---------------------------------------------
        # Sucesso
        # ---------------------------------------------

        flash(
            "Senha alterada com sucesso! "
            "Agora você pode entrar na sua conta.",
            "sucesso"
        )

        return redirect(
            url_for("auth.login")
        )

    # -----------------------------------------------------
    # GET = abre a tela de nova senha
    # -----------------------------------------------------

    return render_template(
        "nova_senha.html",
        token=token
    )


# =========================================================
# LOGOUT
# =========================================================

@auth_bp.route("/logout")
def logout():

    usuario_id = session.get(
        "usuario_id"
    )

    token_sessao = session.get(
        "token_sessao"
    )

    if usuario_id and token_sessao:

        sessao_usuario = SessaoService.buscar_por_token(
            token_sessao
        )

        if sessao_usuario:

            SessaoService.encerrar(
                sessao_usuario
            )

    session.clear()

    flash(
        "Você saiu da sua conta.",
        "sucesso"
    )

    return redirect(
        url_for("auth.login")
    )