// =========================================================
// 
// JAVASCRIPT GERAL
// =========================================================
// Este arquivo controla comportamentos gerais da interface.
//
// Aqui ficam:
// - Menu lateral
// - Botões gerais
// - Modais gerais
// - Mostrar / ocultar senha
// - Confirmações simples
//
// Funcionalidades específicas ficam em seus próprios arquivos:
// - CEP → cep.js
// - Pedidos → pedidos.js
// - Pagamentos → pagamentos.js
// - Clientes → clientes.js
// - Amigurumis → amigurumis.js
// =========================================================


// =========================================================
// MENU LATERAL
// =========================================================

// =========================================================
// MENU LATERAL
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const btnMenu =
            document.getElementById(
                "btnAbrirMenu"
            );

        const menuLateral =
            document.getElementById(
                "menuLateral"
            );

        const btnFecharMenu =
            document.getElementById(
                "btnFecharMenu"
            );

        const sobreposicaoMenu =
            document.getElementById(
                "sobreposicaoMenu"
            );


        // ---------------------------------------------------------
        // SE A PÁGINA NÃO POSSUIR MENU
        // ---------------------------------------------------------

        if (
            !btnMenu ||
            !menuLateral
        ) {

            return;

        }


        // ---------------------------------------------------------
        // ABRIR MENU
        // ---------------------------------------------------------

        function abrirMenu() {

            menuLateral.classList.add(
                "aberto"
            );


            btnMenu.setAttribute(
                "aria-expanded",
                "true"
            );


            if (sobreposicaoMenu) {

                sobreposicaoMenu.classList.add(
                    "visivel"
                );

                sobreposicaoMenu.setAttribute(
                    "aria-hidden",
                    "false"
                );

            }

        }


        // ---------------------------------------------------------
        // FECHAR MENU
        // ---------------------------------------------------------

        function fecharMenu() {

            menuLateral.classList.remove(
                "aberto"
            );


            btnMenu.setAttribute(
                "aria-expanded",
                "false"
            );


            if (sobreposicaoMenu) {

                sobreposicaoMenu.classList.remove(
                    "visivel"
                );

                sobreposicaoMenu.setAttribute(
                    "aria-hidden",
                    "true"
                );

            }

        }


        // ---------------------------------------------------------
        // BOTÃO ABRIR / FECHAR
        // ---------------------------------------------------------

        btnMenu.addEventListener(
            "click",
            function (evento) {

                evento.stopPropagation();


                if (
                    menuLateral.classList.contains(
                        "aberto"
                    )
                ) {

                    fecharMenu();

                } else {

                    abrirMenu();

                }

            }
        );


        // ---------------------------------------------------------
        // BOTÃO FECHAR
        // ---------------------------------------------------------

        if (btnFecharMenu) {

            btnFecharMenu.addEventListener(
                "click",
                function (evento) {

                    evento.stopPropagation();

                    fecharMenu();

                }
            );

        }


        // ---------------------------------------------------------
        // SOBREPOSIÇÃO
        // ---------------------------------------------------------

        if (sobreposicaoMenu) {

            sobreposicaoMenu.addEventListener(
                "click",
                function () {

                    fecharMenu();

                }
            );

        }


        // ---------------------------------------------------------
        // NÃO FECHAR AO CLICAR DENTRO DO MENU
        // ---------------------------------------------------------

        menuLateral.addEventListener(
            "click",
            function (evento) {

                evento.stopPropagation();

            }
        );


        // ---------------------------------------------------------
        // FECHAR COM ESC
        // ---------------------------------------------------------

        document.addEventListener(
            "keydown",
            function (evento) {

                if (
                    evento.key === "Escape"
                ) {

                    fecharMenu();

                }

            }
        );


        // ---------------------------------------------------------
        // FECHAR AO CLICAR EM UM LINK
        // ---------------------------------------------------------

        const linksMenu =
            menuLateral.querySelectorAll(
                "a"
            );


        linksMenu.forEach(
            function (link) {

                link.addEventListener(
                    "click",
                    function () {

                        fecharMenu();

                    }
                );

            }
        );


        // ---------------------------------------------------------
        // FECHAR AO ENVIAR FORMULÁRIO
        // ---------------------------------------------------------

        const formulariosMenu =
            menuLateral.querySelectorAll(
                "form"
            );


        formulariosMenu.forEach(
            function (formulario) {

                formulario.addEventListener(
                    "submit",
                    function () {

                        fecharMenu();

                    }
                );

            }
        );

    }
);

