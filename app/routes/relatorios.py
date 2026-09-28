from datetime import date
from io import BytesIO

from flask import (
    Blueprint,
    render_template,
    request,
    send_file,
    flash,
    session,
)

from app.extensions import db
from app.models import Cliente, Amigurumi, Usuario
from app.services.relatorio_service import RelatorioService
from app.utils.autenticacao import login_required


relatorios_bp = Blueprint(
    "relatorios",
    __name__,
    url_prefix="/relatorios",
)


def _obter_usuario():
    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return None

    return db.session.scalar(
        db.select(Usuario).where(
            Usuario.id == usuario_id
        )
    )


def _obter_filtros():
    return {
        "cliente_id": request.args.get(
            "cliente_id",
            type=int
        ),

        "amigurumi_id": request.args.get(
            "amigurumi_id",
            type=int
        ),

        "tipo": (
            request.args.get("tipo", "").strip()
            or None
        ),

        "status": (
            request.args.get("status", "").strip()
            or None
        ),

        "pagamento": (
            request.args.get("pagamento", "").strip()
            or None
        ),

        "data_inicial": (
            request.args.get("data_inicial", "").strip()
            or None
        ),

        "data_final": (
            request.args.get("data_final", "").strip()
            or None
        ),

        "atrasados": (
            request.args.get("atrasados") == "on"
        ),

        "situacao": (
            request.args.get(
                "situacao",
                "ativos"
            ).strip()
            or "ativos"
        ),
    }


def _carregar_opcoes(usuario_id, situacao):
    """
    Carrega clientes e amigurumis pertencentes
    ao usuário logado.
    """

    if situacao == "excluidos":

        clientes = db.session.scalars(
            db.select(Cliente)
            .where(
                Cliente.usuario_id == usuario_id,
                Cliente.excluido_em.is_not(None),
            )
            .order_by(
                Cliente.nome.asc()
            )
        ).all()

        amigurumis = db.session.scalars(
            db.select(Amigurumi)
            .where(
                Amigurumi.usuario_id == usuario_id,
                Amigurumi.excluido_em.is_not(None),
            )
            .order_by(
                Amigurumi.produto.asc()
            )
        ).all()

    elif situacao == "todos":

        clientes = db.session.scalars(
            db.select(Cliente)
            .where(
                Cliente.usuario_id == usuario_id
            )
            .order_by(
                Cliente.nome.asc()
            )
        ).all()

        amigurumis = db.session.scalars(
            db.select(Amigurumi)
            .where(
                Amigurumi.usuario_id == usuario_id
            )
            .order_by(
                Amigurumi.produto.asc()
            )
        ).all()

    else:

        clientes = db.session.scalars(
            db.select(Cliente)
            .where(
                Cliente.usuario_id == usuario_id,
                Cliente.excluido_em.is_(None),
            )
            .order_by(
                Cliente.nome.asc()
            )
        ).all()

        amigurumis = db.session.scalars(
            db.select(Amigurumi)
            .where(
                Amigurumi.usuario_id == usuario_id,
                Amigurumi.excluido_em.is_(None),
            )
            .order_by(
                Amigurumi.produto.asc()
            )
        ).all()

    return clientes, amigurumis


def _gerar_relatorio(usuario_id, filtros):

    return RelatorioService.gerar(
        usuario_id=usuario_id,

        cliente_id=filtros["cliente_id"],

        amigurumi_id=filtros["amigurumi_id"],

        tipo=filtros["tipo"],

        status=filtros["status"],

        pagamento=filtros["pagamento"],

        data_inicial=filtros["data_inicial"],

        data_final=filtros["data_final"],

        atrasados=filtros["atrasados"],

        situacao=filtros["situacao"],
    )


def _formatar_data(valor):

    if not valor:
        return ""

    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y")

    return str(valor)


def _formatar_datetime(valor):

    if not valor:
        return ""

    if hasattr(valor, "strftime"):
        return valor.strftime(
            "%d/%m/%Y %H:%M"
        )

    return str(valor)


