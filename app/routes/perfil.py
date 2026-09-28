import os
import uuid

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Usuario
from app.utils.autenticacao import login_required
from app.utils.validadores import normalizar_telefone, validar_telefone


perfil_bp = Blueprint(
    "perfil",
    __name__,
    url_prefix="/perfil"
)


EXTENSOES_FOTO_PERMITIDAS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
}

TAMANHO_MAXIMO_FOTO = 20 * 1024 * 1024


def _obter_usuario_logado():
    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return None

    return db.session.scalar(
        db.select(Usuario).where(
            Usuario.id == usuario_id
        )
    )


def _extensao_permitida(nome_arquivo):
    if not nome_arquivo or "." not in nome_arquivo:
        return False

    extensao = nome_arquivo.rsplit(".", 1)[1].lower()

    return extensao in EXTENSOES_FOTO_PERMITIDAS


def _salvar_foto(arquivo):
    if not arquivo or not arquivo.filename:
        raise ValueError("Selecione uma foto.")

    if not _extensao_permitida(arquivo.filename):
        raise ValueError(
            "Formato de foto inválido. "
            "Use JPG, JPEG, PNG ou WEBP."
        )

    arquivo.seek(0, os.SEEK_END)

    tamanho = arquivo.tell()

    arquivo.seek(0)

    if tamanho > TAMANHO_MAXIMO_FOTO:
        raise ValueError(
            "A foto deve ter no máximo 20 MB."
        )

    nome_original = secure_filename(
        arquivo.filename
    )

    if not nome_original:
        raise ValueError(
            "O nome da foto é inválido."
        )

    extensao = nome_original.rsplit(
        ".",
        1
    )[1].lower()

    nome_arquivo = (
        f"{uuid.uuid4().hex}.{extensao}"
    )

    pasta_fotos = os.path.join(
        current_app.static_folder,
        "fotos_perfil"
    )

    os.makedirs(
        pasta_fotos,
        exist_ok=True
    )

    caminho = os.path.join(
        pasta_fotos,
        nome_arquivo
    )

    arquivo.save(caminho)

    return nome_arquivo


@perfil_bp.route(
    "/",
    methods=["GET"]
)
@login_required
def listar():

    usuario = _obter_usuario_logado()

    if usuario is None:
        session.clear()

        flash(
            "Usuário não encontrado.",
            "erro"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "perfil.html",
        usuario=usuario
    )


@perfil_bp.route(
    "/atualizar",
    methods=["POST"]
)
@login_required
def atualizar():

    usuario = _obter_usuario_logado()

    if usuario is None:
        session.clear()

        flash(
            "Usuário não encontrado.",
            "erro"
        )

        return redirect(
            url_for("auth.login")
        )

    nome = request.form.get(
        "nome",
        ""
    ).strip()

    telefone = request.form.get(
        "telefone",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    if not nome:
        flash(
            "O nome é obrigatório.",
            "erro"
        )

        return redirect(
            url_for("perfil.listar")
        )

    if len(nome) > 150:
        flash(
            "O nome deve possuir no máximo "
            "150 caracteres.",
            "erro"
        )

        return redirect(
            url_for("perfil.listar")
        )

    telefone = normalizar_telefone(
        telefone
    )

    if not telefone:
        flash(
            "O telefone é obrigatório.",
            "erro"
        )

        return redirect(
            url_for("perfil.listar")
        )

    if not validar_telefone(telefone):
        flash(
            "Informe um telefone válido.",
            "erro"
        )

        return redirect(
            url_for("perfil.listar")
        )

    if not email:
        flash(
            "O e-mail é obrigatório.",
            "erro"
        )

        return redirect(
            url_for("perfil.listar")
        )

    if len(email) > 255:
        flash(
            "O e-mail deve possuir no máximo "
            "255 caracteres.",
            "erro"
        )

        return redirect(
            url_for("perfil.listar")
        )

    usuario_existente = db.session.scalar(
        db.select(Usuario).where(
            Usuario.email == email,
            Usuario.id != usuario.id
        )
    )

    if usuario_existente:
        flash(
            "Este e-mail já está sendo usado "
            "por outra conta.",
            "erro"
        )

        return redirect(
            url_for("perfil.listar")
        )

    try:

        usuario.nome = nome
        usuario.telefone = telefone
        usuario.email = email

        db.session.commit()

        flash(
            "Informações pessoais atualizadas "
            "com sucesso.",
            "sucesso"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Não foi possível atualizar "
            "suas informações.",
            "erro"
        )

    return redirect(
        url_for("perfil.listar")
    )


@perfil_bp.route(
    "/atualizar-foto",
    methods=["POST"]
)
@login_required
def atualizar_foto():

    usuario = _obter_usuario_logado()

    if usuario is None:
        session.clear()

        flash(
            "Usuário não encontrado.",
            "erro"
        )

        return redirect(
            url_for("auth.login")
        )

    arquivo = request.files.get(
        "foto_perfil"
    )

    if not arquivo or not arquivo.filename:
        flash(
            "Selecione uma foto para continuar.",
            "erro"
        )

        return redirect(
            url_for("perfil.listar")
        )

    foto_anterior = usuario.foto_perfil

    novo_nome = None

    try:

        novo_nome = _salvar_foto(
            arquivo
        )

        usuario.foto_perfil = novo_nome

        db.session.commit()

    except ValueError as erro:

        flash(
            str(erro),
            "erro"
        )

        return redirect(
            url_for("perfil.listar")
        )

    except Exception:

        db.session.rollback()

        if novo_nome:

            caminho_nova_foto = os.path.join(
                current_app.static_folder,
                "fotos_perfil",
                novo_nome
            )

            if os.path.exists(
                caminho_nova_foto
            ):

                try:
                    os.remove(
                        caminho_nova_foto
                    )

                except OSError:
                    pass

        flash(
            "Não foi possível atualizar "
            "a foto de perfil.",
            "erro"
        )

        return redirect(
            url_for("perfil.listar")
        )

    if foto_anterior:

        caminho_foto_anterior = os.path.join(
            current_app.static_folder,
            "fotos_perfil",
            foto_anterior
        )

        if os.path.exists(
            caminho_foto_anterior
        ):

            try:

                os.remove(
                    caminho_foto_anterior
                )

            except OSError:
                pass

    flash(
        "Foto de perfil atualizada "
        "com sucesso.",
        "sucesso"
    )

    return redirect(
        url_for("perfil.listar")
    )