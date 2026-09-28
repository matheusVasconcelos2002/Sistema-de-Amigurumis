from app.extensions import db
from app.models import PreferenciasUsuario
from app.models.enums import TemaInterface


class PreferenciasService:

    @staticmethod
    def buscar(usuario_id):
        """
        Busca as preferências do usuário.
        """

        return db.session.scalar(
            db.select(PreferenciasUsuario).where(
                PreferenciasUsuario.usuario_id == usuario_id
            )
        )

    @staticmethod
    def criar_padrao(usuario_id):
        """
        Cria as preferências padrão do usuário.
        """

        preferencias_existentes = (
            PreferenciasService.buscar(usuario_id)
        )

        if preferencias_existentes:
            return preferencias_existentes

        preferencias = PreferenciasUsuario(
            usuario_id=usuario_id,
            tema=TemaInterface.CLARO,
            cor_interface=None,
            cor_texto=None
        )

        try:
            db.session.add(preferencias)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return preferencias

    @staticmethod
    def _validar_tema(tema):
        """
        Valida o tema da interface.
        """

        if isinstance(tema, TemaInterface):
            return tema

        try:
            return TemaInterface(tema)
        except (ValueError, TypeError):
            raise ValueError(
                "O tema informado é inválido."
            )

    @staticmethod
    def _validar_cor(cor, nome_campo):
        """
        Valida uma cor personalizada.

        O banco utiliza varchar(30), portanto limitamos
        o valor a 30 caracteres.
        """

        if cor is None:
            return None

        cor = str(cor).strip()

        if not cor:
            return None

        if len(cor) > 30:
            raise ValueError(
                f"{nome_campo} deve ter no máximo 30 caracteres."
            )

        return cor

    @staticmethod
    def atualizar_tema(usuario_id, tema):
        """
        Atualiza somente o tema da interface.
        """

        tema = PreferenciasService._validar_tema(tema)

        preferencias = PreferenciasService.buscar(
            usuario_id
        )

        if not preferencias:
            preferencias = PreferenciasService.criar_padrao(
                usuario_id
            )

        preferencias.tema = tema

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return preferencias

    @staticmethod
    def atualizar_cores(
        usuario_id,
        cor_interface=None,
        cor_texto=None
    ):
        """
        Atualiza as cores personalizadas da interface.
        """

        cor_interface = PreferenciasService._validar_cor(
            cor_interface,
            "A cor da interface"
        )

        cor_texto = PreferenciasService._validar_cor(
            cor_texto,
            "A cor do texto"
        )

        preferencias = PreferenciasService.buscar(
            usuario_id
        )

        if not preferencias:
            preferencias = PreferenciasService.criar_padrao(
                usuario_id
            )

        preferencias.cor_interface = cor_interface
        preferencias.cor_texto = cor_texto

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return preferencias

    @staticmethod
    def atualizar(
        usuario_id,
        tema,
        cor_interface=None,
        cor_texto=None
    ):
        """
        Atualiza todas as preferências do usuário.
        """

        tema = PreferenciasService._validar_tema(tema)

        cor_interface = PreferenciasService._validar_cor(
            cor_interface,
            "A cor da interface"
        )

        cor_texto = PreferenciasService._validar_cor(
            cor_texto,
            "A cor do texto"
        )

        preferencias = PreferenciasService.buscar(
            usuario_id
        )

        if not preferencias:
            preferencias = PreferenciasService.criar_padrao(
                usuario_id
            )

        preferencias.tema = tema
        preferencias.cor_interface = cor_interface
        preferencias.cor_texto = cor_texto

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return preferencias

    @staticmethod
    def restaurar_padrao(usuario_id):
        """
        Restaura as preferências para os valores padrão.
        """

        preferencias = PreferenciasService.buscar(
            usuario_id
        )

        if not preferencias:
            return PreferenciasService.criar_padrao(
                usuario_id
            )

        preferencias.tema = TemaInterface.CLARO
        preferencias.cor_interface = None
        preferencias.cor_texto = None

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return preferencias