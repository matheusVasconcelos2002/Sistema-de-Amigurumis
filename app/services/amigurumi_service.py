from app.extensions import db
from app.models import Amigurumi


class AmigurumiService:

    @staticmethod
    def cadastrar(usuario_id, produto, commit=True):
        """
        Cadastra um novo amigurumi para o usuário informado.

        Quando commit=True, salva imediatamente no banco.

        Quando commit=False, apenas adiciona o objeto à sessão.
        Nesse caso, o commit será responsabilidade da operação
        que estiver utilizando o serviço.
        """

        produto = (produto or "").strip()

        if not produto:
            raise ValueError(
                "O nome do amigurumi é obrigatório."
            )

        if len(produto) > 150:
            raise ValueError(
                "O nome do amigurumi deve ter no máximo 150 caracteres."
            )

        amigurumi = Amigurumi(
            usuario_id=usuario_id,
            produto=produto
        )

        try:

            db.session.add(amigurumi)

            if commit:
                db.session.commit()

            else:
                # Gera o ID sem efetivar a transação.
                db.session.flush()

        except Exception:

            db.session.rollback()
            raise

        return amigurumi

    @staticmethod
    def buscar_por_id(usuario_id, amigurumi_id):
        """
        Busca um amigurumi pertencente ao usuário informado.
        """

        return db.session.scalar(
            db.select(Amigurumi).where(
                Amigurumi.id == amigurumi_id,
                Amigurumi.usuario_id == usuario_id
            )
        )

    @staticmethod
    def listar_ativos(usuario_id):
        """
        Retorna somente os amigurumis ativos do usuário.
        """

        return db.session.scalars(
            db.select(Amigurumi)
            .where(
                Amigurumi.usuario_id == usuario_id,
                Amigurumi.excluido_em.is_(None)
            )
            .order_by(Amigurumi.produto.asc())
        ).all()

    @staticmethod
    def listar_excluidos(usuario_id):
        """
        Retorna somente os amigurumis excluídos do usuário.
        """

        return db.session.scalars(
            db.select(Amigurumi)
            .where(
                Amigurumi.usuario_id == usuario_id,
                Amigurumi.excluido_em.is_not(None)
            )
            .order_by(Amigurumi.excluido_em.desc())
        ).all()

    @staticmethod
    def atualizar(usuario_id, amigurumi_id, produto):
        """
        Atualiza o nome de um amigurumi pertencente ao usuário.
        """

        produto = (produto or "").strip()

        if not produto:
            raise ValueError("O nome do amigurumi é obrigatório.")

        if len(produto) > 150:
            raise ValueError(
                "O nome do amigurumi deve ter no máximo 150 caracteres."
            )

        amigurumi = AmigurumiService.buscar_por_id(
            usuario_id=usuario_id,
            amigurumi_id=amigurumi_id
        )

        if not amigurumi:
            raise ValueError("Amigurumi não encontrado.")

        if amigurumi.excluido_em is not None:
            raise ValueError(
                "Não é possível editar um amigurumi excluído."
            )

        amigurumi.produto = produto

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return amigurumi

    @staticmethod
    def excluir(usuario_id, amigurumi_id):
        """
        Realiza exclusão lógica do amigurumi.
        """

        amigurumi = AmigurumiService.buscar_por_id(
            usuario_id=usuario_id,
            amigurumi_id=amigurumi_id
        )

        if not amigurumi:
            raise ValueError("Amigurumi não encontrado.")

        if amigurumi.excluido_em is not None:
            raise ValueError(
                "Este amigurumi já está excluído."
            )

        from datetime import datetime

        amigurumi.excluido_em = datetime.now()

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return amigurumi

    @staticmethod
    def restaurar(usuario_id, amigurumi_id):
        """
        Restaura um amigurumi que foi excluído logicamente.
        """

        amigurumi = AmigurumiService.buscar_por_id(
            usuario_id=usuario_id,
            amigurumi_id=amigurumi_id
        )

        if not amigurumi:
            raise ValueError("Amigurumi não encontrado.")

        if amigurumi.excluido_em is None:
            raise ValueError(
                "Este amigurumi já está ativo."
            )

        amigurumi.excluido_em = None

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return amigurumi