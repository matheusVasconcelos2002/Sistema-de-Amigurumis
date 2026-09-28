// =========================================================
// ANOTACOES.JS
// =========================================================
// Responsável pelas interações específicas da tela
// de Anotações.
//
// FUNCIONALIDADES:
// - Detectar alterações no formulário
// - Avisar antes de sair com alterações não salvas
// - Confirmação ao excluir anotação
// - Confirmação ao restaurar anotação
// - Controle de botões de ação
// - Contador de caracteres
// - Evitar envio duplicado
//
// NÃO RESPONSÁVEL POR:
// - Menu geral              → script.js
// - Clientes                → clientes.js
// - CEP                    → cep.js
// - Amigurumis             → amigurumis.js
// - Pedidos                → pedidos.js
// - Pagamentos             → pagamentos.js
// =========================================================


document.addEventListener(
    "DOMContentLoaded",
    function () {

        // =====================================================
        // ELEMENTOS PRINCIPAIS
        // =====================================================

        const formularios =
            document.querySelectorAll(
                ".form_anotacao"
            );


        const cardsAnotacao =
            document.querySelectorAll(
                ".card_anotacao"
            );


        // =====================================================
        // CONTROLE DE ALTERAÇÕES NÃO SALVAS
        // =====================================================
        //
        // Regra da V2:
        //
        // Se o usuário estiver escrevendo uma anotação
        // e tentar sair sem salvar, devemos avisá-lo.
        //
        // Isso evita perder uma anotação por acidente.
        // =====================================================

        let anotacaoAlterada =
            false;


        let formularioAtivo =
            null;


        // =====================================================
        // MARCAR FORMULÁRIO COMO ALTERADO
        // =====================================================

        function marcarComoAlterado(
            formulario
        ) {

            anotacaoAlterada =
                true;


            formularioAtivo =
                formulario;


            formulario.dataset.alterado =
                "true";

        }


        // =====================================================
        // MARCAR COMO SALVO
        // =====================================================

        function marcarComoSalvo(
            formulario
        ) {

            anotacaoAlterada =
                false;


            formularioAtivo =
                null;


            formulario.dataset.alterado =
                "false";

        }


        // =====================================================
        // OBSERVAR CAMPOS DOS FORMULÁRIOS
        // =====================================================

        formularios.forEach(
            function (formulario) {

                const campos =
                    formulario.querySelectorAll(
                        "input, textarea, select"
                    );


                campos.forEach(
                    function (campo) {

                        campo.addEventListener(
                            "input",
                            function () {

                                marcarComoAlterado(
                                    formulario
                                );

                            }
                        );


                        campo.addEventListener(
                            "change",
                            function () {

                                marcarComoAlterado(
                                    formulario
                                );

                            }
                        );

                    }
                );


                // -------------------------------------------------
                // ENVIO DO FORMULÁRIO
                // -------------------------------------------------

                formulario.addEventListener(
                    "submit",
                    function () {

                        marcarComoSalvo(
                            formulario
                        );

                    }
                );

            }
        );


        // =====================================================
        // CONFIRMAÇÃO ANTES DE SAIR DA PÁGINA
        // =====================================================

        window.addEventListener(
            "beforeunload",
            function (evento) {

                if (
                    !anotacaoAlterada
                ) {

                    return;

                }


                evento.preventDefault();

                evento.returnValue =
                    "";

            }
        );


        // =====================================================
        // LINKS QUE SAEM DA PÁGINA
        // =====================================================
        //
        // Se houver alterações, perguntamos antes de seguir
        // para outra página.
        // =====================================================

        const links =
            document.querySelectorAll(
                "a"
            );


        links.forEach(
            function (link) {

                link.addEventListener(
                    "click",
                    function (evento) {

                        if (
                            !anotacaoAlterada
                        ) {

                            return;

                        }


                        // -----------------------------------------
                        // Links sem destino real
                        // -----------------------------------------

                        const destino =
                            link.getAttribute(
                                "href"
                            );


                        if (
                            !destino
                            ||
                            destino === "#"
                        ) {

                            return;

                        }


                        // -----------------------------------------
                        // Perguntar ao usuário
                        // -----------------------------------------

                        const confirmou =
                            window.confirm(
                                "Você possui alterações não salvas.\n\n" +
                                "Deseja sair mesmo assim?"
                            );


                        if (
                            !confirmou
                        ) {

                            evento.preventDefault();

                            return;

                        }


                        // -----------------------------------------
                        // Usuário confirmou
                        // -----------------------------------------

                        anotacaoAlterada =
                            false;

                    }
                );

            }
        );


        // =====================================================
        // CONTADOR DE CARACTERES
        // =====================================================
        //
        // O título possui limite de 200 caracteres.
        //
        // Se houver maxlength no HTML, o navegador já impede
        // ultrapassar o limite.
        //
        // Aqui apenas mostramos a quantidade utilizada,
        // caso exista um elemento de contador.
        // =====================================================

        const camposTitulo =
            document.querySelectorAll(
                'input[name="titulo"]'
            );


        camposTitulo.forEach(
            function (campo) {

                const contador =
                    campo
                        .closest(
                            "form"
                        )
                        ?.querySelector(
                            ".contador_titulo"
                        );


                function atualizarContador() {

                    if (
                        !contador
                    ) {

                        return;

                    }


                    const limite =
                        campo.maxLength;


                    const atual =
                        campo.value.length;


                    if (
                        limite > 0
                    ) {

                        contador.textContent =
                            atual +
                            " / " +
                            limite;

                    } else {

                        contador.textContent =
                            atual;

                    }

                }


                campo.addEventListener(
                    "input",
                    atualizarContador
                );


                atualizarContador();

            }
        );


        // =====================================================
        // CONTADOR DO CONTEÚDO
        // =====================================================

        const camposConteudo =
            document.querySelectorAll(
                'textarea[name="conteudo"]'
            );


        camposConteudo.forEach(
            function (campo) {

                const contador =
                    campo
                        .closest(
                            "form"
                        )
                        ?.querySelector(
                            ".contador_conteudo"
                        );


                function atualizarContador() {

                    if (
                        !contador
                    ) {

                        return;

                    }


                    const limite =
                        campo.maxLength;


                    const atual =
                        campo.value.length;


                    if (
                        limite > 0
                    ) {

                        contador.textContent =
                            atual +
                            " / " +
                            limite;

                    } else {

                        contador.textContent =
                            atual;

                    }

                }


                campo.addEventListener(
                    "input",
                    atualizarContador
                );


                atualizarContador();

            }
        );


        // =====================================================
        // CONFIRMAÇÕES ATRAVÉS DE DATA-CONFIRMAR
        // =====================================================
        //
        // Podemos usar no HTML:
        //
        // data-confirmar="Deseja excluir esta anotação?"
        //
        // ou:
        //
        // data-confirmar="Deseja restaurar esta anotação?"
        //
        // Assim não precisamos colocar JavaScript inline
        // dentro do HTML.
        // =====================================================

        const elementosConfirmacao =
            document.querySelectorAll(
                "[data-confirmar]"
            );


        elementosConfirmacao.forEach(
            function (elemento) {

                elemento.addEventListener(
                    "click",
                    function (evento) {

                        const mensagem =
                            elemento.getAttribute(
                                "data-confirmar"
                            );


                        if (
                            !mensagem
                        ) {

                            return;

                        }


                        const confirmou =
                            window.confirm(
                                mensagem
                            );


                        if (
                            !confirmou
                        ) {

                            evento.preventDefault();

                            return;

                        }


                        // Se confirmou uma ação que sai da
                        // página, não devemos mostrar novamente
                        // o aviso de alterações.
                        anotacaoAlterada =
                            false;

                    }
                );

            }
        );


        // =====================================================
        // EXCLUSÃO DE ANOTAÇÃO
        // =====================================================
        //
        // A anotação não é necessariamente apagada
        // definitivamente.
        //
        // Na V2 ela vai para a lixeira através de
        // excluido_em.
        //
        // O backend será responsável pela alteração.
        // O JavaScript apenas confirma a ação.
        // =====================================================

        const botoesExcluir =
            document.querySelectorAll(
                ".botao_excluir"
            );


        botoesExcluir.forEach(
            function (botao) {

                if (
                    botao.dataset.confirmacaoConfigurada ===
                    "true"
                ) {

                    return;

                }


                botao.dataset.confirmacaoConfigurada =
                    "true";


                botao.addEventListener(
                    "click",
                    function (evento) {

                        const confirmou =
                            window.confirm(
                                "Deseja mover esta anotação para a lixeira?"
                            );


                        if (
                            !confirmou
                        ) {

                            evento.preventDefault();

                            return;

                        }


                        anotacaoAlterada =
                            false;

                    }
                );

            }
        );


        // =====================================================
        // RESTAURAÇÃO DE ANOTAÇÃO
        // =====================================================

        const botoesRestaurar =
            document.querySelectorAll(
                ".botao_restaurar"
            );


        botoesRestaurar.forEach(
            function (botao) {

                if (
                    botao.dataset.confirmacaoConfigurada ===
                    "true"
                ) {

                    return;

                }


                botao.dataset.confirmacaoConfigurada =
                    "true";


                botao.addEventListener(
                    "click",
                    function (evento) {

                        const confirmou =
                            window.confirm(
                                "Deseja restaurar esta anotação?"
                            );


                        if (
                            !confirmou
                        ) {

                            evento.preventDefault();

                            return;

                        }


                        anotacaoAlterada =
                            false;

                    }
                );

            }
        );


        // =====================================================
        // EVITAR DUPLO ENVIO
        // =====================================================
        //
        // Evita que o usuário clique várias vezes em
        // "Salvar anotação".
        // =====================================================

        formularios.forEach(
            function (formulario) {

                formulario.addEventListener(
                    "submit",
                    function (evento) {

                        if (
                            formulario.dataset.enviando ===
                            "true"
                        ) {

                            evento.preventDefault();

                            return;

                        }


                        formulario.dataset.enviando =
                            "true";


                        const botao =
                            formulario.querySelector(
                                'button[type="submit"], input[type="submit"]'
                            );


                        if (
                            botao
                        ) {

                            botao.disabled =
                                true;


                            const textoOriginal =
                                botao.textContent;


                            botao.dataset.textoOriginal =
                                textoOriginal;


                            botao.textContent =
                                "Salvando...";

                        }

                    }
                );

            }
        );


        // =====================================================
        // DESTAQUE DA ANOTAÇÃO AO PASSAR O MOUSE
        // =====================================================
        //
        // O CSS já cuida da maior parte do visual.
        // Aqui deixamos apenas uma classe de estado,
        // caso seja utilizada posteriormente.
        // =====================================================

        cardsAnotacao.forEach(
            function (card) {

                card.addEventListener(
                    "mouseenter",
                    function () {

                        card.classList.add(
                            "em_foco"
                        );

                    }
                );


                card.addEventListener(
                    "mouseleave",
                    function () {

                        card.classList.remove(
                            "em_foco"
                        );

                    }
                );

            }
        );


        // =====================================================
        // INICIALIZAÇÃO
        // =====================================================

        formularios.forEach(
            function (formulario) {

                formulario.dataset.alterado =
                    "false";

                formulario.dataset.enviando =
                    "false";

            }
        );

    }
);