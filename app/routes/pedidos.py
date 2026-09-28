from datetime import date, datetime
from decimal import Decimal, InvalidOperation

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

from app.models.enums import (
    FormaRecebimento,
    StatusItemPedido,
)

from app.services.amigurumi_service import (
    AmigurumiService,
)

from app.services.cliente_service import (
    ClienteService,
)

from app.services.pedido_service import (
    PedidoService,
)

from app.services.usuario_service import (
    UsuarioService,
)

from app.utils.autenticacao import (
    login_required,
)


pedidos_bp = Blueprint(
    "pedidos",
    __name__,
    url_prefix="/pedidos",
)


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def _obter_usuario():
    """Retorna o usuário atualmente autenticado."""

    usuario_id = session.get(
        "usuario_id"
    )

    if not usuario_id:
        return None

    usuario = UsuarioService.buscar_por_id(
        usuario_id
    )

    if not usuario:
        session.clear()
        return None

    return usuario


def _obter_itens_pedidos(
    usuario_id
):
    """
    Retorna os itens que ainda estão em andamento.

    Entregues e cancelados não aparecem na tela principal.
    """

    pedidos = PedidoService.listar_pedidos(
        usuario_id
    )

    itens = []

    for pedido in pedidos:

        for item in pedido.itens:

            if item.status in (
                StatusItemPedido.ENTREGUE,
                StatusItemPedido.CANCELADO,
            ):
                continue

            itens.append(item)

    itens.sort(
        key=lambda item: (
            item.data_prevista_entrega,
            item.id,
        )
    )

    return itens


def _obter_itens_finalizados(
    usuario_id
):
    """Retorna somente os itens entregues."""

    pedidos = PedidoService.listar_pedidos(
        usuario_id
    )

    itens = []

    for pedido in pedidos:

        for item in pedido.itens:

            if (
                item.status
                == StatusItemPedido.ENTREGUE
            ):
                itens.append(item)

    itens.sort(
        key=lambda item: (
            item.data_entrega
            or item.data_prevista_entrega,
            item.id,
        ),
        reverse=True,
    )

    return itens


def _converter_data(
    valor,
    nome_campo,
):
    """Converte YYYY-MM-DD para date."""

    try:

        return datetime.strptime(
            valor,
            "%Y-%m-%d",
        ).date()

    except (
        TypeError,
        ValueError,
    ):

        raise ValueError(
            f"A {nome_campo} informada é inválida."
        )


def _converter_decimal(
    valor,
    nome_campo,
):
    """Converte valor monetário ou decimal."""

    valor = str(
        valor or ""
    ).strip()

    if not valor:
        raise ValueError(
            f"O campo {nome_campo} é obrigatório."
        )

    valor = valor.replace(
        ",",
        ".",
    )

    try:

        return Decimal(
            valor
        )

    except (
        InvalidOperation,
        ValueError,
    ):

        raise ValueError(
            f"O campo {nome_campo} possui um valor inválido."
        )


# =========================================================
# ITENS DO FORMULÁRIO DA NOVA ENCOMENDA
# =========================================================

