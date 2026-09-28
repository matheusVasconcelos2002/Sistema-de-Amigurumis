// =========================================================
// CEP.JS
// =========================================================
//
// Responsável por:
//
// - Formatar CEP
// - Consultar ViaCEP
// - Preencher endereço automaticamente
// - Permitir cadastro sem CEP
// - Controlar a opção "Não sei o CEP"
// - Funcionar em adicionar cliente e editar cliente
//
// =========================================================


document.addEventListener(
    "DOMContentLoaded",
    function () {


        // =====================================================
        // ELEMENTOS
        // =====================================================

        const campoCep =
            document.getElementById("cep");

        const botaoBuscarCep =
            document.getElementById("btnBuscarCep");

        const checkboxSemCep =
            document.getElementById(
                "cep_nao_informado"
            );

        const campoEstado =
            document.getElementById("estado");

        const campoCidade =
            document.getElementById("cidade");

        const campoRua =
            document.getElementById("rua");

        const campoBairro =
            document.getElementById("bairro");

        const ajudaCep =
            document.getElementById("ajuda_cep");


        // =====================================================
        // VERIFICAR SE ESTAMOS EM UMA TELA COM CEP
        // =====================================================

        if (
            !campoCep ||
            !botaoBuscarCep ||
            !checkboxSemCep
        ) {

            return;

        }


        // =====================================================
        // FORMATAR CEP
        // =====================================================

        function formatarCep(valor) {

            const numeros =
                String(valor || "")
                    .replace(/\D/g, "")
                    .substring(0, 8);


            if (numeros.length <= 5) {

                return numeros;

            }


            return (
                numeros.substring(0, 5)
                +
                "-"
                +
                numeros.substring(5)
            );

        }


        // =====================================================
        // LIMPAR ENDEREÇO
        // =====================================================

        function limparEndereco() {

            if (campoEstado) {
                campoEstado.value = "";
            }

            if (campoCidade) {
                campoCidade.value = "";
            }

            if (campoRua) {
                campoRua.value = "";
            }

            if (campoBairro) {
                campoBairro.value = "";
            }

        }


        // =====================================================
        // ATUALIZAR ESTADO DA TELA
        // =====================================================

        function atualizarEstadoCep() {

            const semCep =
                checkboxSemCep.checked;


            // -------------------------------------------------
            // USUÁRIO NÃO SABE O CEP
            // -------------------------------------------------

            if (semCep) {

                campoCep.value = "";

                campoCep.required = false;

                campoCep.disabled = true;

                botaoBuscarCep.disabled = true;

                botaoBuscarCep.style.display =
                    "none";


                if (ajudaCep) {

                    ajudaCep.textContent =
                        "O CEP não será obrigatório. " +
                        "Preencha manualmente o estado, " +
                        "cidade, rua e bairro.";

                }


                return;

            }


            // -------------------------------------------------
            // USUÁRIO SABE O CEP
            // -------------------------------------------------

            campoCep.disabled = false;

            campoCep.required = true;

            botaoBuscarCep.disabled = false;

            botaoBuscarCep.style.display =
                "inline-flex";


            if (ajudaCep) {

                ajudaCep.textContent =
                    "Informe o CEP e clique em " +
                    "\"Buscar CEP\" para preencher " +
                    "o endereço automaticamente.";

            }

        }


        // =====================================================
        // FORMATAR ENQUANTO DIGITA
        // =====================================================

        campoCep.addEventListener(
            "input",
            function () {

                campoCep.value =
                    formatarCep(
                        campoCep.value
                    );

            }
        );


        // =====================================================
        // CHECKBOX "NÃO SEI O CEP"
        // =====================================================

        checkboxSemCep.addEventListener(
            "change",
            function () {

                atualizarEstadoCep();

            }
        );


        // =====================================================
        // BUSCAR CEP
        // =====================================================

        async function buscarCep() {

            const cep =
                campoCep.value
                    .replace(/\D/g, "");


            // -------------------------------------------------
            // VALIDAR QUANTIDADE
            // -------------------------------------------------

            if (cep.length !== 8) {

                alert(
                    "Informe um CEP válido com 8 números."
                );

                campoCep.focus();

                return;

            }


            // -------------------------------------------------
            // DESABILITAR DURANTE CONSULTA
            // -------------------------------------------------

            botaoBuscarCep.disabled =
                true;

            botaoBuscarCep.textContent =
                "Buscando...";


            try {

                // -------------------------------------------------
                // VIA CEP
                // -------------------------------------------------

                const resposta =
                    await fetch(
                        `https://viacep.com.br/ws/${cep}/json/`
                    );


                if (!resposta.ok) {

                    throw new Error(
                        "Falha na consulta do CEP."
                    );

                }


                const dados =
                    await resposta.json();


                // -------------------------------------------------
                // CEP NÃO ENCONTRADO
                // -------------------------------------------------

                if (dados.erro) {

                    limparEndereco();

                    alert(
                        "CEP não encontrado."
                    );

                    return;

                }


                // -------------------------------------------------
                // PREENCHER ENDEREÇO
                // -------------------------------------------------

                if (campoEstado) {

                    campoEstado.value =
                        dados.uf || "";

                }


                if (campoCidade) {

                    campoCidade.value =
                        dados.localidade || "";

                }


                if (campoRua) {

                    campoRua.value =
                        dados.logradouro || "";

                }


                if (campoBairro) {

                    campoBairro.value =
                        dados.bairro || "";

                }


                // -------------------------------------------------
                // MANTER CEP FORMATADO
                // -------------------------------------------------

                campoCep.value =
                    formatarCep(cep);


            } catch (erro) {

                console.error(
                    "Erro ao consultar CEP:",
                    erro
                );


                alert(
                    "Não foi possível consultar o CEP agora. " +
                    "Você pode preencher o endereço manualmente."
                );


            } finally {

                botaoBuscarCep.disabled =
                    false;

                botaoBuscarCep.textContent =
                    "Buscar CEP";

            }

        }


        // =====================================================
        // BOTÃO BUSCAR CEP
        // =====================================================

        botaoBuscarCep.addEventListener(
            "click",
            buscarCep
        );


        // =====================================================
        // ENTER NO CAMPO CEP
        // =====================================================

        campoCep.addEventListener(
            "keydown",
            function (evento) {

                if (
                    evento.key === "Enter"
                    &&
                    !checkboxSemCep.checked
                ) {

                    evento.preventDefault();

                    buscarCep();

                }

            }
        );


        // =====================================================
        // ESTADO INICIAL
        // =====================================================
        //
        // Na edição:
        //
        // - se já existe CEP → mantém normal.
        //
        // - se não existe CEP → marca automaticamente
        //   "Não sei o CEP".
        //
        // =====================================================

        const cepInicial =
            campoCep.value
                .replace(/\D/g, "");


        if (cepInicial.length === 0) {

            checkboxSemCep.checked =
                true;

        }


        atualizarEstadoCep();

    }
);