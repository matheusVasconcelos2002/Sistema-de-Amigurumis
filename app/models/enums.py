from enum import Enum


class TipoMidia(str, Enum):
    IMAGEM = "imagem"
    VIDEO = "video"


class FormaRecebimento(str, Enum):
    A_DEFINIR = "a_definir"
    ENTREGA = "entrega"
    RETIRADA = "retirada"


class StatusItemPedido(str, Enum):
    A_FAZER = "a_fazer"
    SENDO_FEITO = "sendo_feito"
    FINALIZADO = "finalizado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


class StatusPagamento(str, Enum):
    PENDENTE = "pendente"
    PARCIAL = "parcial"
    PAGO = "pago"


class TipoMovimentacaoPagamento(str, Enum):
    RECEBIMENTO = "recebimento"
    DEVOLUCAO = "devolucao"


class TemaInterface(str, Enum):
    CLARO = "claro"
    ESCURO = "escuro"