def _obter_itens_do_formulario():
    """
    Monta a lista de itens enviada pelo formulário.

    O formulário utiliza:

        produto[]
        quantidade[]
        tamanho[]
        tipo[]
        preco_unitario[]
        data_entrega_prevista[]

    O campo produto é convertido para amigurumi_id.

    Se o amigurumi ainda não existir para o usuário,
    ele será cadastrado automaticamente.
    """

    usuario_id = session[
        "usuario_id"
    ]

    produtos = request.form.getlist(
        "produto[]"
    )

    quantidades = request.form.getlist(
        "quantidade[]"
    )

    tamanhos = request.form.getlist(
        "tamanho[]"
    )

    tipos = request.form.getlist(
        "tipo[]"
    )

    precos = request.form.getlist(
        "preco_unitario[]"
    )

    datas = request.form.getlist(
        "data_entrega_prevista[]"
    )

    quantidade_itens = len(
        produtos
    )

    if quantidade_itens == 0:
        raise ValueError(
            "Adicione pelo menos um amigurumi."
        )

    campos = {
        "quantidade": quantidades,
        "tamanho": tamanhos,
        "tipo": tipos,
        "preco_unitario": precos,
        "data_entrega_prevista": datas,
    }

    for nome, valores in campos.items():

        if len(valores) != quantidade_itens:

            raise ValueError(
                "Os dados dos itens da encomenda estão incompletos."
            )

    amigurumis = (
        AmigurumiService.listar_ativos(
            usuario_id
        )
    )

    mapa_amigurumis = {
        amigurumi.produto.strip().lower():
            amigurumi
        for amigurumi in amigurumis
    }

    itens = []

    for indice, produto in enumerate(
        produtos
    ):

        produto = produto.strip()

        if not produto:

            raise ValueError(
                f"Informe o amigurumi do item {indice + 1}."
            )

        chave_produto = (
            produto.lower()
        )

        amigurumi = mapa_amigurumis.get(
            chave_produto
        )

        if not amigurumi:

            amigurumi = (
                AmigurumiService.cadastrar(
                    usuario_id=usuario_id,
                    produto=produto,
                    commit=False,
                )
            )

            mapa_amigurumis[
                chave_produto
            ] = amigurumi

        data_prevista = (
            _converter_data(
                datas[indice],
                "data prevista de entrega",
            )
        )

        itens.append(
            {
                "amigurumi_id":
                    amigurumi.id,

                "quantidade":
                    quantidades[indice],

                "tamanho":
                    tamanhos[indice],

                "tipo":
                    tipos[indice],

                "preco_unitario":
                    _converter_decimal(
                        precos[indice],
                        "preço unitário",
                    ),

                "data_prevista_entrega":
                    data_prevista,
            }
        )

    return itens


# =========================================================
# PEDIDOS EM ANDAMENTO
# =========================================================

@pedidos_bp.route("/")
@login_required
def listar():

    usuario = _obter_usuario()

    if not usuario:
        return redirect(
            url_for(
                "auth.login"
            )
        )

    data_hoje = date.today()

    itens = _obter_itens_pedidos(
        usuario.id
    )

    total_pedidos = len(
        itens
    )

    total_sendo_feito = sum(
        1
        for item in itens
        if (
            item.status
            == StatusItemPedido.SENDO_FEITO
        )
    )

    total_finalizados = sum(
        1
        for item in itens
        if (
            item.status
            == StatusItemPedido.FINALIZADO
        )
    )

    total_atrasados = sum(
        1
        for item in itens
        if (
            item.data_prevista_entrega
            and item.data_prevista_entrega
            < data_hoje
        )
    )

    return render_template(
        "pedidos.html",
        usuario=usuario,
        itens=itens,
        data_hoje=data_hoje,
        total_pedidos=total_pedidos,
        total_sendo_feito=total_sendo_feito,
        total_finalizados=total_finalizados,
        total_atrasados=total_atrasados,
    )


# =========================================================
# NOVA ENCOMENDA
# =========================================================

