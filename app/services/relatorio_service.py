from datetime import date
from decimal import Decimal

from sqlalchemy import func, or_

from app.extensions import db
from app.models import Pedido, ItemPedido, Cliente, Amigurumi, MovimentacaoPagamento
from app.models.enums import StatusItemPedido, StatusPagamento, TipoMovimentacaoPagamento


class RelatorioService:

    @staticmethod
    def _converter_data(data):
        if not data:
            return None

        if isinstance(data, date):
            return data

        try:
            return date.fromisoformat(data)
        except (TypeError, ValueError):
            raise ValueError("A data informada é inválida.")

    @staticmethod
    def _calcular_valor_item(item):
        return (item.preco_unitario * item.quantidade).quantize(Decimal("0.01"))

    @staticmethod
    def _calcular_pagamento(pagamento):
        recebido = Decimal("0.00")
        devolvido = Decimal("0.00")

        if pagamento:
            for movimentacao in pagamento.movimentacoes:
                if movimentacao.tipo == TipoMovimentacaoPagamento.RECEBIMENTO:
                    recebido += movimentacao.valor
                elif movimentacao.tipo == TipoMovimentacaoPagamento.DEVOLUCAO:
                    devolvido += movimentacao.valor

        recebido = recebido.quantize(Decimal("0.01"))
        devolvido = devolvido.quantize(Decimal("0.01"))
        efetivo = recebido - devolvido

        if efetivo < 0:
            efetivo = Decimal("0.00")

        return {
            "recebido": recebido,
            "devolvido": devolvido,
            "efetivo": efetivo,
        }

    @staticmethod
    def gerar(
        usuario_id,
        cliente_id=None,
        amigurumi_id=None,
        tipo=None,
        status=None,
        pagamento=None,
        data_inicial=None,
        data_final=None,
        atrasados=False,
        incluir_excluidos=False,
        situacao="ativos",
    ):
        data_inicial = RelatorioService._converter_data(data_inicial)
        data_final = RelatorioService._converter_data(data_final)

        if data_inicial and data_final and data_inicial > data_final:
            raise ValueError("A data inicial não pode ser maior que a data final.")

        consulta = (
            db.select(ItemPedido)
            .join(Pedido, ItemPedido.pedido_id == Pedido.id)
            .join(Cliente, Pedido.cliente_id == Cliente.id)
            .join(Amigurumi, ItemPedido.amigurumi_id == Amigurumi.id)
            .where(Pedido.usuario_id == usuario_id)
        )

        if cliente_id:
            consulta = consulta.where(Pedido.cliente_id == cliente_id)

        if amigurumi_id:
            consulta = consulta.where(ItemPedido.amigurumi_id == amigurumi_id)

        if tipo:
            consulta = consulta.where(ItemPedido.tipo == tipo)

        if status:
            try:
                status_enum = status if isinstance(status, StatusItemPedido) else StatusItemPedido(status)
            except (ValueError, TypeError):
                raise ValueError("O status informado é inválido.")

            consulta = consulta.where(ItemPedido.status == status_enum)

        if data_inicial:
            consulta = consulta.where(Pedido.data_pedido >= data_inicial)

        if data_final:
            consulta = consulta.where(Pedido.data_pedido <= data_final)

        if atrasados:
            hoje = date.today()

            consulta = consulta.where(
                ItemPedido.data_prevista_entrega < hoje,
                ItemPedido.status.notin_(
                    [
                        StatusItemPedido.ENTREGUE,
                        StatusItemPedido.CANCELADO,
                    ]
                ),
            )

        if situacao == "ativos":
            consulta = consulta.where(
                Cliente.excluido_em.is_(None),
                Amigurumi.excluido_em.is_(None),
            )

        elif situacao == "excluidos":
            consulta = consulta.where(
                or_(
                    Cliente.excluido_em.is_not(None),
                    Amigurumi.excluido_em.is_not(None),
                )
            )

        elif situacao == "todos":
            pass

        elif not incluir_excluidos:
            consulta = consulta.where(
                Cliente.excluido_em.is_(None),
                Amigurumi.excluido_em.is_(None),
            )

        itens = db.session.scalars(
            consulta.order_by(
                Pedido.data_pedido.desc(),
                ItemPedido.id.desc(),
            )
        ).unique().all()

        resultados = []

        for item in itens:
            pagamento_item = item.pagamento
            dados_pagamento = RelatorioService._calcular_pagamento(pagamento_item)
            valor_total = RelatorioService._calcular_valor_item(item)
            valor_restante = valor_total - dados_pagamento["efetivo"]

            if valor_restante < 0:
                valor_restante = Decimal("0.00")

            if pagamento_item:
                status_pagamento = pagamento_item.status
                pagamento_id = pagamento_item.id

                data_ultimo_pagamento = db.session.scalar(
                    db.select(
                        func.max(
                            MovimentacaoPagamento.data_movimentacao
                        )
                    ).where(
                        MovimentacaoPagamento.pagamento_id == pagamento_item.id
                    )
                )
            else:
                status_pagamento = StatusPagamento.PENDENTE
                pagamento_id = None
                data_ultimo_pagamento = None

            if status_pagamento == StatusPagamento.PAGO:
                status_pagamento_texto = "Pago"
            elif status_pagamento == StatusPagamento.PARCIAL:
                status_pagamento_texto = "Parcial"
            else:
                status_pagamento_texto = "Pendente"

            atrasado = (
                item.data_entrega is None
                and item.data_prevista_entrega < date.today()
                and item.status not in (
                    StatusItemPedido.ENTREGUE,
                    StatusItemPedido.CANCELADO,
                )
            )

            resultados.append(
                {
                    "pedido_id": item.pedido.id,
                    "pedido_nome": item.pedido.nome,
                    "data_pedido": item.pedido.data_pedido,
                    "cliente_id": item.pedido.cliente_id,
                    "cliente_nome": item.pedido.cliente_nome_snapshot,
                    "cliente_telefone": item.pedido.cliente_telefone_snapshot,
                    "amigurumi_id": item.amigurumi_id,
                    "amigurumi_nome": item.amigurumi.produto,
                    "item_id": item.id,
                    "quantidade": item.quantidade,
                    "tamanho": item.tamanho,
                    "tipo": item.tipo,
                    "preco_unitario": item.preco_unitario,
                    "valor_total": valor_total,
                    "data_prevista_entrega": item.data_prevista_entrega,
                    "data_entrega": item.data_entrega,
                    "status": item.status,
                    "status_texto": item.status.value,
                    "forma_recebimento": item.pedido.forma_recebimento,
                    "endereco_cep": item.pedido.endereco_cep,
                    "endereco_estado": item.pedido.endereco_estado,
                    "endereco_cidade": item.pedido.endereco_cidade,
                    "endereco_rua": item.pedido.endereco_rua,
                    "endereco_numero": item.pedido.endereco_numero,
                    "endereco_complemento": item.pedido.endereco_complemento,
                    "endereco_bairro": item.pedido.endereco_bairro,
                    "pagamento_id": pagamento_id,
                    "status_pagamento": status_pagamento,
                    "status_pagamento_texto": status_pagamento_texto,
                    "valor_recebido": dados_pagamento["recebido"],
                    "valor_devolvido": dados_pagamento["devolvido"],
                    "valor_efetivo": dados_pagamento["efetivo"],
                    "valor_restante": valor_restante,
                    "data_ultimo_pagamento": data_ultimo_pagamento,
                    "atrasado": atrasado,
                }
            )

        if pagamento:
            resultados = [
                resultado
                for resultado in resultados
                if (
                    resultado["status_pagamento"].value
                    if isinstance(
                        resultado["status_pagamento"],
                        StatusPagamento,
                    )
                    else str(resultado["status_pagamento"])
                ) == pagamento
            ]

        return resultados

    @staticmethod
    def calcular_totais(resultados):
        quantidade_itens = len(resultados)

        quantidade_total = sum(
            item["quantidade"]
            for item in resultados
        )

        valor_total = sum(
            (item["valor_total"] for item in resultados),
            Decimal("0.00"),
        )

        valor_recebido = sum(
            (item["valor_recebido"] for item in resultados),
            Decimal("0.00"),
        )

        valor_devolvido = sum(
            (item["valor_devolvido"] for item in resultados),
            Decimal("0.00"),
        )

        valor_restante = sum(
            (item["valor_restante"] for item in resultados),
            Decimal("0.00"),
        )

        total_pedidos = len(
            {
                item["pedido_id"]
                for item in resultados
            }
        )

        total_entregues = sum(
            1
            for item in resultados
            if item["status"] == StatusItemPedido.ENTREGUE
        )

        total_atrasados = sum(
            1
            for item in resultados
            if item["atrasado"]
        )

        valor_liquido = valor_recebido - valor_devolvido

        return {
            "total_pedidos": total_pedidos,
            "quantidade_itens": quantidade_itens,
            "quantidade_total": quantidade_total,
            "total_entregues": total_entregues,
            "total_atrasados": total_atrasados,
            "valor_total": valor_total.quantize(Decimal("0.01")),
            "valor_recebido": valor_recebido.quantize(Decimal("0.01")),
            "valor_devolvido": valor_devolvido.quantize(Decimal("0.01")),
            "valor_liquido": valor_liquido.quantize(Decimal("0.01")),
            "valor_restante": valor_restante.quantize(Decimal("0.01")),
        }