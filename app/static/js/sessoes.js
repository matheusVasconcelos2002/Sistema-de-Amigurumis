document.addEventListener(
    "DOMContentLoaded",
    function () {

        const botoesEncerrar =
            document.querySelectorAll(
                "[data-encerrar-sessao]"
            );

        const botaoEncerrarOutras =
            document.querySelector(
                "[data-encerrar-outras]"
            );


        async function enviar(
            url,
            mensagemConfirmacao
        ) {

            if (
                mensagemConfirmacao
                &&
                !window.confirm(
                    mensagemConfirmacao
                )
            ) {

                return;

            }


            const resposta =
                await fetch(
                    url,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json",
                        },
                    }
                );


            const dados =
                await resposta.json();


            if (
                !resposta.ok ||
                !dados.sucesso
            ) {

                throw new Error(
                    dados.mensagem
                    ||
                    "Não foi possível realizar a operação."
                );

            }


            return dados;

        }


        botoesEncerrar.forEach(
            function (botao) {

                botao.addEventListener(
                    "click",
                    async function () {

                        const sessaoId =
                            botao.dataset
                                .encerrarSessao;

                        const url =
                            botao.dataset.url
                            ||
                            `/sessoes/${sessaoId}/encerrar`;


                        try {

                            const dados =
                                await enviar(
                                    url,
                                    "Deseja realmente encerrar esta sessão?"
                                );


                            window.alert(
                                dados.mensagem
                            );


                            window.location.reload();

                        } catch (erro) {

                            window.alert(
                                erro.message
                            );

                        }

                    }
                );

            }
        );


        if (botaoEncerrarOutras) {

            botaoEncerrarOutras.addEventListener(
                "click",
                async function () {

                    try {

                        const dados =
                            await enviar(
                                "/sessoes/encerrar-outras",
                                "Deseja encerrar todas as outras sessões?"
                            );


                        window.alert(
                            dados.mensagem
                        );


                        window.location.reload();

                    } catch (erro) {

                        window.alert(
                            erro.message
                        );

                    }

                }
            );

        }

    }
);