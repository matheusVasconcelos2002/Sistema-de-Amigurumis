import re
from datetime import datetime

from app.extensions import db
from app.models import Cliente


class ClienteService:

    @staticmethod
    def _validar_dados(
        nome,
        telefone,
        cep,
        estado,
        cidade,
        rua,
        numero,
        complemento,
        bairro
    ):
        """
        Valida e normaliza os dados do cliente.

        O CEP é opcional.

        Quando informado:
        - deve possuir exatamente 8 dígitos.

        Quando não informado:
        - será armazenado como NULL no banco.
        """

        nome = (nome or "").strip()

        telefone = (telefone or "").strip()

        cep = re.sub(
            r"\D",
            "",
            cep or ""
        )

        estado = (estado or "").strip().upper()

        cidade = (cidade or "").strip()

        rua = (rua or "").strip()

        numero = (numero or "").strip() or None

        complemento = (
            (complemento or "").strip()
            or None
        )

        bairro = (bairro or "").strip()


        # =====================================================
        # NOME
        # =====================================================

        if not nome:

            raise ValueError(
                "O nome do cliente é obrigatório."
            )

        if len(nome) > 150:

            raise ValueError(
                "O nome do cliente deve ter no máximo 150 caracteres."
            )


        # =====================================================
        # TELEFONE
        # =====================================================

        if not telefone:

            raise ValueError(
                "O telefone do cliente é obrigatório."
            )

        telefone_numeros = re.sub(
            r"\D",
            "",
            telefone
        )

        if len(telefone_numeros) not in (10, 11):

            raise ValueError(
                "O telefone deve possuir 10 ou 11 dígitos."
            )


        # =====================================================
        # CEP
        # =====================================================
        # O CEP agora é OPCIONAL.
        #
        # Se estiver vazio:
        #     será salvo como NULL.
        #
        # Se estiver preenchido:
        #     precisa ter 8 dígitos.
        # =====================================================

        if cep:

            if len(cep) != 8:

                raise ValueError(
                    "O CEP deve possuir 8 dígitos."
                )

        else:

            cep = None


        # =====================================================
        # ESTADO
        # =====================================================

        if len(estado) != 2:

            raise ValueError(
                "O estado deve possuir 2 caracteres."
            )


        # =====================================================
        # CIDADE
        # =====================================================

        if not cidade:

            raise ValueError(
                "A cidade é obrigatória."
            )

        if len(cidade) > 100:

            raise ValueError(
                "A cidade deve ter no máximo 100 caracteres."
            )


        # =====================================================
        # RUA
        # =====================================================

        if not rua:

            raise ValueError(
                "A rua é obrigatória."
            )

        if len(rua) > 200:

            raise ValueError(
                "A rua deve ter no máximo 200 caracteres."
            )


        # =====================================================
        # BAIRRO
        # =====================================================

        if not bairro:

            raise ValueError(
                "O bairro é obrigatório."
            )

        if len(bairro) > 100:

            raise ValueError(
                "O bairro deve ter no máximo 100 caracteres."
            )


        # =====================================================
        # NÚMERO
        # =====================================================

        if numero and len(numero) > 20:

            raise ValueError(
                "O número deve ter no máximo 20 caracteres."
            )


        # =====================================================
        # COMPLEMENTO
        # =====================================================

        if complemento and len(complemento) > 150:

            raise ValueError(
                "O complemento deve ter no máximo 150 caracteres."
            )


        # =====================================================
        # DADOS NORMALIZADOS
        # =====================================================

        return {
            "nome": nome,
            "telefone": telefone_numeros,
            "cep": cep,
            "estado": estado,
            "cidade": cidade,
            "rua": rua,
            "numero": numero,
            "complemento": complemento,
            "bairro": bairro
        }


    # =========================================================
    # CADASTRAR
    # =========================================================

    @staticmethod
    def cadastrar(
        usuario_id,
        nome,
        telefone,
        cep,
        estado,
        cidade,
        rua,
        numero=None,
        complemento=None,
        bairro=None
    ):
        """
        Cadastra um novo cliente.
        """

        dados = ClienteService._validar_dados(
            nome=nome,
            telefone=telefone,
            cep=cep,
            estado=estado,
            cidade=cidade,
            rua=rua,
            numero=numero,
            complemento=complemento,
            bairro=bairro
        )

        cliente = Cliente(
            usuario_id=usuario_id,
            **dados
        )

        try:

            db.session.add(cliente)

            db.session.commit()

        except Exception:

            db.session.rollback()

            raise

        return cliente


    # =========================================================
    # BUSCAR POR ID
    # =========================================================

    @staticmethod
    def buscar_por_id(
        usuario_id,
        cliente_id
    ):
        """
        Busca um cliente pertencente ao usuário informado.
        """

        return db.session.scalar(
            db.select(Cliente).where(
                Cliente.id == cliente_id,
                Cliente.usuario_id == usuario_id
            )
        )


    # =========================================================
    # LISTAR ATIVOS
    # =========================================================

    @staticmethod
    def listar_ativos(
        usuario_id
    ):
        """
        Retorna os clientes ativos do usuário.
        """

        return db.session.scalars(
            db.select(Cliente)
            .where(
                Cliente.usuario_id == usuario_id,
                Cliente.excluido_em.is_(None)
            )
            .order_by(
                Cliente.nome.asc()
            )
        ).all()


    # =========================================================
    # LISTAR EXCLUÍDOS
    # =========================================================

    @staticmethod
    def listar_excluidos(
        usuario_id
    ):
        """
        Retorna os clientes que estão na lixeira.
        """

        return db.session.scalars(
            db.select(Cliente)
            .where(
                Cliente.usuario_id == usuario_id,
                Cliente.excluido_em.is_not(None)
            )
            .order_by(
                Cliente.excluido_em.desc()
            )
        ).all()


    # =========================================================
    # ATUALIZAR
    # =========================================================

    @staticmethod
    def atualizar(
        usuario_id,
        cliente_id,
        nome,
        telefone,
        cep,
        estado,
        cidade,
        rua,
        numero=None,
        complemento=None,
        bairro=None
    ):
        """
        Atualiza os dados de um cliente ativo.

        O CEP continua opcional.
        """

        dados = ClienteService._validar_dados(
            nome=nome,
            telefone=telefone,
            cep=cep,
            estado=estado,
            cidade=cidade,
            rua=rua,
            numero=numero,
            complemento=complemento,
            bairro=bairro
        )

        cliente = ClienteService.buscar_por_id(
            usuario_id=usuario_id,
            cliente_id=cliente_id
        )

        if not cliente:

            raise ValueError(
                "Cliente não encontrado."
            )

        if cliente.excluido_em is not None:

            raise ValueError(
                "Não é possível editar um cliente excluído."
            )


        cliente.nome = dados["nome"]

        cliente.telefone = dados["telefone"]

        cliente.cep = dados["cep"]

        cliente.estado = dados["estado"]

        cliente.cidade = dados["cidade"]

        cliente.rua = dados["rua"]

        cliente.numero = dados["numero"]

        cliente.complemento = dados["complemento"]

        cliente.bairro = dados["bairro"]

        cliente.atualizado_em = datetime.now()


        try:

            db.session.commit()

        except Exception:

            db.session.rollback()

            raise

        return cliente


    # =========================================================
    # EXCLUIR
    # =========================================================

    @staticmethod
    def excluir(
        usuario_id,
        cliente_id
    ):
        """
        Realiza a exclusão lógica do cliente.
        """

        cliente = ClienteService.buscar_por_id(
            usuario_id=usuario_id,
            cliente_id=cliente_id
        )

        if not cliente:

            raise ValueError(
                "Cliente não encontrado."
            )

        if cliente.excluido_em is not None:

            raise ValueError(
                "Este cliente já está excluído."
            )

        cliente.excluido_em = datetime.now()


        try:

            db.session.commit()

        except Exception:

            db.session.rollback()

            raise

        return cliente


    # =========================================================
    # RESTAURAR
    # =========================================================

    @staticmethod
    def restaurar(
        usuario_id,
        cliente_id
    ):
        """
        Restaura um cliente que está na lixeira.
        """

        cliente = ClienteService.buscar_por_id(
            usuario_id=usuario_id,
            cliente_id=cliente_id
        )

        if not cliente:

            raise ValueError(
                "Cliente não encontrado."
            )

        if cliente.excluido_em is None:

            raise ValueError(
                "Este cliente já está ativo."
            )

        cliente.excluido_em = None

        cliente.atualizado_em = datetime.now()


        try:

            db.session.commit()

        except Exception:

            db.session.rollback()

            raise

        return cliente