@pedidos_bp.route(
    "/novo",
    methods=[
        "GET",
        "POST",
    ],
)
@login_required
def novo():

    usuario = _obter_usuario()

    if not usuario:
        return redirect(
            url_for(
                "auth.login"
            )
        )

    usuario_id = usuario.id

    clientes = (
        ClienteService.listar_ativos(
            usuario_id
        )
    )

    amigurumis = (
        AmigurumiService.listar_ativos(
            usuario_id
        )
    )

    if request.method == "GET":

        return render_template(
            "nova_encomenda.html",
            usuario=usuario,
            clientes=clientes,
            amigurumis=amigurumis,
            dados={},
            itens_form=[],
        )

    dados = (
        request.form.to_dict(
            flat=False
        )
    )

    try:

        cliente_id = int(
            request.form.get(
                "cliente_id",
                "",
            )
        )

        nome = request.form.get(
            "nome",
            "",
        ).strip()

        data_pedido = (
            _converter_data(
                request.form.get(
                    "data_pedido",
                    "",
                ),
                "data do pedido",
            )
        )

        forma_recebimento = (
            request.form.get(
                "forma_recebimento",
                FormaRecebimento.A_DEFINIR.value,
            )
        )

        itens = (
            _obter_itens_do_formulario()
        )

        PedidoService.criar_pedido(
            usuario_id=usuario_id,
            cliente_id=cliente_id,
            nome=nome,
            data_pedido=data_pedido,
            forma_recebimento=forma_recebimento,
            itens=itens,
        )

        flash(
            "Encomenda registrada com sucesso!",
            "sucesso",
        )

        return redirect(
            url_for(
                "pedidos.listar"
            )
        )

    except (
        ValueError,
        TypeError,
    ) as erro:

        db.session.rollback()

        flash(
            str(erro),
            "erro",
        )

        return render_template(
            "nova_encomenda.html",
            usuario=usuario,
            clientes=clientes,
            amigurumis=amigurumis,
            dados=dados,
            itens_form=[],
        )


# =========================================================
# SELECIONAR ENCOMENDA PARA EDIÇÃO
# =========================================================

@pedidos_bp.route(
    "/editar"
)
@login_required
def selecionar_edicao():

    usuario = _obter_usuario()

    if not usuario:
        return redirect(
            url_for(
                "auth.login"
            )
        )

    pedidos = (
        PedidoService.listar_pedidos(
            usuario.id
        )
    )

    pedidos_disponiveis = [
        pedido
        for pedido in pedidos
        if any(
            item.status
            not in (
                StatusItemPedido.ENTREGUE,
                StatusItemPedido.CANCELADO,
            )
            for item in pedido.itens
        )
    ]

    return render_template(
        "selecionar_edicao_pedido.html",
        usuario=usuario,
        pedidos=pedidos_disponiveis,
    )


# =========================================================
# EDITAR ENCOMENDA
# =========================================================

