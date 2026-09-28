from datetime import date, datetime

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.extensions import db
from app.models import (
    Pagamento,
    MovimentacaoPagamento,
    ItemPedido,
    Pedido,
)
from app.services.pagamento_service import PagamentoService
from app.services.usuario_service import UsuarioService
from app.utils.autenticacao import login_required


pagamentos_bp = Blueprint(
    "pagamentos",
    __name__,
    url_prefix="/pagamentos",
)


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def _obter_usuario():
    """
    Retorna o usuário atualmente autenticado.
    """

    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return None

    usuario = UsuarioService.buscar_por_id(
        usuario_id
    )

    if not usuario:
        session.clear()
        return None

    return usuario

def _garantir_pagamentos(usuario_id):
    """
    Garante que todo item de pedido do usuário
    possua um registro de pagamento.

    Serve também para corrigir pedidos antigos
    criados antes do controle financeiro existir.
    """

    itens = db.session.scalars(
        db.select(ItemPedido)
        .join(
            Pedido,
            ItemPedido.pedido_id == Pedido.id
        )
        .where(
            Pedido.usuario_id == usuario_id
        )
    ).all()

    alterou = False

    try:
        for item in itens:

            pagamento = (
                PagamentoService.buscar_por_item(
                    usuario_id=usuario_id,
                    item_pedido_id=item.id,
                )
            )

            if not pagamento:

                PagamentoService.criar_para_item(
                    usuario_id=usuario_id,
                    item_pedido_id=item.id,
                    commit=False,
                )

                alterou = True

        if alterou:
            db.session.commit()

    except Exception:
        db.session.rollback()
        raise
    
def _obter_pagamentos(usuario_id):
    """
    Retorna somente os pagamentos pertencentes
    ao usuário autenticado.

    Relacionamento:

        USUÁRIO
           ↓
        PEDIDO
           ↓
        ITEM_PEDIDO
           ↓
        PAGAMENTO
    """

    pagamentos = db.session.scalars(
        db.select(Pagamento)
        .join(
            ItemPedido,
            Pagamento.item_pedido_id
            == ItemPedido.id,
        )
        .join(
            Pedido,
            ItemPedido.pedido_id
            == Pedido.id,
        )
        .where(
            Pedido.usuario_id
            == usuario_id
        )
        .order_by(
            Pedido.data_pedido.desc(),
            Pagamento.id.desc(),
        )
    ).all()

    pagamentos_usuario = []

    for pagamento in pagamentos:

        item = pagamento.item_pedido

        if not item:
            continue

        pedido = item.pedido

        if not pedido:
            continue

        # -------------------------------------------------
        # SEGURANÇA
        # -------------------------------------------------

        if pedido.usuario_id != usuario_id:
            continue

        # -------------------------------------------------
        # VALORES FINANCEIROS
        # -------------------------------------------------

        total_recebido = (
            PagamentoService.calcular_total_recebido(
                usuario_id=usuario_id,
                pagamento_id=pagamento.id,
            )
        )

        total_devolvido = (
            PagamentoService.calcular_total_devolvido(
                usuario_id=usuario_id,
                pagamento_id=pagamento.id,
            )
        )

        valor_total = (
            PagamentoService.calcular_valor_total_item(
                item
            )
        )

        valor_restante = (
            PagamentoService.calcular_valor_restante(
                usuario_id=usuario_id,
                pagamento_id=pagamento.id,
            )
        )

        # -------------------------------------------------
        # ATRIBUTOS CALCULADOS
        # -------------------------------------------------

        pagamento.total_recebido = (
            total_recebido
        )

        pagamento.total_devolvido = (
            total_devolvido
        )

        pagamento.total_restante = (
            valor_restante
        )

        pagamento.valor_total = (
            valor_total
        )

        pagamentos_usuario.append(
            pagamento
        )

    return pagamentos_usuario


# =========================================================
# LISTAR PAGAMENTOS
# =========================================================

@pagamentos_bp.route("/")
@login_required
def listar():

    usuario = _obter_usuario()

    if not usuario:
        return redirect(
            url_for("auth.login")
        )

    _garantir_pagamentos(
        usuario.id
    )

    pagamentos = _obter_pagamentos(
        usuario.id
    )

    total_recebido = sum(
        pagamento.total_recebido
        for pagamento in pagamentos
    )

    total_restante = sum(
        pagamento.total_restante
        for pagamento in pagamentos
    )

    return render_template(
        "pagamentos.html",
        usuario=usuario,
        pagamentos=pagamentos,
        total_recebido=total_recebido,
        total_restante=total_restante,
        data_hoje=date.today(),
    )