// =========================================================
// MOSTRAR / OCULTAR SENHA
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const botoesSenha =
            document.querySelectorAll(
                ".btn_mostrar_senha"
            );


        botoesSenha.forEach(
            function (botao) {

                botao.addEventListener(
                    "click",
                    function () {

                        const idCampo =
                            botao.getAttribute(
                                "data-target"
                            );


                        if (!idCampo) {
                            return;
                        }


                        const campo =
                            document.getElementById(
                                idCampo
                            );


                        if (!campo) {
                            return;
                        }


                        // -------------------------------------------------
                        // MOSTRAR SENHA
                        // -------------------------------------------------

                        if (
                            campo.type === "password"
                        ) {

                            campo.type = "text";

                            botao.textContent = "🙈";

                            botao.setAttribute(
                                "aria-label",
                                "Ocultar senha"
                            );

                            botao.setAttribute(
                                "title",
                                "Ocultar senha"
                            );

                            botao.setAttribute(
                                "aria-pressed",
                                "true"
                            );


                            // -------------------------------------------------
                            // OCULTAR SENHA
                            // -------------------------------------------------

                        } else {

                            campo.type = "password";

                            botao.textContent = "👁";

                            botao.setAttribute(
                                "aria-label",
                                "Mostrar senha"
                            );

                            botao.setAttribute(
                                "title",
                                "Mostrar senha"
                            );

                            botao.setAttribute(
                                "aria-pressed",
                                "false"
                            );

                        }

                    }
                );

            }
        );

    }
);


// =========================================================
// FECHAR MODAIS GERAIS
// =========================================================
// Este comportamento procura elementos que utilizem:
//
// .modal
// .modal_aberto
//
// e permite fechar clicando fora ou pressionando ESC.
//
// Cada modal continua responsável por abrir a si próprio.
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const modais =
            document.querySelectorAll(
                ".modal"
            );


        modais.forEach(
            function (modal) {

                // -------------------------------------------------
                // CLICAR FORA DO CONTEÚDO
                // -------------------------------------------------

                modal.addEventListener(
                    "click",
                    function (evento) {

                        if (
                            evento.target === modal
                        ) {

                            modal.classList.remove(
                                "modal_aberto"
                            );

                            modal.setAttribute(
                                "aria-hidden",
                                "true"
                            );

                        }

                    }
                );

            }
        );


        // ---------------------------------------------------------
        // TECLA ESC
        // ---------------------------------------------------------

        document.addEventListener(
            "keydown",
            function (evento) {

                if (evento.key !== "Escape") {
                    return;
                }


                modais.forEach(
                    function (modal) {

                        if (
                            modal.classList.contains(
                                "modal_aberto"
                            )
                        ) {

                            modal.classList.remove(
                                "modal_aberto"
                            );

                            modal.setAttribute(
                                "aria-hidden",
                                "true"
                            );

                        }

                    }
                );

            }
        );

    }
);


// =========================================================
// CONFIRMAÇÃO DE EXCLUSÃO DE CLIENTE
// =========================================================
// O formulário pode utilizar:
//
// onsubmit="return confirmarExclusaoCliente()"
//
// ou chamar a função através do próprio JS.
// =========================================================

function confirmarExclusaoCliente() {

    return confirm(
        "Você realmente deseja excluir este cliente?"
    );

}


// =========================================================
// CONFIRMAÇÃO DE EXCLUSÃO
// =========================================================
// Botões ou formulários que possuírem:
//
// data-confirmar="mensagem"
//
// receberão uma confirmação antes da ação.
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const elementos =
            document.querySelectorAll(
                "[data-confirmar]"
            );


        elementos.forEach(
            function (elemento) {

                elemento.addEventListener(
                    "click",
                    function (evento) {

                        const mensagem =
                            elemento.getAttribute(
                                "data-confirmar"
                            );


                        if (!mensagem) {
                            return;
                        }


                        const confirmou =
                            window.confirm(
                                mensagem
                            );


                        if (!confirmou) {

                            evento.preventDefault();

                        }

                    }
                );

            }
        );

    }
);