@pedidos_bp.route(
    "/<int:pedido_id>/editar",
    methods=[
        "GET",
        "POST",
    ],
)
@login_required
def editar(
    pedido_id
):

    usuario = _obter_usuario()

    if not usuario:
        return redirect(
            url_for(
                "auth.login"
            )
        )

    usuario_id = usuario.id

    pedido = (
        PedidoService.buscar_por_id(
            usuario_id=usuario_id,
            pedido_id=pedido_id,
        )
    )

    if not pedido:

        flash(
            "Encomenda não encontrada.",
            "erro",
        )

        return redirect(
            url_for(
                "pedidos.listar"
            )
        )

    clientes = (
        ClienteService.listar_ativos(
            usuario_id
        )
    )

    amigurumis = (
        AmigurumiService.listar_ativos(
            usuario_id
        )
    )

    if request.method == "POST":

        try:

            # -------------------------------------------------
            # DADOS PRINCIPAIS DO PEDIDO
            # -------------------------------------------------

            cliente_id = int(
                request.form.get(
                    "cliente_id",
                    "",
                )
            )

            nome = (
                request.form.get(
                    "nome",
                    "",
                )
                .strip()
            )

            data_pedido = (
                _converter_data(
                    request.form.get(
                        "data_pedido",
                        "",
                    ),
                    "data do pedido",
                )
            )

            forma_recebimento = (
                request.form.get(
                    "forma_recebimento",
                    FormaRecebimento.A_DEFINIR.value,
                )
            )

            # -------------------------------------------------
            # DADOS DOS ITENS
            # -------------------------------------------------

            itens_ids = (
                request.form.getlist(
                    "item_id[]"
                )
            )

            amigurumi_ids = (
                request.form.getlist(
                    "amigurumi_id[]"
                )
            )

            quantidades = (
                request.form.getlist(
                    "quantidade[]"
                )
            )

            tamanhos = (
                request.form.getlist(
                    "tamanho[]"
                )
            )

            tipos = (
                request.form.getlist(
                    "tipo[]"
                )
            )

            precos = (
                request.form.getlist(
                    "preco_unitario[]"
                )
            )

            datas = (
                request.form.getlist(
                    "data_prevista_entrega[]"
                )
            )

            quantidade_itens = len(
                itens_ids
            )

            if quantidade_itens == 0:

                raise ValueError(
                    "A encomenda deve possuir pelo menos um item."
                )

            tamanhos_campos = {
                "amigurumi": amigurumi_ids,
                "quantidade": quantidades,
                "tamanho": tamanhos,
                "tipo": tipos,
                "preço": precos,
                "data prevista": datas,
            }

            for nome_campo, valores in (
                tamanhos_campos.items()
            ):

                if len(valores) != (
                    quantidade_itens
                ):

                    raise ValueError(
                        "Os dados dos itens da encomenda "
                        "estão incompletos."
                    )

            # -------------------------------------------------
            # MONTAR ITENS PARA O SERVICE
            # -------------------------------------------------

            itens = []

            for indice in range(
                quantidade_itens
            ):

                item_id = int(
                    itens_ids[indice]
                )

                amigurumi_id = int(
                    amigurumi_ids[indice]
                )

                quantidade = (
                    quantidades[indice]
                )

                tamanho = (
                    tamanhos[indice]
                )

                tipo = (
                    tipos[indice]
                )

                preco_unitario = (
                    _converter_decimal(
                        precos[indice],
                        "preço unitário",
                    )
                )

                data_prevista = (
                    _converter_data(
                        datas[indice],
                        "data prevista de entrega",
                    )
                )

                itens.append(
                    {
                        "item_id": item_id,
                        "amigurumi_id":
                            amigurumi_id,
                        "quantidade":
                            quantidade,
                        "tamanho":
                            tamanho,
                        "tipo":
                            tipo,
                        "preco_unitario":
                            preco_unitario,
                        "data_prevista_entrega":
                            data_prevista,
                    }
                )

            # -------------------------------------------------
            # ATUALIZAR TUDO EM UMA ÚNICA TRANSAÇÃO
            # -------------------------------------------------

            PedidoService.atualizar_pedido(
                usuario_id=usuario_id,
                pedido_id=pedido_id,
                cliente_id=cliente_id,
                nome=nome,
                data_pedido=data_pedido,
                forma_recebimento=forma_recebimento,
                itens=itens,
            )

            flash(
                "Encomenda atualizada com sucesso!",
                "sucesso",
            )

            return redirect(
                url_for(
                    "pedidos.listar"
                )
            )

        except (
            ValueError,
            TypeError,
            IndexError,
        ) as erro:

            db.session.rollback()

            flash(
                str(erro),
                "erro",
            )

    return render_template(
        "editar_encomenda.html",
        usuario=usuario,
        pedido=pedido,
        clientes=clientes,
        amigurumis=amigurumis,
    )


# =========================================================
# PEDIDOS FINALIZADOS
# =========================================================

@pedidos_bp.route(
    "/finalizados"
)
@login_required
def finalizados():

    usuario = _obter_usuario()

    if not usuario:
        return redirect(
            url_for(
                "auth.login"
            )
        )

    itens = (
        _obter_itens_finalizados(
            usuario.id
        )
    )

    valor_total = sum(
        (
            Decimal(
                str(
                    item.preco_unitario
                )
            )
            * item.quantidade
            for item in itens
        ),
        Decimal("0.00"),
    )

    valor_total_formatado = (
        f"{valor_total:.2f}"
        .replace(
            ".",
            ",",
        )
    )

    return render_template(
        "pedidos_finalizados.html",
        usuario=usuario,
        itens=itens,
        total_finalizados=len(
            itens
        ),
        valor_total_entregue=(
            valor_total_formatado
        ),
    )


# =========================================================
# INICIAR PRODUÇÃO
# =========================================================

