from datetime import date, datetime, timezone
from decimal import Decimal

from app.extensions import db
from app.models import (
    Pedido,
    ItemPedido,
    Cliente,
    Amigurumi,
)
from app.models.enums import (
    FormaRecebimento,
    StatusItemPedido,
)
from app.services.pagamento_service import PagamentoService


class PedidoService:
    """
    Regras de negócio relacionadas a pedidos e itens de pedidos.

    Regras principais:
    - Um pedido pode possuir vários itens.
    - Cada item possui quantidade, tamanho, tipo, preço e prazo próprios.
    - O endereço do pedido é um snapshot histórico.
    - Retirada usa o endereço fixo do CESIT/UEA.
    - Cancelamento definitivo do pedido é transacional.
    - Se houver pagamentos, o cancelamento permite devolver ou não o valor.
    - Um pedido com item já entregue não pode ser fisicamente excluído.
    """

    # =========================================================
    # ENDEREÇO FIXO PARA RETIRADA
    # =========================================================

    RETIRADA_COMPLEMENTO = "CESIT-UEA, ao lado do CETAM"
    RETIRADA_CIDADE = "Itacoatiara"
    RETIRADA_ESTADO = "AM"
    RETIRADA_RUA = "Avenida Mário Andreazza"
    RETIRADA_BAIRRO = "Jardim Florestal"
    RETIRADA_NUMERO = "2960"
    RETIRADA_CEP = None

    # =========================================================
    # VALIDAÇÕES
    # =========================================================

    @staticmethod
    def _validar_data_pedido(data_pedido):
        """Valida a data do pedido."""

        if (
            not isinstance(data_pedido, date)
            or isinstance(data_pedido, datetime)
        ):
            raise ValueError(
                "A data do pedido é inválida."
            )

        return data_pedido

    @staticmethod
    def _validar_nome(nome):
        """Valida o nome do pedido."""

        nome = (nome or "").strip()

        if not nome:
            raise ValueError(
                "O nome do pedido é obrigatório."
            )

        if len(nome) > 200:
            raise ValueError(
                "O nome do pedido deve ter no máximo 200 caracteres."
            )

        return nome

    @staticmethod
    def _buscar_cliente(usuario_id, cliente_id):
        """Busca um cliente ativo pertencente ao usuário."""

        cliente = db.session.scalar(
            db.select(Cliente).where(
                Cliente.id == cliente_id,
                Cliente.usuario_id == usuario_id,
                Cliente.excluido_em.is_(None),
            )
        )

        if not cliente:
            raise ValueError(
                "Cliente não encontrado."
            )

        return cliente

    @staticmethod
    def _buscar_amigurumi(usuario_id, amigurumi_id):
        """Busca um amigurumi ativo pertencente ao usuário."""

        amigurumi = db.session.scalar(
            db.select(Amigurumi).where(
                Amigurumi.id == amigurumi_id,
                Amigurumi.usuario_id == usuario_id,
                Amigurumi.excluido_em.is_(None),
            )
        )

        if not amigurumi:
            raise ValueError(
                "Amigurumi não encontrado."
            )

        return amigurumi

    @staticmethod
    def _validar_forma_recebimento(forma_recebimento):
        """Converte e valida a forma de recebimento."""

        if isinstance(
            forma_recebimento,
            FormaRecebimento,
        ):
            return forma_recebimento

        try:
            return FormaRecebimento(
                forma_recebimento
            )

        except (
            ValueError,
            TypeError,
        ):
            raise ValueError(
                "A forma de recebimento informada é inválida."
            )

    @staticmethod
    def _validar_devolver_pagamentos(
        devolver_pagamentos
    ):
        """Aceita booleano ou valores comuns enviados por formulário."""

        if isinstance(
            devolver_pagamentos,
            bool,
        ):
            return devolver_pagamentos

        if isinstance(
            devolver_pagamentos,
            str,
        ):
            valor = (
                devolver_pagamentos
                .strip()
                .lower()
            )

            if valor in {
                "sim",
                "s",
                "true",
                "1",
                "on",
                "devolver",
            }:
                return True

            if valor in {
                "não",
                "nao",
                "n",
                "false",
                "0",
                "off",
                "nao_devolver",
            }:
                return False

        raise ValueError(
            "A opção de devolução informada é inválida."
        )

    @staticmethod
    def _validar_item(
        quantidade,
        tamanho,
        tipo,
        preco_unitario,
        data_pedido,
        data_prevista_entrega,
    ):
        """Valida os dados de um item do pedido."""

        try:
            quantidade = int(
                quantidade
            )

        except (
            TypeError,
            ValueError,
        ):
            raise ValueError(
                "A quantidade deve ser um número inteiro."
            )

        if quantidade <= 0:
            raise ValueError(
                "A quantidade deve ser maior que zero."
            )

        try:
            tamanho = Decimal(
                str(tamanho)
            ).quantize(
                Decimal("0.01")
            )

        except (
            TypeError,
            ValueError,
        ):
            raise ValueError(
                "O tamanho informado é inválido."
            )

        if tamanho <= 0:
            raise ValueError(
                "O tamanho deve ser maior que zero."
            )

        tipo = (tipo or "").strip()

        if not tipo:
            raise ValueError(
                "O tipo do amigurumi é obrigatório."
            )

        if len(tipo) > 100:
            raise ValueError(
                "O tipo deve ter no máximo 100 caracteres."
            )

        try:
            preco_unitario = Decimal(
                str(preco_unitario)
            ).quantize(
                Decimal("0.01")
            )

        except (
            TypeError,
            ValueError,
        ):
            raise ValueError(
                "O preço unitário informado é inválido."
            )

        if preco_unitario <= 0:
            raise ValueError(
                "O preço unitário deve ser maior que zero."
            )

        if (
            not isinstance(
                data_prevista_entrega,
                date,
            )
            or isinstance(
                data_prevista_entrega,
                datetime,
            )
        ):
            raise ValueError(
                "A data prevista de entrega é inválida."
            )

        if data_prevista_entrega < data_pedido:
            raise ValueError(
                "A data prevista de entrega não pode ser anterior à data do pedido."
            )

        return {
            "quantidade": quantidade,
            "tamanho": tamanho,
            "tipo": tipo,
            "preco_unitario": preco_unitario,
            "data_prevista_entrega": data_prevista_entrega,
        }

    # =========================================================
    # ENDEREÇO HISTÓRICO
    # =========================================================

    @staticmethod
    def _aplicar_endereco_por_forma(
        pedido,
        cliente,
        forma_recebimento,
    ):
        """
        Preenche o endereço histórico do pedido
        conforme a forma de recebimento.
        """

        if (
            forma_recebimento
            == FormaRecebimento.ENTREGA
        ):
            pedido.endereco_cep = cliente.cep
            pedido.endereco_estado = cliente.estado
            pedido.endereco_cidade = cliente.cidade
            pedido.endereco_rua = cliente.rua
            pedido.endereco_numero = cliente.numero
            pedido.endereco_complemento = (
                cliente.complemento
            )
            pedido.endereco_bairro = cliente.bairro

            return

        if (
            forma_recebimento
            == FormaRecebimento.RETIRADA
        ):
            pedido.endereco_cep = (
                PedidoService.RETIRADA_CEP
            )
            pedido.endereco_estado = (
                PedidoService.RETIRADA_ESTADO
            )
            pedido.endereco_cidade = (
                PedidoService.RETIRADA_CIDADE
            )
            pedido.endereco_rua = (
                PedidoService.RETIRADA_RUA
            )
            pedido.endereco_numero = (
                PedidoService.RETIRADA_NUMERO
            )
            pedido.endereco_complemento = (
                PedidoService.RETIRADA_COMPLEMENTO
            )
            pedido.endereco_bairro = (
                PedidoService.RETIRADA_BAIRRO
            )

            return

        # A definir
        pedido.endereco_cep = None
        pedido.endereco_estado = None
        pedido.endereco_cidade = None
        pedido.endereco_rua = None
        pedido.endereco_numero = None
        pedido.endereco_complemento = None
        pedido.endereco_bairro = None

    # =========================================================
    # CRIAR PEDIDO
    # =========================================================

    @staticmethod
    def criar_pedido(
        usuario_id,
        cliente_id,
        nome,
        data_pedido,
        forma_recebimento,
        itens,
    ):
        """Cria um pedido com um ou vários itens."""

        nome = PedidoService._validar_nome(
            nome
        )

        data_pedido = (
            PedidoService._validar_data_pedido(
                data_pedido
            )
        )

        forma_recebimento = (
            PedidoService._validar_forma_recebimento(
                forma_recebimento
            )
        )

        if (
            not isinstance(
                itens,
                (list, tuple),
            )
            or not itens
        ):
            raise ValueError(
                "O pedido deve possuir pelo menos um item."
            )

        cliente = PedidoService._buscar_cliente(
            usuario_id,
            cliente_id,
        )

        pedido = Pedido(
            usuario_id=usuario_id,
            cliente_id=cliente.id,
            nome=nome,
            data_pedido=data_pedido,
            forma_recebimento=forma_recebimento,
            cliente_nome_snapshot=cliente.nome,
            cliente_telefone_snapshot=cliente.telefone,
        )

        PedidoService._aplicar_endereco_por_forma(
            pedido,
            cliente,
            forma_recebimento,
        )

        try:
            db.session.add(
                pedido
            )

            db.session.flush()

            for dados_item in itens:

                if not isinstance(
                    dados_item,
                    dict,
                ):
                    raise ValueError(
                        "Os dados de cada item devem ser informados em um dicionário."
                    )

                amigurumi = (
                    PedidoService._buscar_amigurumi(
                        usuario_id=usuario_id,
                        amigurumi_id=dados_item[
                            "amigurumi_id"
                        ],
                    )
                )

                dados_validados = (
                    PedidoService._validar_item(
                        quantidade=dados_item[
                            "quantidade"
                        ],
                        tamanho=dados_item[
                            "tamanho"
                        ],
                        tipo=dados_item[
                            "tipo"
                        ],
                        preco_unitario=dados_item[
                            "preco_unitario"
                        ],
                        data_pedido=data_pedido,
                        data_prevista_entrega=dados_item[
                            "data_prevista_entrega"
                        ],
                    )
                )

                item = ItemPedido(
                    pedido_id=pedido.id,
                    amigurumi_id=amigurumi.id,
                    **dados_validados,
                )

                db.session.add(item)

                db.session.flush()

                PagamentoService.criar_para_item(
                    usuario_id=usuario_id,
                    item_pedido_id=item.id,
                    commit=False,
                )

            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return pedido

    # =========================================================
    # BUSCAR PEDIDO
    # =========================================================

    @staticmethod
    def buscar_por_id(
        usuario_id,
        pedido_id,
    ):
        """Busca um pedido pertencente ao usuário."""

        return db.session.scalar(
            db.select(Pedido).where(
                Pedido.id == pedido_id,
                Pedido.usuario_id == usuario_id,
            )
        )

    # =========================================================
    # LISTAR PEDIDOS
    # =========================================================

    @staticmethod
    def listar_pedidos(
        usuario_id
    ):
        """Lista os pedidos do usuário."""

        return db.session.scalars(
            db.select(Pedido)
            .where(
                Pedido.usuario_id == usuario_id
            )
            .order_by(
                Pedido.data_pedido.desc(),
                Pedido.id.desc(),
            )
        ).all()

    # =========================================================
    # BUSCAR ITEM
    # =========================================================

    @staticmethod
    def buscar_item(
        usuario_id,
        item_pedido_id,
    ):
        """Busca um item pertencente a um pedido do usuário."""

        return db.session.scalar(
            db.select(ItemPedido)
            .join(
                Pedido,
                ItemPedido.pedido_id
                == Pedido.id,
            )
            .where(
                ItemPedido.id
                == item_pedido_id,
                Pedido.usuario_id
                == usuario_id,
            )
        )

    # =========================================================
    # ATUALIZAR PEDIDO + ITENS
    # =========================================================

    @staticmethod
    def atualizar_pedido(
        usuario_id,
        pedido_id,
        cliente_id,
        nome,
        data_pedido,
        forma_recebimento,
        itens,
    ):
        """
        Atualiza os dados principais do pedido e seus itens
        em uma única transação.

        Se qualquer validação falhar, nenhuma alteração
        é confirmada no banco.
        """

        pedido = PedidoService.buscar_por_id(
            usuario_id=usuario_id,
            pedido_id=pedido_id,
        )

        if not pedido:
            raise ValueError(
                "Pedido não encontrado."
            )

        nome = PedidoService._validar_nome(
            nome
        )

        data_pedido = (
            PedidoService._validar_data_pedido(
                data_pedido
            )
        )

        forma_recebimento = (
            PedidoService._validar_forma_recebimento(
                forma_recebimento
            )
        )

        if not itens:
            raise ValueError(
                "O pedido deve possuir pelo menos um item."
            )

        cliente = PedidoService._buscar_cliente(
            usuario_id,
            cliente_id,
        )

        if len(itens) != len(
            pedido.itens
        ):
            raise ValueError(
                "A quantidade de itens enviados não corresponde aos itens da encomenda."
            )

        itens_pedido = {
            item.id: item
            for item in pedido.itens
        }

        itens_recebidos = set()

        try:
            # -------------------------------------------------
            # ATUALIZAR DADOS PRINCIPAIS
            # -------------------------------------------------

            pedido.nome = nome
            pedido.cliente_id = cliente.id
            pedido.data_pedido = data_pedido
            pedido.forma_recebimento = (
                forma_recebimento
            )

            # Atualiza os snapshots do cliente.
            pedido.cliente_nome_snapshot = (
                cliente.nome
            )

            pedido.cliente_telefone_snapshot = (
                cliente.telefone
            )

            # Atualiza o endereço histórico conforme
            # a nova forma de recebimento.
            PedidoService._aplicar_endereco_por_forma(
                pedido,
                cliente,
                forma_recebimento,
            )

            # -------------------------------------------------
            # ATUALIZAR ITENS
            # -------------------------------------------------

            for dados_item in itens:

                item_id = int(
                    dados_item["item_id"]
                )

                if item_id in itens_recebidos:
                    raise ValueError(
                        "Um mesmo item foi enviado mais de uma vez."
                    )

                item = itens_pedido.get(
                    item_id
                )

                if not item:
                    raise ValueError(
                        "Item do pedido não encontrado."
                    )

                itens_recebidos.add(
                    item_id
                )

                if item.status in (
                    StatusItemPedido.ENTREGUE,
                    StatusItemPedido.CANCELADO,
                ):
                    raise ValueError(
                        "Não é possível editar um item entregue ou cancelado."
                    )

                amigurumi = (
                    PedidoService._buscar_amigurumi(
                        usuario_id=usuario_id,
                        amigurumi_id=int(
                            dados_item[
                                "amigurumi_id"
                            ]
                        ),
                    )
                )

                dados_validados = (
                    PedidoService._validar_item(
                        quantidade=dados_item[
                            "quantidade"
                        ],
                        tamanho=dados_item[
                            "tamanho"
                        ],
                        tipo=dados_item[
                            "tipo"
                        ],
                        preco_unitario=dados_item[
                            "preco_unitario"
                        ],
                        data_pedido=data_pedido,
                        data_prevista_entrega=dados_item[
                            "data_prevista_entrega"
                        ],
                    )
                )

                item.amigurumi_id = (
                    amigurumi.id
                )

                item.quantidade = (
                    dados_validados[
                        "quantidade"
                    ]
                )

                item.tamanho = (
                    dados_validados[
                        "tamanho"
                    ]
                )

                item.tipo = (
                    dados_validados[
                        "tipo"
                    ]
                )

                item.preco_unitario = (
                    dados_validados[
                        "preco_unitario"
                    ]
                )

                item.data_prevista_entrega = (
                    dados_validados[
                        "data_prevista_entrega"
                    ]
                )

            # -------------------------------------------------
            # GARANTIR QUE TODOS OS ITENS FORAM ENVIADOS
            # -------------------------------------------------

            if itens_recebidos != set(
                itens_pedido.keys()
            ):
                raise ValueError(
                    "Nem todos os itens da encomenda foram enviados."
                )

            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return pedido

    # =========================================================
    # ADICIONAR ITEM
    # =========================================================

    @staticmethod
    def adicionar_item(
        usuario_id,
        pedido_id,
        amigurumi_id,
        quantidade,
        tamanho,
        tipo,
        preco_unitario,
        data_prevista_entrega,
    ):
        """Adiciona outro amigurumi a um pedido existente."""

        pedido = PedidoService.buscar_por_id(
            usuario_id,
            pedido_id,
        )

        if not pedido:
            raise ValueError(
                "Pedido não encontrado."
            )

        if any(
            item.status
            == StatusItemPedido.ENTREGUE
            for item in pedido.itens
        ):
            raise ValueError(
                "Não é possível adicionar itens a um pedido que já possui item entregue."
            )

        if (
            pedido.itens
            and all(
                item.status
                == StatusItemPedido.CANCELADO
                for item in pedido.itens
            )
        ):
            raise ValueError(
                "Não é possível adicionar itens a um pedido cancelado."
            )

        amigurumi = (
            PedidoService._buscar_amigurumi(
                usuario_id,
                amigurumi_id,
            )
        )

        dados_validados = (
            PedidoService._validar_item(
                quantidade=quantidade,
                tamanho=tamanho,
                tipo=tipo,
                preco_unitario=preco_unitario,
                data_pedido=pedido.data_pedido,
                data_prevista_entrega=data_prevista_entrega,
            )
        )

        item = ItemPedido(
            pedido_id=pedido.id,
            amigurumi_id=amigurumi.id,
            **dados_validados,
        )

        try:
            db.session.add(item)

            db.session.flush()

            PagamentoService.criar_para_item(
                usuario_id=usuario_id,
                item_pedido_id=item.id,
                commit=False,
            )

            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return item

    # =========================================================
    # ATUALIZAR ITEM INDIVIDUAL
    # =========================================================

    @staticmethod
    def atualizar_item(
        usuario_id,
        item_pedido_id,
        amigurumi_id,
        quantidade,
        tamanho,
        tipo,
        preco_unitario,
        data_prevista_entrega,
    ):
        """Atualiza um item existente do pedido."""

        item = PedidoService.buscar_item(
            usuario_id,
            item_pedido_id,
        )

        if not item:
            raise ValueError(
                "Item do pedido não encontrado."
            )

        if item.status in (
            StatusItemPedido.ENTREGUE,
            StatusItemPedido.CANCELADO,
        ):
            raise ValueError(
                "Não é possível editar um item entregue ou cancelado."
            )

        amigurumi = (
            PedidoService._buscar_amigurumi(
                usuario_id,
                amigurumi_id,
            )
        )

        dados_validados = (
            PedidoService._validar_item(
                quantidade=quantidade,
                tamanho=tamanho,
                tipo=tipo,
                preco_unitario=preco_unitario,
                data_pedido=item.pedido.data_pedido,
                data_prevista_entrega=data_prevista_entrega,
            )
        )

        item.amigurumi_id = (
            amigurumi.id
        )

        item.quantidade = (
            dados_validados["quantidade"]
        )

        item.tamanho = (
            dados_validados["tamanho"]
        )

        item.tipo = (
            dados_validados["tipo"]
        )

        item.preco_unitario = (
            dados_validados[
                "preco_unitario"
            ]
        )

        item.data_prevista_entrega = (
            dados_validados[
                "data_prevista_entrega"
            ]
        )

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return item

    # =========================================================
    # ALTERAR FORMA DE RECEBIMENTO
    # =========================================================

    @staticmethod
    def alterar_forma_recebimento(
        usuario_id,
        pedido_id,
        forma_recebimento,
    ):
        """
        Altera a forma de recebimento e atualiza
        o endereço histórico do pedido.
        """

        pedido = PedidoService.buscar_por_id(
            usuario_id,
            pedido_id,
        )

        if not pedido:
            raise ValueError(
                "Pedido não encontrado."
            )

        forma_recebimento = (
            PedidoService._validar_forma_recebimento(
                forma_recebimento
            )
        )

        if (
            forma_recebimento
            == pedido.forma_recebimento
        ):
            raise ValueError(
                "O pedido já está nessa forma de recebimento."
            )

        cliente = PedidoService._buscar_cliente(
            usuario_id,
            pedido.cliente_id,
        )

        pedido.forma_recebimento = (
            forma_recebimento
        )

        PedidoService._aplicar_endereco_por_forma(
            pedido,
            cliente,
            forma_recebimento,
        )

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return pedido

    # =========================================================
    # ALTERAR STATUS
    # =========================================================

    @staticmethod
    def alterar_status(
        usuario_id,
        item_pedido_id,
        novo_status,
    ):
        """
        Altera somente os status normais de produção.

        CANCELADO não pode ser definido por este método.
        """

        item = PedidoService.buscar_item(
            usuario_id,
            item_pedido_id,
        )

        if not item:
            raise ValueError(
                "Item do pedido não encontrado."
            )

        if isinstance(
            novo_status,
            StatusItemPedido,
        ):
            status = novo_status

        else:
            try:
                status = StatusItemPedido(
                    novo_status
                )

            except (
                ValueError,
                TypeError,
            ):
                raise ValueError(
                    "O status informado é inválido."
                )

        if (
            status
            == StatusItemPedido.CANCELADO
        ):
            raise ValueError(
                "O cancelamento deve ser feito pelo fluxo de cancelamento, com a escolha sobre devolução do pagamento."
            )

        status_anterior = item.status

        fluxo_permitido = {
            StatusItemPedido.A_FAZER: [
                StatusItemPedido.SENDO_FEITO
            ],
            StatusItemPedido.SENDO_FEITO: [
                StatusItemPedido.FINALIZADO
            ],
            StatusItemPedido.FINALIZADO: [
                StatusItemPedido.ENTREGUE
            ],
            StatusItemPedido.ENTREGUE: [],
            StatusItemPedido.CANCELADO: [],
        }

        if status == status_anterior:
            raise ValueError(
                "O item já está nesse status."
            )

        if status not in fluxo_permitido[
            status_anterior
        ]:
            raise ValueError(
                "Não é possível alterar o item diretamente "
                f"de '{status_anterior.value}' "
                f"para '{status.value}'."
            )

        if (
            status
            == StatusItemPedido.ENTREGUE
        ):
            if (
                date.today()
                < item.pedido.data_pedido
            ):
                raise ValueError(
                    "A data de entrega não pode ser anterior à data do pedido."
                )

            item.data_entrega = (
                datetime.now(timezone.utc)
            )

        try:
            item.status = status
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return item

    # =========================================================
    # FINALIZAR ITEM
    # =========================================================

    @staticmethod
    def finalizar_item(
        usuario_id,
        item_pedido_id,
    ):
        """Marca o item como finalizado."""

        return PedidoService.alterar_status(
            usuario_id=usuario_id,
            item_pedido_id=item_pedido_id,
            novo_status=StatusItemPedido.FINALIZADO,
        )

    # =========================================================
    # ENTREGAR ITEM
    # =========================================================

    @staticmethod
    def entregar_item(
        usuario_id,
        item_pedido_id,
    ):
        """Marca o item como entregue."""

        return PedidoService.alterar_status(
            usuario_id=usuario_id,
            item_pedido_id=item_pedido_id,
            novo_status=StatusItemPedido.ENTREGUE,
        )

    # =========================================================
    # CANCELAMENTO INTERNO
    # =========================================================

    @staticmethod
    def _cancelar_item_sem_commit(
        item,
        motivo_cancelamento,
    ):
        """Aplica o cancelamento sem abrir nova transação."""

        item.status = (
            StatusItemPedido.CANCELADO
        )

        item.motivo_cancelamento = (
            motivo_cancelamento
        )

        item.data_entrega = None

    # =========================================================
    # CANCELAR ITEM
    # =========================================================

    @staticmethod
    def cancelar_item(
        usuario_id,
        item_pedido_id,
        motivo_cancelamento,
        devolver_pagamento=False,
    ):
        """
        Cancela somente um item.
        """

        motivo_cancelamento = (
            motivo_cancelamento or ""
        ).strip()

        if not motivo_cancelamento:
            raise ValueError(
                "O motivo do cancelamento é obrigatório."
            )

        devolver_pagamento = (
            PedidoService._validar_devolver_pagamentos(
                devolver_pagamento
            )
        )

        item = PedidoService.buscar_item(
            usuario_id,
            item_pedido_id,
        )

        if not item:
            raise ValueError(
                "Item do pedido não encontrado."
            )

        if item.status in (
            StatusItemPedido.ENTREGUE,
            StatusItemPedido.CANCELADO,
        ):
            raise ValueError(
                "Este item não pode ser cancelado."
            )

        todos_cancelados = False
        valor_devolucao = Decimal(
            "0.00"
        )

        try:
            pagamento = getattr(
                item,
                "pagamento",
                None,
            )

            if (
                devolver_pagamento
                and pagamento
            ):
                valor_devolucao = (
                    PagamentoService.calcular_total_recebido(
                        usuario_id=usuario_id,
                        pagamento_id=pagamento.id,
                    )
                )

                if valor_devolucao > 0:
                    PagamentoService.registrar_devolucao(
                        usuario_id=usuario_id,
                        pagamento_id=pagamento.id,
                        valor=valor_devolucao,
                        data_movimentacao=datetime.now(
                            timezone.utc
                        ),
                        observacao=(
                            f"Devolução pelo cancelamento "
                            f"do item {item.id} "
                            f"do pedido {item.pedido_id}."
                        ),
                        commit=False,
                    )

            PedidoService._cancelar_item_sem_commit(
                item,
                motivo_cancelamento,
            )

            pedido = item.pedido

            todos_cancelados = all(
                outro_item.status
                == StatusItemPedido.CANCELADO
                for outro_item in pedido.itens
            )

            if todos_cancelados:
                db.session.delete(
                    pedido
                )

            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return {
            "item": item,
            "pedido_excluido": todos_cancelados,
            "valor_devolvido": valor_devolucao,
        }

    # =========================================================
    # CANCELAR PEDIDO
    # =========================================================

    @staticmethod
    def cancelar_pedido(
        usuario_id,
        pedido_id,
        motivo_cancelamento,
        devolver_pagamentos,
    ):
        """
        Cancela definitivamente um pedido.
        """

        motivo_cancelamento = (
            motivo_cancelamento or ""
        ).strip()

        if not motivo_cancelamento:
            raise ValueError(
                "O motivo do cancelamento é obrigatório."
            )

        devolver_pagamentos = (
            PedidoService._validar_devolver_pagamentos(
                devolver_pagamentos
            )
        )

        pedido = PedidoService.buscar_por_id(
            usuario_id,
            pedido_id,
        )

        if not pedido:
            raise ValueError(
                "Pedido não encontrado."
            )

        if not pedido.itens:
            raise ValueError(
                "O pedido não possui itens."
            )

        if any(
            item.status
            == StatusItemPedido.ENTREGUE
            for item in pedido.itens
        ):
            raise ValueError(
                "Não é possível cancelar fisicamente um pedido que possui item já entregue. Cancele somente os itens ainda não entregues."
            )

        pagamentos_para_devolver = []
        valor_total_devolucao = Decimal(
            "0.00"
        )

        try:
            if devolver_pagamentos:
                agora = datetime.now(
                    timezone.utc
                )

                for item in pedido.itens:

                    pagamento = getattr(
                        item,
                        "pagamento",
                        None,
                    )

                    if not pagamento:
                        continue

                    valor = (
                        PagamentoService.calcular_total_recebido(
                            usuario_id=usuario_id,
                            pagamento_id=pagamento.id,
                        )
                    )

                    if valor <= 0:
                        continue

                    pagamentos_para_devolver.append(
                        (
                            pagamento.id,
                            valor,
                        )
                    )

                    valor_total_devolucao += (
                        valor
                    )

                for (
                    pagamento_id,
                    valor,
                ) in pagamentos_para_devolver:

                    PagamentoService.registrar_devolucao(
                        usuario_id=usuario_id,
                        pagamento_id=pagamento_id,
                        valor=valor,
                        data_movimentacao=agora,
                        observacao=(
                            f"Devolução pelo cancelamento "
                            f"do pedido {pedido.id}."
                        ),
                        commit=False,
                    )

            for item in pedido.itens:

                if (
                    item.status
                    != StatusItemPedido.CANCELADO
                ):
                    PedidoService._cancelar_item_sem_commit(
                        item,
                        motivo_cancelamento,
                    )

            itens_cancelados = len(
                pedido.itens
            )

            db.session.delete(
                pedido
            )

            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return {
            "pedido_id": pedido_id,
            "pedido_excluido": True,
            "devolucao_solicitada": (
                devolver_pagamentos
            ),
            "valor_devolvido": (
                valor_total_devolucao.quantize(
                    Decimal("0.01")
                )
            ),
            "itens_cancelados": (
                itens_cancelados
            ),
        }