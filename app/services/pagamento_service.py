from datetime import datetime, timezone
from decimal import Decimal

from app.extensions import db
from app.models import (
    Pagamento,
    MovimentacaoPagamento,
    ItemPedido,
)
from app.models.enums import (
    TipoMovimentacaoPagamento,
    StatusPagamento,
)


class PagamentoService:

    @staticmethod
    def _converter_valor(valor):
        """
        Converte o valor informado para Decimal.
        """

        try:
            valor = Decimal(str(valor))
        except Exception:
            raise ValueError("O valor informado é inválido.")

        if valor <= 0:
            raise ValueError("O valor deve ser maior que zero.")

        return valor.quantize(Decimal("0.01"))

    @staticmethod
    def _buscar_pagamento(usuario_id, pagamento_id):
        """
        Busca um pagamento pertencente ao usuário.
        """

        return db.session.scalar(
            db.select(Pagamento)
            .join(
                ItemPedido,
                Pagamento.item_pedido_id == ItemPedido.id
            )
            .where(
                Pagamento.id == pagamento_id,
                ItemPedido.pedido.has(
                    usuario_id=usuario_id
                )
            )
        )

    @staticmethod
    def buscar_por_item(usuario_id, item_pedido_id):
        """
        Busca o pagamento de um item pertencente ao usuário.
        """

        return db.session.scalar(
            db.select(Pagamento)
            .join(
                ItemPedido,
                Pagamento.item_pedido_id == ItemPedido.id
            )
            .where(
                Pagamento.item_pedido_id == item_pedido_id,
                ItemPedido.pedido.has(
                    usuario_id=usuario_id
                )
            )
        )

    @staticmethod
    def criar_para_item(
        usuario_id,
        item_pedido_id,
        commit=True,
    ):
        """
        Cria o controle de pagamento para um item.

        Cada item possui apenas um registro de pagamento.

        commit=True:
            Salva imediatamente no banco.

        commit=False:
            Apenas adiciona o pagamento à transação atual.
            O Service responsável fará o commit.
        """

        item = db.session.scalar(
            db.select(ItemPedido)
            .where(
                ItemPedido.id == item_pedido_id,
                ItemPedido.pedido.has(
                    usuario_id=usuario_id
                )
            )
        )

        if not item:
            raise ValueError(
                "Item do pedido não encontrado."
            )

        pagamento_existente = db.session.scalar(
            db.select(Pagamento)
            .where(
                Pagamento.item_pedido_id
                == item_pedido_id
            )
        )

        if pagamento_existente:
            return pagamento_existente

        pagamento = Pagamento(
            item_pedido_id=item_pedido_id
        )

        try:
            db.session.add(pagamento)

            if commit:
                db.session.commit()
            else:
                db.session.flush()

        except Exception:
            if commit:
                db.session.rollback()

            raise

        return pagamento

    @staticmethod
    def listar_movimentacoes(usuario_id, pagamento_id):
        """
        Lista todas as movimentações de um pagamento.
        """

        pagamento = PagamentoService._buscar_pagamento(
            usuario_id=usuario_id,
            pagamento_id=pagamento_id
        )

        if not pagamento:
            raise ValueError("Pagamento não encontrado.")

        return db.session.scalars(
            db.select(MovimentacaoPagamento)
            .where(
                MovimentacaoPagamento.pagamento_id == pagamento_id
            )
            .order_by(
                MovimentacaoPagamento.data_movimentacao.asc()
            )
        ).all()

    @staticmethod
    def calcular_total_recebido(usuario_id, pagamento_id):
        """
        Calcula o total efetivamente recebido.

        Recebimentos somam.
        Devoluções subtraem.
        """

        movimentacoes = PagamentoService.listar_movimentacoes(
            usuario_id=usuario_id,
            pagamento_id=pagamento_id
        )

        total_recebido = Decimal("0.00")

        for movimentacao in movimentacoes:

            if (
                movimentacao.tipo
                == TipoMovimentacaoPagamento.RECEBIMENTO
            ):
                total_recebido += movimentacao.valor

            elif (
                movimentacao.tipo
                == TipoMovimentacaoPagamento.DEVOLUCAO
            ):
                total_recebido -= movimentacao.valor

        return total_recebido.quantize(
            Decimal("0.01")
        )

    @staticmethod
    def calcular_total_devolvido(usuario_id, pagamento_id):
        """
        Calcula o total devolvido ao cliente.
        """

        movimentacoes = PagamentoService.listar_movimentacoes(
            usuario_id=usuario_id,
            pagamento_id=pagamento_id
        )

        total_devolvido = Decimal("0.00")

        for movimentacao in movimentacoes:

            if (
                movimentacao.tipo
                == TipoMovimentacaoPagamento.DEVOLUCAO
            ):
                total_devolvido += movimentacao.valor

        return total_devolvido.quantize(
            Decimal("0.01")
        )

    @staticmethod
    def calcular_valor_total_item(item):
        """
        Calcula o valor total do item.

        Total = preço unitário × quantidade.
        """

        return (
            item.preco_unitario * item.quantidade
        ).quantize(
            Decimal("0.01")
        )

    @staticmethod
    def calcular_valor_restante(
        usuario_id,
        pagamento_id
    ):
        """
        Calcula quanto ainda falta receber do item.
        """

        pagamento = PagamentoService._buscar_pagamento(
            usuario_id=usuario_id,
            pagamento_id=pagamento_id
        )

        if not pagamento:
            raise ValueError("Pagamento não encontrado.")

        total_item = PagamentoService.calcular_valor_total_item(
            pagamento.item_pedido
        )

        total_recebido = PagamentoService.calcular_total_recebido(
            usuario_id=usuario_id,
            pagamento_id=pagamento_id
        )

        restante = total_item - total_recebido

        if restante < 0:
            restante = Decimal("0.00")

        return restante.quantize(
            Decimal("0.01")
        )

    @staticmethod
    def registrar_recebimento(
        usuario_id,
        pagamento_id,
        valor,
        data_movimentacao=None,
        observacao=None
    ):
        """
        Registra um recebimento.

        Cada recebimento fica registrado como uma
        movimentação separada.
        """

        valor = PagamentoService._converter_valor(valor)

        pagamento = PagamentoService._buscar_pagamento(
            usuario_id=usuario_id,
            pagamento_id=pagamento_id
        )

        if not pagamento:
            raise ValueError("Pagamento não encontrado.")

        valor_restante = PagamentoService.calcular_valor_restante(
            usuario_id=usuario_id,
            pagamento_id=pagamento_id
        )

        if valor > valor_restante:
            raise ValueError(
                "O valor recebido não pode ser maior "
                "que o valor restante."
            )

        if data_movimentacao is None:
            data_movimentacao = datetime.now(timezone.utc)

        movimentacao = MovimentacaoPagamento(
            pagamento_id=pagamento.id,
            tipo=TipoMovimentacaoPagamento.RECEBIMENTO,
            valor=valor,
            data_movimentacao=data_movimentacao,
            observacao=(
                observacao.strip()
                if observacao
                else None
            )
        )

        try:
            db.session.add(movimentacao)
            db.session.flush()

            PagamentoService._atualizar_status(
                pagamento
            )

            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return movimentacao

    @staticmethod
    def registrar_devolucao(
        usuario_id,
        pagamento_id,
        valor,
        data_movimentacao=None,
        observacao=None,
        commit=True
    ):
        """
        Registra uma devolução parcial ou total.

        `commit=False` permite que outro Service participe da mesma
        transação, como no cancelamento definitivo de um pedido.
        """

        valor = PagamentoService._converter_valor(valor)

        pagamento = PagamentoService._buscar_pagamento(
            usuario_id=usuario_id,
            pagamento_id=pagamento_id
        )

        if not pagamento:
            raise ValueError("Pagamento não encontrado.")

        total_recebido = PagamentoService.calcular_total_recebido(
            usuario_id=usuario_id,
            pagamento_id=pagamento_id
        )

        if valor > total_recebido:
            raise ValueError(
                "A devolução não pode ser maior "
                "que o valor efetivamente recebido."
            )

        if data_movimentacao is None:
            data_movimentacao = datetime.now(timezone.utc)

        movimentacao = MovimentacaoPagamento(
            pagamento_id=pagamento.id,
            tipo=TipoMovimentacaoPagamento.DEVOLUCAO,
            valor=valor,
            data_movimentacao=data_movimentacao,
            observacao=(
                observacao.strip()
                if observacao
                else None
            )
        )

        try:
            db.session.add(movimentacao)
            db.session.flush()

            PagamentoService._atualizar_status(
                pagamento
            )

            if commit:
                db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return movimentacao

    @staticmethod
    def _atualizar_status(pagamento):
        """
        Atualiza o status financeiro do pagamento.
        """

        item = pagamento.item_pedido

        valor_total = PagamentoService.calcular_valor_total_item(
            item
        )

        total_efetivo = Decimal("0.00")

        movimentacoes = db.session.scalars(
            db.select(MovimentacaoPagamento)
            .where(
                MovimentacaoPagamento.pagamento_id
                == pagamento.id
            )
        ).all()

        for movimentacao in movimentacoes:

            if (
                movimentacao.tipo
                == TipoMovimentacaoPagamento.RECEBIMENTO
            ):
                total_efetivo += movimentacao.valor

            elif (
                movimentacao.tipo
                == TipoMovimentacaoPagamento.DEVOLUCAO
            ):
                total_efetivo -= movimentacao.valor

        total_efetivo = total_efetivo.quantize(
            Decimal("0.01")
        )

        if total_efetivo <= 0:
            pagamento.status = StatusPagamento.PENDENTE

        elif total_efetivo < valor_total:
            pagamento.status = StatusPagamento.PARCIAL

        else:
            pagamento.status = StatusPagamento.PAGO