@pedidos_bp.route(
    "/item/<int:item_id>/iniciar-producao",
    methods=["POST"],
)
@login_required
def iniciar_producao(
    item_id
):

    usuario_id = session[
        "usuario_id"
    ]

    try:

        PedidoService.alterar_status(
            usuario_id=usuario_id,
            item_pedido_id=item_id,
            novo_status=(
                StatusItemPedido.SENDO_FEITO
            ),
        )

        flash(
            "Produção iniciada com sucesso.",
            "sucesso",
        )

    except ValueError as erro:

        flash(
            str(erro),
            "erro",
        )

    return redirect(
        url_for(
            "pedidos.listar"
        )
    )


# =========================================================
# FINALIZAR ITEM
# =========================================================

@pedidos_bp.route(
    "/item/<int:item_id>/finalizar",
    methods=["POST"],
)
@login_required
def finalizar(
    item_id
):

    usuario_id = session[
        "usuario_id"
    ]

    try:

        PedidoService.finalizar_item(
            usuario_id=usuario_id,
            item_pedido_id=item_id,
        )

        flash(
            "Item finalizado com sucesso.",
            "sucesso",
        )

    except ValueError as erro:

        flash(
            str(erro),
            "erro",
        )

    return redirect(
        url_for(
            "pedidos.listar"
        )
    )


# =========================================================
# ENTREGAR ITEM
# =========================================================

@pedidos_bp.route(
    "/item/<int:item_id>/entregar",
    methods=["POST"],
)
@login_required
def entregar(
    item_id
):

    usuario_id = session[
        "usuario_id"
    ]

    try:

        PedidoService.entregar_item(
            usuario_id=usuario_id,
            item_pedido_id=item_id,
        )

        flash(
            "Item marcado como entregue.",
            "sucesso",
        )

    except ValueError as erro:

        flash(
            str(erro),
            "erro",
        )

    return redirect(
        url_for(
            "pedidos.listar"
        )
    )


# =========================================================
# CANCELAR ITEM
# =========================================================

@pedidos_bp.route(
    "/item/<int:item_id>/cancelar",
    methods=["POST"],
)
@login_required
def cancelar_item(
    item_id
):

    usuario_id = session[
        "usuario_id"
    ]

    motivo = request.form.get(
        "motivo_cancelamento",
        "",
    )

    devolver_pagamento = (
        request.form.get(
            "devolver_pagamento",
            "nao_devolver",
        )
    )

    try:

        resultado = (
            PedidoService.cancelar_item(
                usuario_id=usuario_id,
                item_pedido_id=item_id,
                motivo_cancelamento=motivo,
                devolver_pagamento=(
                    devolver_pagamento
                ),
            )
        )

        if (
            resultado[
                "valor_devolvido"
            ]
            > 0
        ):

            flash(
                "Item cancelado e valor devolvido ao cliente.",
                "sucesso",
            )

        else:

            flash(
                "Item cancelado com sucesso.",
                "sucesso",
            )

    except ValueError as erro:

        flash(
            str(erro),
            "erro",
        )

    return redirect(
        url_for(
            "pedidos.listar"
        )
    )


# =========================================================
# CANCELAR PEDIDO
# =========================================================

@pedidos_bp.route(
    "/<int:pedido_id>/cancelar",
    methods=["POST"],
)
@login_required
def cancelar_pedido(
    pedido_id
):

    usuario_id = session[
        "usuario_id"
    ]

    motivo = request.form.get(
        "motivo_cancelamento",
        "",
    )

    devolver_pagamentos = (
        request.form.get(
            "devolver_pagamentos",
            "nao_devolver",
        )
    )

    try:

        resultado = (
            PedidoService.cancelar_pedido(
                usuario_id=usuario_id,
                pedido_id=pedido_id,
                motivo_cancelamento=motivo,
                devolver_pagamentos=(
                    devolver_pagamentos
                ),
            )
        )

        if (
            resultado[
                "valor_devolvido"
            ]
            > 0
        ):

            flash(
                "Pedido cancelado e valores recebidos devolvidos ao cliente.",
                "sucesso",
            )

        else:

            flash(
                "Pedido cancelado com sucesso.",
                "sucesso",
            )

    except ValueError as erro:

        flash(
            str(erro),
            "erro",
        )

    return redirect(
        url_for(
            "pedidos.listar"
        )
    )