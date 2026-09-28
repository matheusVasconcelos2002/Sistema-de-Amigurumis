from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models import Usuario
from app.utils.validadores import normalizar_telefone, validar_telefone


class UsuarioService:

    @staticmethod
    def cadastrar(nome, email, telefone, senha, confirmar_senha):
        nome = nome.strip()
        email = email.strip().lower()
        telefone = normalizar_telefone(telefone)

        if not nome:
            raise ValueError("O nome é obrigatório.")

        if not email:
            raise ValueError("O email é obrigatório.")

        if not telefone:
            raise ValueError("O telefone é obrigatório.")

        if not validar_telefone(telefone):
            raise ValueError("Informe um telefone válido.")

        if not senha:
            raise ValueError("A senha é obrigatória.")

        if len(senha) < 8:
            raise ValueError(
                "A senha deve possuir pelo menos 8 caracteres."
            )

        if senha != confirmar_senha:
            raise ValueError("As senhas não coincidem.")

        usuario_existente = db.session.scalar(
            db.select(Usuario).where(Usuario.email == email)
        )

        if usuario_existente:
            raise ValueError("Este email já está cadastrado.")

        senha_hash = generate_password_hash(senha)

        usuario = Usuario(
            nome=nome,
            email=email,
            telefone=telefone,
            senha_hash=senha_hash
        )

        try:
            db.session.add(usuario)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return usuario

    @staticmethod
    def autenticar(email, senha):
        email = email.strip().lower()

        if not email:
            raise ValueError("O email é obrigatório.")

        if not senha:
            raise ValueError("A senha é obrigatória.")

        usuario = db.session.scalar(
            db.select(Usuario).where(Usuario.email == email)
        )

        if not usuario:
            raise ValueError("Email ou senha incorretos.")

        if not check_password_hash(usuario.senha_hash, senha):
            raise ValueError("Email ou senha incorretos.")

        return usuario

    @staticmethod
    def buscar_por_id(usuario_id):
        """
        Busca o usuário pelo ID.
        Usado pelas rotas que precisam recuperar
        o usuário atualmente autenticado.
        """
        if not usuario_id:
            return None

        return db.session.get(
            Usuario,
            usuario_id
        )