def _exportar_excel(resultados, resumo):
    """
    Gera o Excel em memória.

    Nenhum arquivo temporário é criado
    no servidor.
    """

    try:

        import xlsxwriter

    except ImportError as erro:

        raise RuntimeError(
            "A biblioteca xlsxwriter "
            "não está instalada."
        ) from erro

    memoria = BytesIO()

    workbook = xlsxwriter.Workbook(
        memoria,
        {"in_memory": True}
    )

    worksheet = workbook.add_worksheet(
        "Relatório"
    )

    formato_titulo = workbook.add_format({
        "bold": True,
        "font_size": 14,
    })

    formato_cabecalho = workbook.add_format({
        "bold": True,
        "border": 1,
    })

    formato_moeda = workbook.add_format({
        "num_format": 'R$ #,##0.00',
    })

    formato_inteiro = workbook.add_format({
        "num_format": "0",
    })

    worksheet.write(
        "A1",
        "Relatório de pedidos",
        formato_titulo,
    )

    colunas = [
        "Pedido",
        "Cliente",
        "Amigurumi",
        "Quantidade",
        "Tamanho",
        "Tipo",
        "Preço unitário",
        "Total",
        "Status",
        "Pagamento",
        "Recebido",
        "Devolvido",
        "Líquido",
        "Restante",
        "Forma de recebimento",
        "Data do pedido",
        "Entrega prevista",
        "Entrega realizada",
        "Atrasado",
    ]

    linha_cabecalho = 2

    for coluna, nome in enumerate(colunas):

        worksheet.write(
            linha_cabecalho,
            coluna,
            nome,
            formato_cabecalho,
        )

    for indice, resultado in enumerate(
        resultados,
        start=linha_cabecalho + 1
    ):

        valores = [
            resultado["pedido_nome"],
            resultado["cliente_nome"],
            resultado["amigurumi_nome"],
            resultado["quantidade"],
            float(resultado["tamanho"]),
            resultado["tipo"],
            float(resultado["preco_unitario"]),
            float(resultado["valor_total"]),
            resultado["status_texto"],
            resultado["status_pagamento_texto"],
            float(resultado["valor_recebido"]),
            float(resultado["valor_devolvido"]),
            float(resultado["valor_efetivo"]),
            float(resultado["valor_restante"]),
            (
                resultado["forma_recebimento"].value
                if hasattr(
                    resultado["forma_recebimento"],
                    "value"
                )
                else str(
                    resultado["forma_recebimento"]
                )
            ),
            resultado["data_pedido"],
            resultado["data_prevista_entrega"],
            resultado["data_entrega"],
            (
                "Sim"
                if resultado["atrasado"]
                else "Não"
            ),
        ]

        for coluna, valor in enumerate(valores):

            if coluna in {
                6,
                7,
                10,
                11,
                12,
                13,
            }:

                worksheet.write_number(
                    indice,
                    coluna,
                    valor,
                    formato_moeda,
                )

            elif coluna == 3:

                worksheet.write_number(
                    indice,
                    coluna,
                    valor,
                    formato_inteiro,
                )

            elif coluna == 15:

                worksheet.write(
                    indice,
                    coluna,
                    _formatar_data(valor),
                )

            elif coluna == 16:

                worksheet.write(
                    indice,
                    coluna,
                    _formatar_data(valor),
                )

            elif coluna == 17:

                worksheet.write(
                    indice,
                    coluna,
                    _formatar_datetime(valor),
                )

            else:

                worksheet.write(
                    indice,
                    coluna,
                    valor,
                )

    linha_resumo = (
        len(resultados)
        + linha_cabecalho
        + 3
    )

    worksheet.write(
        linha_resumo,
        0,
        "Resumo",
        formato_titulo,
    )

    resumo_excel = [
        (
            "Pedidos",
            resumo["total_pedidos"]
        ),
        (
            "Itens",
            resumo["quantidade_itens"]
        ),
        (
            "Quantidade total",
            resumo["quantidade_total"]
        ),
        (
            "Valor total",
            float(resumo["valor_total"])
        ),
        (
            "Valor recebido",
            float(resumo["valor_recebido"])
        ),
        (
            "Valor devolvido",
            float(resumo["valor_devolvido"])
        ),
        (
            "Valor líquido",
            float(resumo["valor_liquido"])
        ),
        (
            "Valor restante",
            float(resumo["valor_restante"])
        ),
        (
            "Entregues",
            resumo["total_entregues"]
        ),
        (
            "Atrasados",
            resumo["total_atrasados"]
        ),
    ]

    for deslocamento, (
        nome,
        valor
    ) in enumerate(
        resumo_excel,
        start=1
    ):

        worksheet.write(
            linha_resumo + deslocamento,
            0,
            nome,
        )

        if isinstance(valor, float):

            worksheet.write_number(
                linha_resumo + deslocamento,
                1,
                valor,
                formato_moeda,
            )

        else:

            worksheet.write(
                linha_resumo + deslocamento,
                1,
                valor,
            )

    worksheet.set_column(
        "A:A",
        24
    )

    worksheet.set_column(
        "B:C",
        25
    )

    worksheet.set_column(
        "D:D",
        12
    )

    worksheet.set_column(
        "E:E",
        12
    )

    worksheet.set_column(
        "F:F",
        18
    )

    worksheet.set_column(
        "G:N",
        16
    )

    worksheet.set_column(
        "O:O",
        20
    )

    worksheet.set_column(
        "P:R",
        18
    )

    worksheet.set_column(
        "S:S",
        12
    )

    worksheet.freeze_panes(
        3,
        0
    )

    worksheet.autofilter(
        linha_cabecalho,
        0,
        linha_cabecalho + len(resultados),
        len(colunas) - 1,
    )

    workbook.close()

    memoria.seek(0)

    return memoria