# =========================================================
# REGISTRAR RECEBIMENTO
# =========================================================

@pagamentos_bp.route(
    "/<int:pagamento_id>/receber",
    methods=["POST"],
)
@login_required
def receber(pagamento_id):

    usuario = _obter_usuario()

    if not usuario:
        return redirect(
            url_for("auth.login")
        )

    valor = request.form.get(
        "valor",
        "",
    ).strip()

    data_movimentacao = request.form.get(
        "data_movimentacao",
        "",
    ).strip()

    observacao = request.form.get(
        "observacao",
        "",
    ).strip()

    try:

        data = None

        if data_movimentacao:
            data = datetime.strptime(
                data_movimentacao,
                "%Y-%m-%d",
            )

        PagamentoService.registrar_recebimento(
            usuario_id=usuario.id,
            pagamento_id=pagamento_id,
            valor=valor,
            data_movimentacao=data,
            observacao=(
                observacao
                if observacao
                else None
            ),
        )

        flash(
            "Recebimento registrado com sucesso!",
            "sucesso",
        )

    except (
        ValueError,
        TypeError,
    ) as erro:

        flash(
            str(erro),
            "erro",
        )

    return redirect(
        url_for("pagamentos.listar")
    )


# =========================================================
# REGISTRAR DEVOLUÇÃO
# =========================================================

@pagamentos_bp.route(
    "/<int:pagamento_id>/devolver",
    methods=["POST"],
)
@login_required
def devolver(pagamento_id):

    usuario = _obter_usuario()

    if not usuario:
        return redirect(
            url_for("auth.login")
        )

    valor = request.form.get(
        "valor",
        "",
    ).strip()

    data_movimentacao = request.form.get(
        "data_movimentacao",
        "",
    ).strip()

    observacao = request.form.get(
        "observacao",
        "",
    ).strip()

    try:

        data = None

        if data_movimentacao:
            data = datetime.strptime(
                data_movimentacao,
                "%Y-%m-%d",
            )

        PagamentoService.registrar_devolucao(
            usuario_id=usuario.id,
            pagamento_id=pagamento_id,
            valor=valor,
            data_movimentacao=data,
            observacao=(
                observacao
                if observacao
                else None
            ),
        )

        flash(
            "Devolução registrada com sucesso!",
            "sucesso",
        )

    except (
        ValueError,
        TypeError,
    ) as erro:

        flash(
            str(erro),
            "erro",
        )

    return redirect(
        url_for("pagamentos.listar")
    )


# =========================================================
# HISTÓRICO DE MOVIMENTAÇÕES
# =========================================================

@pagamentos_bp.route(
    "/<int:pagamento_id>/historico"
)
@login_required
def historico(pagamento_id):

    usuario = _obter_usuario()

    if not usuario:
        return redirect(
            url_for("auth.login")
        )

    try:

        movimentacoes = (
            PagamentoService.listar_movimentacoes(
                usuario_id=usuario.id,
                pagamento_id=pagamento_id,
            )
        )

    except ValueError as erro:

        flash(
            str(erro),
            "erro",
        )

        return redirect(
            url_for("pagamentos.listar")
        )

    pagamento = db.session.get(
        Pagamento,
        pagamento_id,
    )

    if not pagamento:
        flash(
            "Pagamento não encontrado.",
            "erro",
        )

        return redirect(
            url_for("pagamentos.listar")
        )

    item = pagamento.item_pedido

    if not item:
        flash(
            "Pagamento não encontrado.",
            "erro",
        )

        return redirect(
            url_for("pagamentos.listar")
        )

    pedido = item.pedido

    if not pedido:
        flash(
            "Pagamento não encontrado.",
            "erro",
        )

        return redirect(
            url_for("pagamentos.listar")
        )

    if pedido.usuario_id != usuario.id:

        flash(
            "Pagamento não encontrado.",
            "erro",
        )

        return redirect(
            url_for("pagamentos.listar")
        )

    return render_template(
        "historico_pagamento.html",
        usuario=usuario,
        pagamento=pagamento,
        movimentacoes=movimentacoes,
    )