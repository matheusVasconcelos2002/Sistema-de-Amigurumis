// =========================================================
// CLIENTES.JS
// =========================================================
// Responsável pelas interações específicas do módulo
// de clientes.
//
// FUNCIONALIDADES:
// - Pesquisa de clientes
// - Abas Ativos / Excluídos
// - Validação básica do formulário
// - Normalização do telefone
// - Normalização do CEP
// - Evitar envio duplicado
// - Confirmação de exclusão
// - Confirmação de restauração
//
// NÃO RESPONSÁVEL POR:
// - Menu lateral       → script.js
// - Buscar CEP         → cep.js
// - Regras de negócio  → Flask / Services
//
// As validações definitivas continuam no backend.
// =========================================================

document.addEventListener("DOMContentLoaded", function () {

    // =====================================================
    // ELEMENTOS GERAIS
    // =====================================================

    const campoTelefone = document.getElementById("telefone");
    const campoCep = document.getElementById("cep");


    // =====================================================
    // FUNÇÕES DE NORMALIZAÇÃO
    // =====================================================

    function normalizarTelefone(valor) {
        return String(valor || "").replace(/\D/g, "");
    }


    function normalizarCep(valor) {
        return String(valor || "").replace(/\D/g, "");
    }


    // =====================================================
    // TELEFONE
    // =====================================================
    // Permite somente números e limita a 11 dígitos.
    // =====================================================

    if (campoTelefone) {

        campoTelefone.addEventListener("input", function () {

            const valor = normalizarTelefone(
                campoTelefone.value
            );

            campoTelefone.value = valor.substring(0, 11);

        });

    }


    // =====================================================
    // VALIDAÇÃO DO FORMULÁRIO DE CLIENTE
    // =====================================================

    function validarFormularioCliente(
        formulario
    ) {

        const nome =
            formulario.querySelector(
                "#nome"
            );

        const telefone =
            formulario.querySelector(
                "#telefone"
            );

        const cep =
            formulario.querySelector(
                "#cep"
            );

        const cepNaoInformado =
            formulario.querySelector(
                "#cep_nao_informado"
            );

        const estado =
            formulario.querySelector(
                "#estado"
            );

        const cidade =
            formulario.querySelector(
                "#cidade"
            );

        const rua =
            formulario.querySelector(
                "#rua"
            );

        const bairro =
            formulario.querySelector(
                "#bairro"
            );


        // =====================================================
        // NOME
        // =====================================================

        if (
            nome &&
            !nome.value.trim()
        ) {

            alert(
                "Informe o nome do cliente."
            );

            nome.focus();

            return false;

        }


        // =====================================================
        // TELEFONE
        // =====================================================

        if (telefone) {

            const telefoneLimpo =
                normalizarTelefone(
                    telefone.value
                );


            if (
                telefoneLimpo.length !== 10
                &&
                telefoneLimpo.length !== 11
            ) {

                alert(
                    "Informe um telefone válido com 10 ou 11 números."
                );

                telefone.focus();

                return false;

            }


            telefone.value =
                telefoneLimpo;

        }


        // =====================================================
        // CEP
        // =====================================================

        const naoSabeCep =
            cepNaoInformado
            &&
            cepNaoInformado.checked;


        // -----------------------------------------------------
        // CASO 1:
        // Usuário marcou "Não sei o CEP"
        // -----------------------------------------------------

        if (naoSabeCep) {

            if (cep) {

                cep.value = "";

                cep.required = false;

            }

        }


        // -----------------------------------------------------
        // CASO 2:
        // Usuário NÃO marcou "Não sei o CEP"
        // -----------------------------------------------------

        else if (cep) {

            const cepLimpo =
                normalizarCep(
                    cep.value
                );


            if (
                cepLimpo.length !== 8
            ) {

                alert(
                    "Informe um CEP válido com 8 números ou marque \"Não sei o CEP\"."
                );

                cep.disabled = false;

                cep.focus();

                return false;

            }


            cep.value =
                cepLimpo;

        }


        // =====================================================
        // ESTADO
        // =====================================================

        if (
            estado &&
            !estado.value.trim()
        ) {

            alert(
                "Informe o estado do cliente."
            );

            estado.focus();

            return false;

        }


        // =====================================================
        // CIDADE
        // =====================================================

        if (
            cidade &&
            !cidade.value.trim()
        ) {

            alert(
                "Informe a cidade do cliente."
            );

            cidade.focus();

            return false;

        }


        // =====================================================
        // RUA
        // =====================================================

        if (
            rua &&
            !rua.value.trim()
        ) {

            alert(
                "Informe a rua do cliente."
            );

            rua.focus();

            return false;

        }


        // =====================================================
        // BAIRRO
        // =====================================================

        if (
            bairro &&
            !bairro.value.trim()
        ) {

            alert(
                "Informe o bairro do cliente."
            );

            bairro.focus();

            return false;

        }


        return true;

    }

    // =====================================================
    // FORMULÁRIOS
    // =====================================================
    //
    // IMPORTANTE:
    // Não usamos somente:
    //
    // form[action*="cliente"]
    //
    // porque os formulários de exclusão e restauração
    // também pertencem às rotas de clientes.
    //
    // Aqui identificamos primeiro se o formulário possui
    // campos reais de cadastro/edição.
    // =====================================================

    const formularios = document.querySelectorAll("form");


    formularios.forEach(function (formulario) {

        formulario.addEventListener(
            "submit",
            function (evento) {

                // =================================================
                // IDENTIFICAR EXCLUSÃO
                // =================================================

                const ehExclusao =
                    formulario.action.includes("/excluir") ||
                    formulario.querySelector(".btn_excluir");


                // =================================================
                // IDENTIFICAR RESTAURAÇÃO
                // =================================================

                const ehRestauracao =
                    formulario.action.includes("/restaurar");


                // =================================================
                // FORMULÁRIO DE EXCLUSÃO
                // =================================================
                //
                // A exclusão possui confirmação própria.
                // Não deve passar pela validação de nome,
                // telefone, CEP etc.
                // =================================================

                if (ehExclusao) {

                    return;
                }


                // =================================================
                // FORMULÁRIO DE RESTAURAÇÃO
                // =================================================

                if (ehRestauracao) {

                    return;
                }


                // =================================================
                // VERIFICAR SE É REALMENTE FORMULÁRIO DE CLIENTE
                // =================================================
                //
                // Isso evita que outros formulários da página
                // sejam afetados pelo código.
                // =================================================

                const possuiCamposCliente =
                    formulario.querySelector(
                        "#nome, #telefone, #cep, #estado, #cidade, #rua"
                    );


                if (!possuiCamposCliente) {

                    return;
                }


                // =================================================
                // VALIDAR
                // =================================================

                if (
                    !validarFormularioCliente(
                        formulario
                    )
                ) {

                    evento.preventDefault();

                    return;
                }


                // =================================================
                // EVITAR ENVIO DUPLICADO
                // =================================================

                if (
                    formulario.dataset.enviando === "true"
                ) {

                    evento.preventDefault();

                    return;
                }


                formulario.dataset.enviando = "true";


                // =================================================
                // DESABILITAR BOTÃO
                // =================================================

                const botaoEnviar =
                    formulario.querySelector(
                        'button[type="submit"]'
                    );


                if (botaoEnviar) {

                    botaoEnviar.disabled = true;

                    botaoEnviar.dataset.textoOriginal =
                        botaoEnviar.textContent;

                    botaoEnviar.textContent =
                        "Salvando...";
                }

            }
        );

    });


    // =====================================================
    // PESQUISA DE CLIENTES
    // =====================================================

    const campoPesquisa =
        document.getElementById(
            "pesquisa_cliente"
        );


    const listaAtivos =
        document.getElementById(
            "listaAtivos"
        );


    const listaExcluidos =
        document.getElementById(
            "listaExcluidos"
        );


    if (campoPesquisa) {

        campoPesquisa.addEventListener(
            "input",
            function () {

                const termo =
                    campoPesquisa.value
                        .trim()
                        .toLowerCase();


                // ---------------------------------------------
                // Procurar somente nas listas existentes.
                // ---------------------------------------------

                const listas = [
                    listaAtivos,
                    listaExcluidos
                ];


                listas.forEach(function (lista) {

                    if (!lista) {
                        return;
                    }


                    const clientes =
                        lista.querySelectorAll(
                            ".cliente_card, .cliente_item"
                        );


                    clientes.forEach(
                        function (cliente) {

                            const texto =
                                cliente.textContent
                                    .toLowerCase();


                            if (
                                !termo ||
                                texto.includes(termo)
                            ) {

                                cliente.style.display = "";

                            } else {

                                cliente.style.display = "none";
                            }

                        }
                    );

                });

            }
        );

    }


    // =====================================================
    // ABAS ATIVOS / EXCLUÍDOS
    // =====================================================

    const abas =
        document.querySelectorAll(
            ".aba_cliente"
        );


    function mostrarAba(tipo) {

        // -------------------------------------------------
        // ATIVOS
        // -------------------------------------------------

        if (listaAtivos) {

            listaAtivos.hidden =
                tipo !== "ativos";
        }


        // -------------------------------------------------
        // EXCLUÍDOS
        // -------------------------------------------------

        if (listaExcluidos) {

            listaExcluidos.hidden =
                tipo !== "excluidos";
        }


        // -------------------------------------------------
        // CLASSE VISUAL DA ABA
        // -------------------------------------------------

        abas.forEach(function (aba) {

            const abaTipo =
                aba.dataset.aba;


            if (abaTipo === tipo) {

                aba.classList.add("ativa");

            } else {

                aba.classList.remove("ativa");
            }

        });


        // -------------------------------------------------
        // LIMPAR PESQUISA AO TROCAR DE ABA
        // -------------------------------------------------

        if (campoPesquisa) {

            campoPesquisa.value = "";

            const listaVisivel =
                tipo === "ativos"
                    ? listaAtivos
                    : listaExcluidos;


            if (listaVisivel) {

                const clientes =
                    listaVisivel.querySelectorAll(
                        ".cliente_card, .cliente_item"
                    );


                clientes.forEach(
                    function (cliente) {

                        cliente.style.display = "";
                    }
                );

            }

        }

    }


    abas.forEach(function (aba) {

        aba.addEventListener(
            "click",
            function () {

                // -------------------------------------------------
                // Primeiro tenta usar data-aba.
                // -------------------------------------------------

                let tipo =
                    aba.dataset.aba;


                // -------------------------------------------------
                // Caso o HTML ainda não tenha data-aba,
                // identifica pela posição/texto.
                // -------------------------------------------------

                if (!tipo) {

                    const texto =
                        aba.textContent
                            .trim()
                            .toLowerCase();


                    if (
                        texto.includes("excluído") ||
                        texto.includes("excluidos")
                    ) {

                        tipo = "excluidos";

                    } else {

                        tipo = "ativos";
                    }

                }


                mostrarAba(tipo);

            }
        );

    });


    // =====================================================
    // ESTADO INICIAL DAS ABAS
    // =====================================================
    //
    // A tela começa mostrando clientes ativos.
    // =====================================================

    if (
        listaAtivos ||
        listaExcluidos
    ) {

        mostrarAba("ativos");
    }


    // =====================================================
    // CONFIRMAÇÃO DE EXCLUSÃO
    // =====================================================

    const botoesExcluir =
        document.querySelectorAll(
            ".btn_excluir"
        );


    botoesExcluir.forEach(
        function (botao) {

            botao.addEventListener(
                "click",
                function (evento) {

                    const confirmou =
                        window.confirm(
                            "Você realmente deseja excluir este cliente?\n\n" +
                            "O cliente será movido para a área de Excluídos."
                        );


                    if (!confirmou) {

                        evento.preventDefault();
                    }

                }
            );

        }
    );


    // =====================================================
    // CONFIRMAÇÃO DE RESTAURAÇÃO
    // =====================================================
    //
    // O HTML atual utiliza .btn_secundario.
    //
    // Por isso também verificamos a URL do formulário,
    // evitando depender de uma classe que ainda não existe.
    // =====================================================

    const formulariosRestauracao =
        document.querySelectorAll(
            'form[action*="/restaurar"]'
        );


    formulariosRestauracao.forEach(
        function (formulario) {

            formulario.addEventListener(
                "submit",
                function (evento) {

                    const confirmou =
                        window.confirm(
                            "Deseja restaurar este cliente?"
                        );


                    if (!confirmou) {

                        evento.preventDefault();
                    }

                }
            );

        }
    );


    // =====================================================
    // COMPATIBILIDADE COM editar_clientes.html
    // =====================================================
    //
    // Mantemos esta função global caso alguma versão da
    // tela de edição ainda utilize:
    //
    // onsubmit="return confirmarExclusaoCliente()"
    //
    // Posteriormente podemos remover essa compatibilidade
    // quando todas as telas estiverem usando somente JS externo.
    // =====================================================

    window.confirmarExclusaoCliente =
        function () {

            return window.confirm(
                "Você realmente deseja excluir este cliente?\n\n" +
                "O cliente será movido para a área de Excluídos."
            );

        };


    // =====================================================
    // CONFIRMAÇÃO GENÉRICA
    // =====================================================
    //
    // Permite futuramente utilizar:
    //
    // data-confirmar-cliente="Mensagem..."
    //
    // sem precisar criar outro código.
    // =====================================================

    const elementosConfirmacao =
        document.querySelectorAll(
            "[data-confirmar-cliente]"
        );


    elementosConfirmacao.forEach(
        function (elemento) {

            elemento.addEventListener(
                "click",
                function (evento) {

                    const mensagem =
                        elemento.getAttribute(
                            "data-confirmar-cliente"
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

});