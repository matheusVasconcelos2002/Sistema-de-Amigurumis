// =========================================================
// OFICIAL AMIGURUMIS V2
// RELATORIO.JS
// =========================================================
//
// Responsável somente pelas interações da tela.
//
// O JavaScript NÃO:
// - consulta banco;
// - calcula relatório;
// - gera relatório;
// - altera dados.
//
// Essas responsabilidades pertencem ao backend.
//
// =========================================================


document.addEventListener(
    "DOMContentLoaded",
    function () {


        // =====================================================
        // ELEMENTOS
        // =====================================================

        const formulario =
            document.querySelector(
                ".form_filtros"
            );


        const dataInicial =
            document.querySelector(
                "#data_inicial"
            );


        const dataFinal =
            document.querySelector(
                "#data_final"
            );


        const campoTipo =
            document.querySelector(
                "#tipo"
            );


        const botaoFiltrar =
            document.querySelector(
                ".btn_filtrar"
            );


        const botaoLimpar =
            document.querySelector(
                ".btn_limpar"
            );


        const botaoExportar =
            document.querySelector(
                ".btn_exportar"
            );



        // =====================================================
        // MARCAR CAMPO INVÁLIDO
        // =====================================================

        function marcarInvalido(
            campo
        ) {

            if (!campo) {
                return;
            }

            campo.classList.add(
                "campo_invalido"
            );

        }



        // =====================================================
        // LIMPAR ERRO
        // =====================================================

        function limparInvalido(
            campo
        ) {

            if (!campo) {
                return;
            }

            campo.classList.remove(
                "campo_invalido"
            );

        }



        // =====================================================
        // VALIDAR PERÍODO
        // =====================================================

        function validarPeriodo() {


            if (
                !dataInicial ||
                !dataFinal
            ) {

                return true;

            }


            if (
                !dataInicial.value ||
                !dataFinal.value
            ) {

                limparInvalido(
                    dataInicial
                );

                limparInvalido(
                    dataFinal
                );

                return true;

            }


            if (
                dataFinal.value <
                dataInicial.value
            ) {

                marcarInvalido(
                    dataInicial
                );

                marcarInvalido(
                    dataFinal
                );


                window.alert(
                    "A data final não pode ser anterior à data inicial."
                );


                dataFinal.focus();

                return false;

            }


            limparInvalido(
                dataInicial
            );

            limparInvalido(
                dataFinal
            );


            return true;

        }



        // =====================================================
        // DATA MÍNIMA
        // =====================================================

        function atualizarMinimoDataFinal() {


            if (
                !dataInicial ||
                !dataFinal
            ) {

                return;

            }


            if (
                dataInicial.value
            ) {

                dataFinal.min =
                    dataInicial.value;

            } else {

                dataFinal.removeAttribute(
                    "min"
                );

            }

        }



        // =====================================================
        // NORMALIZAR TIPO
        // =====================================================

        if (campoTipo) {

            campoTipo.addEventListener(
                "input",
                function () {

                    campoTipo.value =
                        campoTipo.value.replace(
                            /\s{2,}/g,
                            " "
                        );


                    limparInvalido(
                        campoTipo
                    );

                }
            );

        }



        // =====================================================
        // DATA INICIAL
        // =====================================================

        if (dataInicial) {

            dataInicial.addEventListener(
                "change",
                function () {

                    atualizarMinimoDataFinal();

                    validarPeriodo();

                }
            );

        }



        // =====================================================
        // DATA FINAL
        // =====================================================

        if (dataFinal) {

            dataFinal.addEventListener(
                "change",
                function () {

                    validarPeriodo();

                }
            );

        }



        // =====================================================
        // SUBMIT DOS FILTROS
        // =====================================================

        if (formulario) {

            formulario.addEventListener(
                "submit",
                function (evento) {


                    if (
                        !validarPeriodo()
                    ) {

                        evento.preventDefault();

                        return;

                    }


                    if (
                        formulario.dataset.enviando ===
                        "true"
                    ) {

                        evento.preventDefault();

                        return;

                    }


                    formulario.dataset.enviando =
                        "true";


                    if (botaoFiltrar) {

                        botaoFiltrar.disabled =
                            true;


                        botaoFiltrar.textContent =
                            "Filtrando...";

                    }

                }
            );

        }



        // =====================================================
        // LIMPAR FILTROS
        // =====================================================

        if (botaoLimpar) {

            botaoLimpar.addEventListener(
                "click",
                function () {

                    if (formulario) {

                        formulario.dataset.enviando =
                            "false";

                    }

                }
            );

        }



        // =====================================================
        // EXPORTAÇÃO
        // =====================================================

        if (botaoExportar) {

            botaoExportar.addEventListener(
                "click",
                function (evento) {


                    if (
                        !validarPeriodo()
                    ) {

                        evento.preventDefault();

                        return;

                    }


                    if (
                        botaoExportar.dataset.exportando ===
                        "true"
                    ) {

                        evento.preventDefault();

                        return;

                    }


                    const confirmou =
                        window.confirm(
                            "Deseja exportar o relatório atual para Excel?"
                        );


                    if (!confirmou) {

                        evento.preventDefault();

                        return;

                    }


                    botaoExportar.dataset.exportando =
                        "true";


                    botaoExportar.textContent =
                        "📊 Exportando...";

                }
            );

        }



        // =====================================================
        // INICIALIZAÇÃO
        // =====================================================

        atualizarMinimoDataFinal();

        validarPeriodo();

    }
);