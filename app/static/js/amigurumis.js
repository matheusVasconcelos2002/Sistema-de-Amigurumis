document.addEventListener("DOMContentLoaded", function () {

    // =====================================================
    // CONFIGURAÇÕES
    // =====================================================

    const LIMITE_IMAGEM = 15 * 1024 * 1024;
    const LIMITE_VIDEO = 105 * 1024 * 1024;

    const EXTENSOES_IMAGEM = [
        "jpg",
        "jpeg",
        "png",
        "webp"
    ];

    const EXTENSOES_VIDEO = [
        "mp4",
        "webm"
    ];


    // =====================================================
    // FUNÇÕES AUXILIARES
    // =====================================================

    function obterExtensao(nome) {

        const partes = nome
            .toLowerCase()
            .split(".");

        if (partes.length < 2) {
            return "";
        }

        return partes.pop();
    }


    function formatarTamanho(bytes) {

        if (bytes < 1024) {
            return `${bytes} bytes`;
        }

        if (bytes < 1024 * 1024) {
            return `${(bytes / 1024).toFixed(1)} KB`;
        }

        return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
    }


    function validarArquivo(arquivo) {

        const extensao = obterExtensao(
            arquivo.name
        );

        if (
            EXTENSOES_IMAGEM.includes(extensao)
        ) {

            if (arquivo.size > LIMITE_IMAGEM) {

                return {
                    valido: false,
                    mensagem:
                        `A imagem "${arquivo.name}" ` +
                        `ultrapassa o limite de 15 MB.`
                };
            }

            return {
                valido: true,
                tipo: "imagem"
            };
        }


        if (
            EXTENSOES_VIDEO.includes(extensao)
        ) {

            if (arquivo.size > LIMITE_VIDEO) {

                return {
                    valido: false,
                    mensagem:
                        `O vídeo "${arquivo.name}" ` +
                        `ultrapassa o limite de 105 MB.`
                };
            }

            return {
                valido: true,
                tipo: "video"
            };
        }


        return {
            valido: false,
            mensagem:
                `O arquivo "${arquivo.name}" ` +
                `possui um formato não permitido.`
        };
    }


    function mostrarErro(mensagem) {

        window.alert(
            mensagem
        );
    }


    // =====================================================
    // PREVIEW DE IMAGEM
    //
    // Usado em:
    // adicionar_amigurumis.html
    // editar_amigurumis.html
    // =====================================================

    const inputImagem =
        document.getElementById(
            "imagem"
        );

    const previewImagem =
        document.getElementById(
            "previewImagemContainer"
        );


    if (
        inputImagem &&
        previewImagem
    ) {

        inputImagem.addEventListener(
            "change",
            function () {

                previewImagem.innerHTML = "";

                const arquivo =
                    inputImagem.files[0];

                if (!arquivo) {
                    return;
                }


                const validacao =
                    validarArquivo(
                        arquivo
                    );


                if (!validacao.valido) {

                    inputImagem.value = "";

                    mostrarErro(
                        validacao.mensagem
                    );

                    return;
                }


                const imagem =
                    document.createElement(
                        "img"
                    );


                imagem.src =
                    URL.createObjectURL(
                        arquivo
                    );


                imagem.alt =
                    "Pré-visualização da imagem";


                previewImagem.appendChild(
                    imagem
                );
            }
        );
    }


    // =====================================================
    // PREVIEW DA GALERIA
    //
    // Usado em:
    // galeria_amigurumis.html
    // =====================================================

    const inputMidias =
        document.getElementById(
            "midias"
        );

    const previewMidias =
        document.getElementById(
            "previewMidias"
        );


    if (
        inputMidias &&
        previewMidias
    ) {

        inputMidias.addEventListener(
            "change",
            function () {

                previewMidias.innerHTML = "";

                const arquivos =
                    Array.from(
                        inputMidias.files
                    );


                for (
                    const arquivo
                    of arquivos
                ) {

                    const validacao =
                        validarArquivo(
                            arquivo
                        );


                    if (
                        !validacao.valido
                    ) {

                        inputMidias.value = "";

                        previewMidias.innerHTML = "";

                        mostrarErro(
                            validacao.mensagem
                        );

                        return;
                    }


                    const item =
                        document.createElement(
                            "div"
                        );


                    item.className =
                        "preview_midia_item";


                    const titulo =
                        document.createElement(
                            "strong"
                        );


                    titulo.textContent =
                        arquivo.name;


                    const tamanho =
                        document.createElement(
                            "small"
                        );


                    tamanho.textContent =
                        formatarTamanho(
                            arquivo.size
                        );


                    // -------------------------------------------------
                    // IMAGEM
                    // -------------------------------------------------

                    if (
                        validacao.tipo ===
                        "imagem"
                    ) {

                        const imagem =
                            document.createElement(
                                "img"
                            );


                        imagem.src =
                            URL.createObjectURL(
                                arquivo
                            );


                        imagem.alt =
                            arquivo.name;


                        item.appendChild(
                            imagem
                        );

                    }


                    // -------------------------------------------------
                    // VÍDEO
                    // -------------------------------------------------

                    else {

                        const video =
                            document.createElement(
                                "video"
                            );


                        video.controls =
                            true;


                        video.preload =
                            "metadata";


                        video.src =
                            URL.createObjectURL(
                                arquivo
                            );


                        item.appendChild(
                            video
                        );
                    }


                    item.appendChild(
                        titulo
                    );


                    item.appendChild(
                        tamanho
                    );


                    previewMidias.appendChild(
                        item
                    );
                }
            }
        );
    }


    // =====================================================
    // ENVIO DA GALERIA
    // =====================================================

    const formularioUpload =
        document.getElementById(
            "formUploadMidias"
        );


    const botaoEnviar =
        document.getElementById(
            "btnEnviarMidias"
        );


    if (
        formularioUpload
    ) {

        formularioUpload.addEventListener(
            "submit",
            function (evento) {

                // -------------------------------------------------
                // Verifica se existe pelo menos uma mídia
                // -------------------------------------------------

                if (
                    !inputMidias ||
                    inputMidias.files.length === 0
                ) {

                    evento.preventDefault();

                    mostrarErro(
                        "Selecione pelo menos uma " +
                        "imagem ou vídeo."
                    );

                    return;
                }


                // -------------------------------------------------
                // Valida todos os arquivos novamente
                // antes do envio
                // -------------------------------------------------

                for (
                    const arquivo
                    of inputMidias.files
                ) {

                    const validacao =
                        validarArquivo(
                            arquivo
                        );


                    if (
                        !validacao.valido
                    ) {

                        evento.preventDefault();

                        mostrarErro(
                            validacao.mensagem
                        );

                        return;
                    }
                }


                // -------------------------------------------------
                // Impede envio duplicado
                // -------------------------------------------------

                if (
                    formularioUpload.dataset.enviando ===
                    "true"
                ) {

                    evento.preventDefault();

                    return;
                }


                formularioUpload.dataset.enviando =
                    "true";


                // -------------------------------------------------
                // Atualiza botão
                // -------------------------------------------------

                if (
                    botaoEnviar
                ) {

                    botaoEnviar.disabled =
                        true;


                    botaoEnviar.textContent =
                        "Enviando...";
                }
            }
        );
    }


    // =====================================================
    // EXCLUSÃO DE MÍDIA
    // =====================================================

    const botoesExcluirMidia =
        document.querySelectorAll(
            "[data-excluir-midia]"
        );


    botoesExcluirMidia.forEach(
        function (botao) {

            botao.addEventListener(
                "click",
                function (evento) {

                    const confirmou =
                        window.confirm(
                            "Deseja excluir esta mídia?\n\n" +
                            "O arquivo será removido da galeria."
                        );


                    if (!confirmou) {

                        evento.preventDefault();
                    }
                }
            );
        }
    );


    // =====================================================
    // EXCLUSÃO DO AMIGURUMI
    // =====================================================

    const botoesExcluirAmigurumi =
        document.querySelectorAll(
            "[data-excluir-amigurumi]"
        );


    botoesExcluirAmigurumi.forEach(
        function (botao) {

            botao.addEventListener(
                "click",
                function (evento) {

                    const confirmou =
                        window.confirm(
                            "Deseja excluir este amigurumi?\n\n" +
                            "Ele será movido para a área de Excluídos " +
                            "e poderá ser restaurado posteriormente."
                        );


                    if (!confirmou) {

                        evento.preventDefault();
                    }
                }
            );
        }
    );


    // =====================================================
    // RESTAURAÇÃO DO AMIGURUMI
    // =====================================================

    const botoesRestaurar =
        document.querySelectorAll(
            "[data-restaurar-amigurumi]"
        );


    botoesRestaurar.forEach(
        function (botao) {

            botao.addEventListener(
                "click",
                function (evento) {

                    const confirmou =
                        window.confirm(
                            "Deseja restaurar este amigurumi?"
                        );


                    if (!confirmou) {

                        evento.preventDefault();
                    }
                }
            );
        }
    );


    // =====================================================
    // ABAS
    // ATIVOS / EXCLUÍDOS
    // =====================================================

    const abas =
        document.querySelectorAll(
            "[data-aba]"
        );


    const painelAtivos =
        document.getElementById(
            "painelAtivos"
        );


    const painelExcluidos =
        document.getElementById(
            "painelExcluidos"
        );


    abas.forEach(
        function (aba) {

            aba.addEventListener(
                "click",
                function () {

                    const destino =
                        aba.dataset.aba;


                    // -------------------------------------------------
                    // Remove a classe ativa de todas as abas
                    // -------------------------------------------------

                    abas.forEach(
                        function (item) {

                            item.classList.remove(
                                "ativa"
                            );
                        }
                    );


                    // -------------------------------------------------
                    // Ativa a aba clicada
                    // -------------------------------------------------

                    aba.classList.add(
                        "ativa"
                    );


                    // -------------------------------------------------
                    // Mostra/oculta painel de ativos
                    // -------------------------------------------------

                    if (
                        painelAtivos
                    ) {

                        painelAtivos.classList.toggle(
                            "ativo",
                            destino === "ativos"
                        );
                    }


                    // -------------------------------------------------
                    // Mostra/oculta painel de excluídos
                    // -------------------------------------------------

                    if (
                        painelExcluidos
                    ) {

                        painelExcluidos.classList.toggle(
                            "ativo",
                            destino === "excluidos"
                        );
                    }
                }
            );
        }
    );

});