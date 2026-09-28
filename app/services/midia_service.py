from __future__ import annotations

import os
import uuid
from pathlib import Path

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Amigurumi, MidiaAmigurumi
from app.models.enums import TipoMidia


class MidiaService:
    """
    Serviço responsável pelas mídias dos amigurumis.

    Regras alinhadas à tela galeria_amigurumis.html:

    - Imagens: JPG, JPEG, PNG e WEBP.
    - Imagens: máximo de 15 MB por arquivo.
    - Vídeos: MP4 e WEBM.
    - Vídeos: máximo de 105 MB por arquivo.
    - Permite múltiplos arquivos no mesmo envio.
    - Cada mídia pertence a um amigurumi e a um usuário.
    - O caminho salvo no banco é relativo à pasta static/.
    """

    LIMITE_IMAGEM = 15 * 1024 * 1024
    LIMITE_VIDEO = 105 * 1024 * 1024

    EXTENSOES_IMAGEM = {
        "jpg",
        "jpeg",
        "png",
        "webp",
    }

    EXTENSOES_VIDEO = {
        "mp4",
        "webm",
    }

    TIPOS_IMAGEM = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    TIPOS_VIDEO = {
        "video/mp4",
        "video/webm",
    }

    # =========================================================
    # BUSCAR AMIGURUMI
    # =========================================================

    @staticmethod
    def _buscar_amigurumi(usuario_id, amigurumi_id):
        """
        Garante que o amigurumi pertence ao usuário logado.
        """

        return db.session.scalar(
            db.select(Amigurumi).where(
                Amigurumi.id == amigurumi_id,
                Amigurumi.usuario_id == usuario_id,
            )
        )

    # =========================================================
    # DIRETÓRIO DAS MÍDIAS
    # =========================================================

    @staticmethod
    def _obter_diretorio(amigurumi_id, usuario_id):
        """
        Retorna o diretório físico das mídias.

        Estrutura:

        static/
        └── uploads/
            └── amigurumis/
                └── usuario_id/
                    └── amigurumi_id/
        """

        diretorio = (
            Path(current_app.static_folder)
            / "uploads"
            / "amigurumis"
            / str(usuario_id)
            / str(amigurumi_id)
        )

        diretorio.mkdir(
            parents=True,
            exist_ok=True,
        )

        return diretorio

    # =========================================================
    # EXTENSÃO
    # =========================================================

    @staticmethod
    def _obter_extensao(nome):
        """
        Obtém a extensão sem o ponto e em minúsculas.
        """

        nome = (nome or "").strip()

        if "." not in nome:
            return ""

        return nome.rsplit(".", 1)[1].lower()

    # =========================================================
    # TAMANHO
    # =========================================================

    @staticmethod
    def _obter_tamanho(arquivo):
        """
        Obtém o tamanho do arquivo sem carregar todo o conteúdo
        para a memória.
        """

        try:
            posicao_atual = arquivo.stream.tell()

            arquivo.stream.seek(
                0,
                os.SEEK_END,
            )

            tamanho = arquivo.stream.tell()

            arquivo.stream.seek(
                posicao_atual,
                os.SEEK_SET,
            )

            return tamanho

        except (OSError, ValueError):
            raise ValueError(
                f"Não foi possível verificar o tamanho "
                f"do arquivo '{arquivo.filename}'."
            )

    # =========================================================
    # VALIDAR ARQUIVO
    # =========================================================

    @classmethod
    def _validar_arquivo(cls, arquivo):
        """
        Valida extensão, tipo MIME e tamanho.

        Retorna:

        (
            tipo_midia,
            extensao,
            tamanho_bytes
        )
        """

        if not arquivo:
            raise ValueError(
                "Arquivo de mídia inválido."
            )

        nome_original = (
            arquivo.filename or ""
        ).strip()

        if not nome_original:
            raise ValueError(
                "Foi enviado um arquivo sem nome."
            )

        extensao = cls._obter_extensao(
            nome_original
        )

        if not extensao:
            raise ValueError(
                f"O arquivo '{nome_original}' "
                "não possui extensão válida."
            )

        tipo_mime = (
            arquivo.mimetype or ""
        ).lower()

        # -----------------------------------------------------
        # IMAGEM
        # -----------------------------------------------------

        if extensao in cls.EXTENSOES_IMAGEM:

            if tipo_mime and tipo_mime not in cls.TIPOS_IMAGEM:

                raise ValueError(
                    f"O arquivo '{nome_original}' "
                    "não possui um tipo de imagem permitido."
                )

            tipo = TipoMidia.IMAGEM

            limite = cls.LIMITE_IMAGEM

        # -----------------------------------------------------
        # VÍDEO
        # -----------------------------------------------------

        elif extensao in cls.EXTENSOES_VIDEO:

            if tipo_mime and tipo_mime not in cls.TIPOS_VIDEO:

                raise ValueError(
                    f"O arquivo '{nome_original}' "
                    "não possui um tipo de vídeo permitido."
                )

            tipo = TipoMidia.VIDEO

            limite = cls.LIMITE_VIDEO

        # -----------------------------------------------------
        # FORMATO NÃO PERMITIDO
        # -----------------------------------------------------

        else:

            raise ValueError(
                f"O arquivo '{nome_original}' possui "
                "um formato não permitido. "
                "Use JPG, JPEG, PNG, WEBP, MP4 ou WEBM."
            )

        tamanho = cls._obter_tamanho(
            arquivo
        )

        if tamanho <= 0:

            raise ValueError(
                f"O arquivo '{nome_original}' está vazio."
            )

        if tamanho > limite:

            limite_mb = (
                15
                if tipo == TipoMidia.IMAGEM
                else 105
            )

            raise ValueError(
                f"O arquivo '{nome_original}' "
                f"ultrapassa o limite de {limite_mb} MB."
            )

        return (
            tipo,
            extensao,
            tamanho,
        )

    # =========================================================
    # NOME DO ARQUIVO
    # =========================================================

    @staticmethod
    def _gerar_nome_arquivo(arquivo, extensao):
        """
        Gera um nome físico seguro e único.

        O nome original não é usado diretamente no caminho.
        """

        nome_seguro = secure_filename(
            arquivo.filename or ""
        )

        if not nome_seguro:
            nome_seguro = "midia"

        base = Path(nome_seguro).stem

        base = secure_filename(base)

        if not base:
            base = "midia"

        identificador = uuid.uuid4().hex

        return (
            f"{base}_{identificador}.{extensao}"
        )

    # =========================================================
    # CAMINHO RELATIVO
    # =========================================================

    @staticmethod
    def _caminho_relativo(
        usuario_id,
        amigurumi_id,
        nome_arquivo,
    ):
        """
        Caminho que será salvo no banco.

        Exemplo:

        uploads/amigurumis/8/12/foto_a1b2c3.jpg
        """

        return str(
            Path("uploads")
            / "amigurumis"
            / str(usuario_id)
            / str(amigurumi_id)
            / nome_arquivo
        ).replace("\\", "/")

    # =========================================================
    # ADICIONAR MÍDIAS
    # =========================================================

    @classmethod
    def adicionar_midias(
        cls,
        usuario_id,
        amigurumi_id,
        arquivos,
    ):
        """
        Adiciona várias mídias ao mesmo amigurumi.

        O método primeiro valida todos os arquivos.
        Somente depois começa a salvar os arquivos físicos
        e registrar os dados no PostgreSQL.

        Retorna uma lista de MidiaAmigurumi.
        """

        amigurumi = cls._buscar_amigurumi(
            usuario_id=usuario_id,
            amigurumi_id=amigurumi_id,
        )

        if not amigurumi:

            raise ValueError(
                "Amigurumi não encontrado."
            )

        if amigurumi.excluido_em is not None:

            raise ValueError(
                "Não é possível adicionar mídias "
                "a um amigurumi excluído."
            )

        arquivos = [
            arquivo
            for arquivo in (arquivos or [])
            if arquivo and arquivo.filename
        ]

        if not arquivos:

            raise ValueError(
                "Selecione pelo menos uma imagem ou vídeo."
            )

        # -----------------------------------------------------
        # PRIMEIRA ETAPA:
        # validar tudo antes de salvar qualquer arquivo
        # -----------------------------------------------------

        arquivos_validados = []

        for arquivo in arquivos:

            tipo, extensao, tamanho = (
                cls._validar_arquivo(
                    arquivo
                )
            )

            arquivos_validados.append(
                (
                    arquivo,
                    tipo,
                    extensao,
                    tamanho,
                )
            )

        diretorio = cls._obter_diretorio(
            amigurumi_id=amigurumi_id,
            usuario_id=usuario_id,
        )

        midias_criadas = []
        caminhos_salvos = []

        try:

            # -------------------------------------------------
            # SEGUNDA ETAPA:
            # salvar arquivos + objetos SQLAlchemy
            # -------------------------------------------------

            for (
                arquivo,
                tipo,
                extensao,
                tamanho,
            ) in arquivos_validados:

                nome_original = (
                    arquivo.filename or ""
                ).strip()

                nome_original = (
                    nome_original[:255]
                )

                nome_arquivo = (
                    cls._gerar_nome_arquivo(
                        arquivo=arquivo,
                        extensao=extensao,
                    )
                )

                caminho_fisico = (
                    diretorio / nome_arquivo
                )

                arquivo.save(
                    str(caminho_fisico)
                )

                caminhos_salvos.append(
                    caminho_fisico
                )

                caminho_relativo = (
                    cls._caminho_relativo(
                        usuario_id=usuario_id,
                        amigurumi_id=amigurumi_id,
                        nome_arquivo=nome_arquivo,
                    )
                )

                midia = MidiaAmigurumi(
                    amigurumi_id=amigurumi_id,
                    usuario_id=usuario_id,
                    tipo=tipo,
                    arquivo=caminho_relativo,
                    nome_original=nome_original,
                    tamanho_bytes=tamanho,
                )

                db.session.add(
                    midia
                )

                midias_criadas.append(
                    midia
                )

            db.session.commit()

            return midias_criadas

        except Exception:

            db.session.rollback()

            # Se o banco falhar, não deixamos arquivos órfãos
            for caminho in caminhos_salvos:

                try:

                    if caminho.exists():

                        caminho.unlink()

                except OSError:

                    pass

            raise

    # =========================================================
    # LISTAR MÍDIAS
    # =========================================================

    @classmethod
    def listar(
        cls,
        usuario_id,
        amigurumi_id,
    ):
        """
        Lista as mídias de um amigurumi pertencente
        ao usuário informado.
        """

        amigurumi = cls._buscar_amigurumi(
            usuario_id=usuario_id,
            amigurumi_id=amigurumi_id,
        )

        if not amigurumi:

            raise ValueError(
                "Amigurumi não encontrado."
            )

        return db.session.scalars(
            db.select(MidiaAmigurumi)
            .where(
                MidiaAmigurumi.usuario_id
                == usuario_id,

                MidiaAmigurumi.amigurumi_id
                == amigurumi_id,
            )
            .order_by(
                MidiaAmigurumi.criado_em.desc()
            )
        ).all()

    # =========================================================
    # BUSCAR UMA MÍDIA
    # =========================================================

    @classmethod
    def buscar_por_id(
        cls,
        usuario_id,
        amigurumi_id,
        midia_id,
    ):
        """
        Busca uma mídia garantindo simultaneamente:

        - usuário correto;
        - amigurumi correto;
        - mídia correta.
        """

        return db.session.scalar(
            db.select(MidiaAmigurumi).where(
                MidiaAmigurumi.id == midia_id,
                MidiaAmigurumi.amigurumi_id
                == amigurumi_id,
                MidiaAmigurumi.usuario_id
                == usuario_id,
            )
        )

    # =========================================================
    # EXCLUIR MÍDIA
    # =========================================================

    @classmethod
    def excluir(
        cls,
        usuario_id,
        amigurumi_id,
        midia_id,
    ):
        """
        Exclui permanentemente uma mídia.

        Primeiro remove o registro do banco.
        Depois remove o arquivo físico.

        A mídia não possui lixeira própria no modelo atual.
        """

        midia = cls.buscar_por_id(
            usuario_id=usuario_id,
            amigurumi_id=amigurumi_id,
            midia_id=midia_id,
        )

        if not midia:

            raise ValueError(
                "Mídia não encontrada."
            )

        caminho_fisico = (
            Path(current_app.static_folder)
            / Path(midia.arquivo)
        )

        try:

            db.session.delete(
                midia
            )

            db.session.commit()

        except Exception:

            db.session.rollback()
            raise

        # -----------------------------------------------------
        # Remover arquivo físico
        # -----------------------------------------------------

        try:

            if caminho_fisico.exists():

                caminho_fisico.unlink()

        except OSError as erro:

            current_app.logger.warning(
                "A mídia foi removida do banco, "
                "mas o arquivo físico não pôde ser removido: %s",
                erro,
            )

        # -----------------------------------------------------
        # Limpar diretório vazio
        # -----------------------------------------------------

        try:

            diretorio_midia = (
                caminho_fisico.parent
            )

            if (
                diretorio_midia.exists()
                and not any(
                    diretorio_midia.iterdir()
                )
            ):

                diretorio_midia.rmdir()

        except OSError:

            pass

        return midia
