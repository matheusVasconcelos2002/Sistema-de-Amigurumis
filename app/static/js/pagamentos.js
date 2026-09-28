// =========================================================
// PAGAMENTOS.JS
// =========================================================


document.addEventListener(
    "DOMContentLoaded",
    function () {


        // =====================================================
        // ELEMENTOS
        // =====================================================

        const modal =
            document.getElementById(
                "modal_pagamento"
            );


        const formulario =
            document.getElementById(
                "form_pagamento"
            );


        const campoValor =
            document.getElementById(
                "valor_pagamento"
            );


        const campoData =
            document.getElementById(
                "data_movimentacao"
            );


        const campoObservacao =
            document.getElementById(
                "observacao_pagamento"
            );


        const cliente =
            document.getElementById(
                "modal_cliente"
            );


        const amigurumi =
            document.getElementById(
                "modal_amigurumi"
            );


        const valorLimite =
            document.getElementById(
                "modal_valor_limite"
            );


        const labelLimite =
            document.getElementById(
                "modal_label_limite"
            );


        const titulo =
            document.getElementById(
                "titulo_modal_pagamento"
            );


        const rotulo =
            document.getElementById(
                "rotulo_modal_pagamento"
            );


        const descricao =
            document.getElementById(
                "descricao_modal_pagamento"
            );


        const mensagemLimite =
            document.getElementById(
                "mensagem_limite"
            );


        const botoesAbrir =
            document.querySelectorAll(
                "[data-abrir-pagamento]"
            );


        const botoesFechar =
            document.querySelectorAll(
                "[data-fechar-pagamento]"
            );


        // =====================================================
        // CONVERTER VALOR
        // =====================================================

        function converterValor(valor) {

            if (
                valor === null ||
                valor === undefined ||
                valor === ""
            ) {

                return 0;

            }


            if (
                typeof valor === "number"
            ) {

                return Number.isFinite(valor)
                    ? valor
                    : 0;

            }


            let texto =
                String(valor)
                    .trim();


            /*
             * Aceita valores como:
             *
             * 3400
             * 3400.50
             * 3.400,50
             * 3400,50
             */

            if (
                texto.includes(".") &&
                texto.includes(",")
            ) {

                texto =
                    texto
                        .replace(/\./g, "")
                        .replace(",", ".");

            }

            else if (
                texto.includes(",")
            ) {

                texto =
                    texto.replace(
                        ",",
                        "."
                    );

            }


            const numero =
                Number(texto);


            return Number.isFinite(numero)
                ? numero
                : 0;

        }


        // =====================================================
        // FORMATAR MOEDA
        // =====================================================

        function formatarMoeda(valor) {

            return new Intl.NumberFormat(
                "pt-BR",
                {
                    style: "currency",
                    currency: "BRL"
                }
            ).format(
                converterValor(valor)
            );

        }


        // =====================================================
        // ABRIR MODAL
        // =====================================================

        function abrirModal(botao) {

            if (
                !modal ||
                !formulario ||
                !campoValor
            ) {

                return;

            }


            // -------------------------------------------------
            // DADOS DO BOTÃO
            // -------------------------------------------------

            const modo =
                botao.dataset.modo ||
                "receber";


            const url =
                botao.dataset.url ||
                "";


            const valorMaximo =
                converterValor(
                    botao.dataset.maximo
                );


            const nomeCliente =
                botao.dataset.cliente ||
                "-";


            const nomeAmigurumi =
                botao.dataset.amigurumi ||
                "-";


            // -------------------------------------------------
            // VERIFICAR URL
            // -------------------------------------------------

            if (!url) {

                alert(
                    "Não foi possível identificar a operação."
                );

                return;

            }


            // -------------------------------------------------
            // DADOS DO MODAL
            // -------------------------------------------------

            if (cliente) {

                cliente.textContent =
                    nomeCliente;

            }


            if (amigurumi) {

                amigurumi.textContent =
                    nomeAmigurumi;

            }


            if (valorLimite) {

                valorLimite.textContent =
                    formatarMoeda(
                        valorMaximo
                    );

            }


            // -------------------------------------------------
            // MODO RECEBIMENTO
            // -------------------------------------------------

            if (
                modo === "receber"
            ) {

                if (rotulo) {

                    rotulo.textContent =
                        "Recebimento";

                }


                if (titulo) {

                    titulo.textContent =
                        "Registrar pagamento";

                }


                if (descricao) {

                    descricao.textContent =
                        "Informe o valor recebido do cliente.";

                }


                if (labelLimite) {

                    labelLimite.textContent =
                        "Valor restante";

                }


                if (mensagemLimite) {

                    mensagemLimite.textContent =
                        "O valor não pode ser maior que o restante.";

                }


                formulario.action =
                    url;

            }


            // -------------------------------------------------
            // MODO DEVOLUÇÃO
            // -------------------------------------------------

            else if (
                modo === "devolver"
            ) {

                if (rotulo) {

                    rotulo.textContent =
                        "Devolução";

                }


                if (titulo) {

                    titulo.textContent =
                        "Registrar devolução";

                }


                if (descricao) {

                    descricao.textContent =
                        "Informe o valor que será devolvido ao cliente.";

                }


                if (labelLimite) {

                    labelLimite.textContent =
                        "Máximo para devolução";

                }


                if (mensagemLimite) {

                    mensagemLimite.textContent =
                        "A devolução não pode ser maior que o valor recebido.";

                }


                formulario.action =
                    url;

            }


            // -------------------------------------------------
            // LIMPAR CAMPO DE VALOR
            // -------------------------------------------------

            campoValor.value =
                "";


            campoValor.max =
                valorMaximo.toFixed(2);


            campoValor.dataset.maximo =
                valorMaximo.toFixed(2);


            campoValor.classList.remove(
                "campo_invalido"
            );


            // -------------------------------------------------
            // DATA
            // -------------------------------------------------

            if (
                campoData &&
                !campoData.value
            ) {

                const hoje =
                    new Date();


                const ano =
                    hoje.getFullYear();


                const mes =
                    String(
                        hoje.getMonth() + 1
                    ).padStart(
                        2,
                        "0"
                    );


                const dia =
                    String(
                        hoje.getDate()
                    ).padStart(
                        2,
                        "0"
                    );


                campoData.value =
                    `${ano}-${mes}-${dia}`;

            }


            // -------------------------------------------------
            // OBSERVAÇÃO
            // -------------------------------------------------

            if (campoObservacao) {

                campoObservacao.value =
                    "";

            }


            // -------------------------------------------------
            // CONTROLE DE ENVIO
            // -------------------------------------------------

            formulario.dataset.enviando =
                "false";


            const botaoConfirmar =
                document.getElementById(
                    "btn_confirmar_pagamento"
                );


            if (botaoConfirmar) {

                botaoConfirmar.disabled =
                    false;


                botaoConfirmar.textContent =
                    "Confirmar";

            }


            // -------------------------------------------------
            // EXIBIR MODAL
            // -------------------------------------------------

            modal.hidden =
                false;


            /*
             * IMPORTANTE:
             *
             * A classe precisa ser colocada
             * NO PRÓPRIO MODAL.
             *
             * O CSS utiliza:
             *
             * .modal_pagamento.modal_aberto
             */

            modal.classList.add(
                "modal_aberto"
            );


            /*
             * Também bloqueamos a rolagem
             * da página enquanto o modal
             * estiver aberto.
             */

            document.body.classList.add(
                "modal_bloqueado"
            );


            // -------------------------------------------------
            // FOCO
            // -------------------------------------------------

            setTimeout(
                function () {

                    campoValor.focus();

                },
                100
            );

        }


        // =====================================================
        // FECHAR MODAL
        // =====================================================

        function fecharModal() {

            if (!modal) {

                return;

            }


            // -------------------------------------------------
            // ESCONDER
            // -------------------------------------------------

            modal.classList.remove(
                "modal_aberto"
            );


            modal.hidden =
                true;


            // -------------------------------------------------
            // LIBERAR SCROLL
            // -------------------------------------------------

            document.body.classList.remove(
                "modal_bloqueado"
            );


            // -------------------------------------------------
            // LIMPAR ESTADO
            // -------------------------------------------------

            if (formulario) {

                formulario.dataset.enviando =
                    "false";

            }


            if (campoValor) {

                campoValor.classList.remove(
                    "campo_invalido"
                );

            }


            const botaoConfirmar =
                document.getElementById(
                    "btn_confirmar_pagamento"
                );


            if (botaoConfirmar) {

                botaoConfirmar.disabled =
                    false;


                botaoConfirmar.textContent =
                    "Confirmar";

            }

        }


        // =====================================================
        // BOTÕES DE ABRIR
        // =====================================================

        botoesAbrir.forEach(
            function (botao) {

                botao.addEventListener(
                    "click",
                    function (evento) {

                        evento.preventDefault();

                        abrirModal(
                            botao
                        );

                    }
                );

            }
        );


        // =====================================================
        // BOTÕES DE FECHAR
        // =====================================================

        botoesFechar.forEach(
            function (botao) {

                botao.addEventListener(
                    "click",
                    function (evento) {

                        evento.preventDefault();

                        fecharModal();

                    }
                );

            }
        );


        // =====================================================
        // CLICAR NO FUNDO DO MODAL
        // =====================================================

        if (modal) {

            modal.addEventListener(
                "click",
                function (evento) {

                    /*
                     * Se clicou diretamente no
                     * fundo/sobreposição, fecha.
                     */

                    if (
                        evento.target === modal
                    ) {

                        fecharModal();

                    }

                }
            );

        }


        // =====================================================
        // ESC FECHA O MODAL
        // =====================================================

        document.addEventListener(
            "keydown",
            function (evento) {

                if (
                    evento.key === "Escape" &&
                    modal &&
                    !modal.hidden
                ) {

                    fecharModal();

                }

            }
        );


        // =====================================================
        // VALIDAR VALOR
        // =====================================================

        if (formulario) {

            formulario.addEventListener(
                "submit",
                function (evento) {


                    // -----------------------------------------
                    // EVITAR DUPLO ENVIO
                    // -----------------------------------------

                    if (
                        formulario.dataset.enviando
                        === "true"
                    ) {

                        evento.preventDefault();

                        return;

                    }


                    // -----------------------------------------
                    // PEGAR VALOR
                    // -----------------------------------------

                    const valor =
                        converterValor(
                            campoValor.value
                        );


                    const maximo =
                        converterValor(
                            campoValor.dataset.maximo
                        );


                    // -----------------------------------------
                    // MAIOR QUE ZERO
                    // -----------------------------------------

                    if (
                        valor <= 0
                    ) {

                        evento.preventDefault();


                        alert(
                            "Informe um valor maior que zero."
                        );


                        campoValor.focus();

                        return;

                    }


                    // -----------------------------------------
                    // NÃO PODE ULTRAPASSAR LIMITE
                    // -----------------------------------------

                    if (
                        valor > maximo
                    ) {

                        evento.preventDefault();


                        alert(
                            "O valor informado não pode ser maior que " +
                            formatarMoeda(maximo) +
                            "."
                        );


                        campoValor.focus();

                        return;

                    }


                    // -----------------------------------------
                    // CONFIRMAÇÃO
                    // -----------------------------------------

                    const modo =
                        formulario.action.includes(
                            "/devolver"
                        )
                            ? "devolução"
                            : "recebimento";


                    const confirmou =
                        window.confirm(
                            "Deseja registrar esta " +
                            modo +
                            "?\n\nValor: " +
                            formatarMoeda(valor)
                        );


                    if (!confirmou) {

                        evento.preventDefault();

                        return;

                    }


                    // -----------------------------------------
                    // EVITAR DUPLO ENVIO
                    // -----------------------------------------

                    formulario.dataset.enviando =
                        "true";


                    const botao =
                        document.getElementById(
                            "btn_confirmar_pagamento"
                        );


                    if (botao) {

                        botao.disabled =
                            true;


                        botao.textContent =
                            "Registrando...";

                    }

                }
            );

        }


        // =====================================================
        // VALIDAR DIGITAÇÃO DO VALOR
        // =====================================================

        if (campoValor) {

            campoValor.addEventListener(
                "input",
                function () {

                    const valor =
                        converterValor(
                            campoValor.value
                        );


                    const maximo =
                        converterValor(
                            campoValor.dataset.maximo
                        );


                    if (
                        valor > maximo
                    ) {

                        campoValor.classList.add(
                            "campo_invalido"
                        );

                    }

                    else {

                        campoValor.classList.remove(
                            "campo_invalido"
                        );

                    }

                }
            );

        }


        // =====================================================
        // ATUALIZAR VALORES VISUAIS
        // =====================================================

        const linhas =
            document.querySelectorAll(
                "[data-financeiro]"
            );


        linhas.forEach(
            function (linha) {

                const total =
                    converterValor(
                        linha.dataset.total
                    );


                const recebido =
                    converterValor(
                        linha.dataset.recebido
                    );


                const devolvido =
                    converterValor(
                        linha.dataset.devolvido
                    );


                // ---------------------------------------------
                // TOTAL LÍQUIDO RECEBIDO
                // ---------------------------------------------

                const liquido =
                    Math.max(
                        recebido -
                        devolvido,
                        0
                    );


                // ---------------------------------------------
                // RESTANTE
                // ---------------------------------------------

                const restante =
                    Math.max(
                        total -
                        liquido,
                        0
                    );


                // ---------------------------------------------
                // CAMPO RECEBIDO
                // ---------------------------------------------

                const elementoRecebido =
                    linha.querySelector(
                        ".valor_pago"
                    );


                if (
                    elementoRecebido
                ) {

                    elementoRecebido.textContent =
                        formatarMoeda(
                            liquido
                        );

                }


                // ---------------------------------------------
                // CAMPO RESTANTE
                // ---------------------------------------------

                const elementoRestante =
                    linha.querySelector(
                        ".valor_restante"
                    );


                if (
                    elementoRestante
                ) {

                    elementoRestante.textContent =
                        formatarMoeda(
                            restante
                        );

                }

            }
        );


    }
);