@relatorios_bp.route(
    "/",
    methods=["GET"]
)
@login_required
def listar():

    usuario = _obter_usuario()

    if usuario is None:

        flash(
            "Usuário não encontrado.",
            "erro"
        )

        return render_template(
            "relatorio.html",
            usuario=None
        )

    filtros = _obter_filtros()

    if filtros["situacao"] not in {
        "ativos",
        "excluidos",
        "todos",
    }:

        filtros["situacao"] = "ativos"

    try:

        resultados = _gerar_relatorio(
            usuario.id,
            filtros,
        )

        resumo = (
            RelatorioService.calcular_totais(
                resultados
            )
        )

    except ValueError as erro:

        resultados = []

        resumo = (
            RelatorioService.calcular_totais(
                []
            )
        )

        flash(
            str(erro),
            "erro"
        )

    clientes, amigurumis = (
        _carregar_opcoes(
            usuario.id,
            filtros["situacao"],
        )
    )

    return render_template(
        "relatorio.html",
        usuario=usuario,
        resultados=resultados,
        resumo=resumo,
        clientes=clientes,
        amigurumis=amigurumis,
        filtros=filtros,
    )


@relatorios_bp.route(
    "/exportar-excel",
    methods=["GET"]
)
@login_required
def exportar_excel():

    usuario = _obter_usuario()

    if usuario is None:

        flash(
            "Usuário não encontrado.",
            "erro"
        )

        return render_template(
            "relatorio.html",
            usuario=None
        )

    filtros = _obter_filtros()

    if filtros["situacao"] not in {
        "ativos",
        "excluidos",
        "todos",
    }:

        filtros["situacao"] = "ativos"

    try:

        resultados = _gerar_relatorio(
            usuario.id,
            filtros,
        )

        resumo = (
            RelatorioService.calcular_totais(
                resultados
            )
        )

        arquivo = _exportar_excel(
            resultados,
            resumo,
        )

    except (
        ValueError,
        RuntimeError
    ) as erro:

        flash(
            str(erro),
            "erro"
        )

        return listar()

    nome_arquivo = (
        "relatorio_amigurumis_"
        f"{date.today().strftime('%Y-%m-%d')}.xlsx"
    )

    return send_file(
        arquivo,
        as_attachment=True,
        download_name=nome_arquivo,
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )