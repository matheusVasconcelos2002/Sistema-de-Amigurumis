from datetime import datetime

from app.extensions import db
from app.models import Anotacao


class AnotacaoService:

    @staticmethod
    def cadastrar(usuario_id, titulo, conteudo):
        """
        Cadastra uma nova anotação para o usuário.
        """

        titulo = (titulo or "").strip()
        conteudo = (conteudo or "").strip()

        if not titulo:
            raise ValueError("O título da anotação é obrigatório.")

        if len(titulo) > 200:
            raise ValueError(
                "O título da anotação deve ter no máximo 200 caracteres."
            )

        if not conteudo:
            raise ValueError("O conteúdo da anotação é obrigatório.")

        anotacao = Anotacao(
            usuario_id=usuario_id,
            titulo=titulo,
            conteudo=conteudo
        )

        try:
            db.session.add(anotacao)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return anotacao

    @staticmethod
    def buscar_por_id(usuario_id, anotacao_id):
        """
        Busca uma anotação pertencente ao usuário.
        """

        return db.session.scalar(
            db.select(Anotacao).where(
                Anotacao.id == anotacao_id,
                Anotacao.usuario_id == usuario_id
            )
        )

    @staticmethod
    def listar_ativas(usuario_id):
        """
        Retorna as anotações ativas do usuário.
        """

        return db.session.scalars(
            db.select(Anotacao)
            .where(
                Anotacao.usuario_id == usuario_id,
                Anotacao.excluido_em.is_(None)
            )
            .order_by(Anotacao.atualizado_em.desc())
        ).all()

    @staticmethod
    def listar_excluidas(usuario_id):
        """
        Retorna as anotações que estão na lixeira.
        """

        return db.session.scalars(
            db.select(Anotacao)
            .where(
                Anotacao.usuario_id == usuario_id,
                Anotacao.excluido_em.is_not(None)
            )
            .order_by(Anotacao.excluido_em.desc())
        ).all()

    @staticmethod
    def atualizar(usuario_id, anotacao_id, titulo, conteudo):
        """
        Atualiza uma anotação ativa pertencente ao usuário.
        """

        titulo = (titulo or "").strip()
        conteudo = (conteudo or "").strip()

        if not titulo:
            raise ValueError("O título da anotação é obrigatório.")

        if len(titulo) > 200:
            raise ValueError(
                "O título da anotação deve ter no máximo 200 caracteres."
            )

        if not conteudo:
            raise ValueError("O conteúdo da anotação é obrigatório.")

        anotacao = AnotacaoService.buscar_por_id(
            usuario_id=usuario_id,
            anotacao_id=anotacao_id
        )

        if not anotacao:
            raise ValueError("Anotação não encontrada.")

        if anotacao.excluido_em is not None:
            raise ValueError(
                "Não é possível editar uma anotação que está na lixeira."
            )

        anotacao.titulo = titulo
        anotacao.conteudo = conteudo
        anotacao.atualizado_em = datetime.now()

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return anotacao

    @staticmethod
    def excluir(usuario_id, anotacao_id):
        """
        Move a anotação para a lixeira através de exclusão lógica.
        """

        anotacao = AnotacaoService.buscar_por_id(
            usuario_id=usuario_id,
            anotacao_id=anotacao_id
        )

        if not anotacao:
            raise ValueError("Anotação não encontrada.")

        if anotacao.excluido_em is not None:
            raise ValueError(
                "Esta anotação já está na lixeira."
            )

        anotacao.excluido_em = datetime.now()

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return anotacao

    @staticmethod
    def restaurar(usuario_id, anotacao_id):
        """
        Restaura uma anotação que está na lixeira.
        """

        anotacao = AnotacaoService.buscar_por_id(
            usuario_id=usuario_id,
            anotacao_id=anotacao_id
        )

        if not anotacao:
            raise ValueError("Anotação não encontrada.")

        if anotacao.excluido_em is None:
            raise ValueError(
                "Esta anotação já está ativa."
            )

        anotacao.excluido_em = None
        anotacao.atualizado_em = datetime.now()

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return anotacao