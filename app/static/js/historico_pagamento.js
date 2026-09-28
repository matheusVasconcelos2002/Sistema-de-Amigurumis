// =========================================================
// HISTÓRICO DE PAGAMENTO
// =========================================================


document.addEventListener(
    "DOMContentLoaded",
    function () {

        // =====================================================
        // ANIMAÇÃO SUAVE DAS MOVIMENTAÇÕES
        // =====================================================

        const movimentacoes =
            document.querySelectorAll(
                ".movimentacao"
            );


        movimentacoes.forEach(
            function (movimentacao, indice) {

                movimentacao.style.opacity = "0";

                movimentacao.style.transform =
                    "translateY(5px)";


                setTimeout(
                    function () {

                        movimentacao.style.transition =
                            "opacity 0.25s ease, transform 0.25s ease";


                        movimentacao.style.opacity =
                            "1";


                        movimentacao.style.transform =
                            "translateY(0)";

                    },
                    indice * 45
                );

            }
        );

    }
);