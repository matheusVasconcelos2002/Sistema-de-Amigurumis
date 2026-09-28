// =========================================================
// OFICIAL AMIGURUMIS
// PERFIL.JS
// =========================================================
//
// Responsável pelas interações da tela "Meu Perfil".
//
// FUNCIONALIDADES:
// - Visualizar foto de perfil
// - Pré-visualizar nova foto antes de salvar
// - Validar formato da imagem
// - Validar tamanho máximo de 5 MB
// - Cancelar seleção de nova foto
// - Confirmar alteração da foto
// - Confirmar remoção da foto
// - Evitar envio duplicado
// - Restaurar a foto original ao cancelar
//
// IMPORTANTE:
// O JavaScript apenas melhora a experiência do usuário.
// A validação definitiva deve continuar sendo feita
// pelo backend.
// =========================================================


document.addEventListener(
    "DOMContentLoaded",
    function () {


        // =====================================================
        // CONFIGURAÇÕES
        // =====================================================

        const TAMANHO_MAXIMO =
            20 * 1024 * 1024;


        const FORMATOS_PERMITIDOS = [
            "image/jpeg",
            "image/png",
            "image/webp"
        ];


        // =====================================================
        // ELEMENTOS DA FOTO
        // =====================================================

        const inputFoto =
            document.querySelector(
                "#foto_perfil"
            );


        const previewFoto =
            document.querySelector(
                "#preview_foto_perfil"
            );


        const btnVisualizarFoto =
            document.querySelector(
                "#btnVisualizarFoto"
            );


        const btnCancelarFoto =
            document.querySelector(
                "#btnCancelarFoto"
            );


        const btnSalvarFoto =
            document.querySelector(
                "#btnSalvarFoto"
            );


        const formFoto =
            document.querySelector(
                "#formFotoPerfil"
            );


        const formRemoverFoto =
            document.querySelector(
                "#formRemoverFoto"
            );


        // =====================================================
        // GUARDAR FOTO ORIGINAL
        // =====================================================

        let fotoOriginalSrc = null;

        let fotoOriginalAlt = null;


        if (
            previewFoto
        ) {

            fotoOriginalSrc =
                previewFoto.src;

            fotoOriginalAlt =
                previewFoto.alt;

        }


        // =====================================================
        // ARQUIVO SELECIONADO
        // =====================================================

        let arquivoSelecionado =
            null;


        // =====================================================
        // FUNÇÃO PARA LIMPAR ERRO VISUAL
        // =====================================================

        function limparErroCampo(
            campo
        ) {

            if (
                !campo
            ) {

                return;

            }


            campo.classList.remove(
                "campo_invalido"
            );

        }


        // =====================================================
        // FUNÇÃO PARA MARCAR ERRO VISUAL
        // =====================================================

        function marcarErroCampo(
            campo
        ) {

            if (
                !campo
            ) {

                return;

            }


            campo.classList.add(
                "campo_invalido"
            );

        }


        // =====================================================
        // VALIDAR EXTENSÃO / TIPO
        // =====================================================

        function formatoPermitido(arquivo) {

            if (!arquivo || !arquivo.name) {
                return false;
            }

            const nomeArquivo = arquivo.name.toLowerCase();

            const extensoesPermitidas = [
                ".jpg",
                ".jpeg",
                ".png",
                ".webp"
            ];

            const extensaoValida = extensoesPermitidas.some(
                function (extensao) {
                    return nomeArquivo.endsWith(extensao);
                }
            );

            if (!extensaoValida) {
                return false;
            }

            /*
             * Alguns celulares/navegadores podem informar
             * o MIME de maneira diferente ou até deixar vazio.
             *
             * Como a extensão já foi validada, não vamos
             * rejeitar automaticamente nesses casos.
             */

            if (!arquivo.type) {
                return true;
            }

            const formatosMimePermitidos = [
                "image/jpeg",
                "image/jpg",
                "image/png",
                "image/webp"
            ];

            return formatosMimePermitidos.includes(
                arquivo.type.toLowerCase()
            );
        }

        // =====================================================
        // VALIDAR TAMANHO
        // =====================================================

        function tamanhoPermitido(
            arquivo
        ) {

            if (
                !arquivo
            ) {

                return false;

            }


            return arquivo.size <=
                TAMANHO_MAXIMO;

        }


        // =====================================================
        // FORMATAR TAMANHO DO ARQUIVO
        // =====================================================

        function formatarTamanho(
            bytes
        ) {

            if (
                bytes < 1024 * 1024
            ) {

                return (
                    bytes / 1024
                ).toFixed(1)
                    + " KB";

            }


            return (
                bytes / (1024 * 1024)
            ).toFixed(2)
                + " MB";

        }


        // =====================================================
        // VALIDAR FOTO
        // =====================================================

        function validarFoto(
            arquivo
        ) {

            if (
                !arquivo
            ) {

                return false;

            }


            // -------------------------------------------------
            // FORMATO
            // -------------------------------------------------

            if (
                !formatoPermitido(
                    arquivo
                )
            ) {

                alert(
                    "Formato de imagem inválido.\n\n" +
                    "Escolha uma imagem JPG, JPEG, PNG ou WEBP."
                );

                marcarErroCampo(
                    inputFoto
                );

                return false;

            }


            // -------------------------------------------------
            // TAMANHO
            // -------------------------------------------------

            if (
                !tamanhoPermitido(
                    arquivo
                )
            ) {

                alert(
                    "A imagem selecionada possui " +
                    formatarTamanho(
                        arquivo.size
                    ) +
                    ".\n\n" +
                    "O tamanho máximo permitido é de 20 MB."
                );

                marcarErroCampo(
                    inputFoto
                );

                return false;

            }


            limparErroCampo(
                inputFoto
            );


            return true;

        }


        // =====================================================
        // PRÉ-VISUALIZAÇÃO
        // =====================================================

        if (
            inputFoto
            &&
            previewFoto
        ) {

            inputFoto.addEventListener(
                "change",
                function () {

                    const arquivo =
                        inputFoto.files[0];


                    // ---------------------------------------------
                    // NENHUM ARQUIVO
                    // ---------------------------------------------

                    if (
                        !arquivo
                    ) {

                        arquivoSelecionado =
                            null;

                        return;

                    }


                    // ---------------------------------------------
                    // VALIDAR
                    // ---------------------------------------------

                    if (
                        !validarFoto(
                            arquivo
                        )
                    ) {

                        inputFoto.value =
                            "";

                        arquivoSelecionado =
                            null;

                        return;

                    }


                    arquivoSelecionado =
                        arquivo;


                    // ---------------------------------------------
                    // GERAR PRÉ-VISUALIZAÇÃO
                    // ---------------------------------------------

                    const leitor =
                        new FileReader();


                    leitor.addEventListener(
                        "load",
                        function (evento) {

                            previewFoto.src =
                                evento.target.result;

                            previewFoto.alt =
                                "Pré-visualização da nova foto de perfil";

                        }
                    );


                    leitor.readAsDataURL(
                        arquivo
                    );

                }
            );

        }


        // =====================================================
        // VISUALIZAR FOTO
        // =====================================================
        //
        // Ao clicar na foto, abrimos uma visualização maior.
        //
        // Não criamos uma nova janela.
        // Apenas usamos uma interface simples do navegador.
        // =====================================================

        if (
            btnVisualizarFoto
            &&
            previewFoto
        ) {

            btnVisualizarFoto.addEventListener(
                "click",
                function () {

                    if (
                        !previewFoto.src
                    ) {

                        return;

                    }


                    // ---------------------------------------------
                    // ABRIR A IMAGEM EM NOVA ABA
                    // ---------------------------------------------

                    window.open(
                        previewFoto.src,
                        "_blank",
                        "noopener,noreferrer"
                    );

                }
            );

        }


        // =====================================================
        // CANCELAR SELEÇÃO
        // =====================================================

        if (
            btnCancelarFoto
        ) {

            btnCancelarFoto.addEventListener(
                "click",
                function () {

                    // ---------------------------------------------
                    // LIMPAR INPUT
                    // ---------------------------------------------

                    if (
                        inputFoto
                    ) {

                        inputFoto.value =
                            "";

                        limparErroCampo(
                            inputFoto
                        );

                    }


                    arquivoSelecionado =
                        null;


                    // ---------------------------------------------
                    // RESTAURAR FOTO ORIGINAL
                    // ---------------------------------------------

                    if (
                        previewFoto
                        &&
                        fotoOriginalSrc
                    ) {

                        previewFoto.src =
                            fotoOriginalSrc;

                        previewFoto.alt =
                            fotoOriginalAlt;

                    }

                }
            );

        }


        // =====================================================
        // CONFIRMAR ALTERAÇÃO DA FOTO
        // =====================================================

        if (
            formFoto
        ) {

            formFoto.addEventListener(
                "submit",
                function (evento) {

                    // ---------------------------------------------
                    // VERIFICAR ARQUIVO
                    // ---------------------------------------------

                    if (
                        !inputFoto
                        ||
                        !inputFoto.files.length
                    ) {

                        evento.preventDefault();

                        alert(
                            "Escolha uma foto antes de salvar."
                        );

                        if (
                            inputFoto
                        ) {

                            inputFoto.focus();

                        }

                        return;

                    }


                    const arquivo =
                        inputFoto.files[0];


                    // ---------------------------------------------
                    // VALIDAR NOVAMENTE
                    // ---------------------------------------------
                    //
                    // Mesmo tendo validado no "change",
                    // validamos novamente antes do envio.
                    // ---------------------------------------------

                    if (
                        !validarFoto(
                            arquivo
                        )
                    ) {

                        evento.preventDefault();

                        return;

                    }


                    // ---------------------------------------------
                    // CONFIRMAÇÃO
                    // ---------------------------------------------

                    const confirmou =
                        window.confirm(
                            "Deseja salvar esta nova foto de perfil?"
                        );


                    if (
                        !confirmou
                    ) {

                        evento.preventDefault();

                        return;

                    }


                    // ---------------------------------------------
                    // EVITAR DUPLO ENVIO
                    // ---------------------------------------------

                    if (
                        formFoto.dataset.enviando ===
                        "true"
                    ) {

                        evento.preventDefault();

                        return;

                    }


                    formFoto.dataset.enviando =
                        "true";


                    // ---------------------------------------------
                    // DESABILITAR BOTÃO
                    // ---------------------------------------------

                    if (
                        btnSalvarFoto
                    ) {

                        btnSalvarFoto.disabled =
                            true;

                        btnSalvarFoto.textContent =
                            "Salvando...";

                    }

                }
            );

        }


        // =====================================================
        // REMOVER FOTO
        // =====================================================

        if (
            formRemoverFoto
        ) {

            formRemoverFoto.addEventListener(
                "submit",
                function (evento) {

                    // ---------------------------------------------
                    // CONFIRMAÇÃO
                    // ---------------------------------------------

                    const confirmou =
                        window.confirm(
                            "Deseja realmente remover sua foto de perfil?\n\n" +
                            "A imagem padrão será utilizada novamente."
                        );


                    if (
                        !confirmou
                    ) {

                        evento.preventDefault();

                        return;

                    }


                    // ---------------------------------------------
                    // EVITAR DUPLO ENVIO
                    // ---------------------------------------------

                    if (
                        formRemoverFoto.dataset.enviando ===
                        "true"
                    ) {

                        evento.preventDefault();

                        return;

                    }


                    formRemoverFoto.dataset.enviando =
                        "true";


                    // ---------------------------------------------
                    // LOCALIZAR BOTÃO
                    // ---------------------------------------------

                    const botao =
                        formRemoverFoto.querySelector(
                            'button[type="submit"]'
                        );


                    if (
                        botao
                    ) {

                        botao.disabled =
                            true;

                        botao.textContent =
                            "Removendo...";

                    }

                }
            );

        }


        // =====================================================
        // IMPEDIR ENVIO DUPLICADO
        // =====================================================

        const formularios =
            document.querySelectorAll(
                ".form_foto, .form_remover_foto"
            );


        formularios.forEach(
            function (formulario) {

                formulario.addEventListener(
                    "keydown",
                    function (evento) {

                        // -----------------------------------------
                        // Não permitir Enter repetido enquanto
                        // o formulário estiver sendo enviado.
                        // -----------------------------------------

                        if (
                            formulario.dataset.enviando ===
                            "true"
                            &&
                            evento.key ===
                            "Enter"
                        ) {

                            evento.preventDefault();

                        }

                    }
                );

            }
        );


    }
);