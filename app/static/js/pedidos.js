// =========================================================
// PEDIDOS.JS
// =========================================================
// Responsável pela tela:
// - Nova encomenda
// - Adicionar amigurumis
// - Remover amigurumis
// - Modal de confirmação
// - Organização dos itens
// =========================================================


document.addEventListener("DOMContentLoaded", function () {

    // =====================================================
    // ELEMENTOS PRINCIPAIS
    // =====================================================

    const listaAmigurumis =
        document.getElementById("lista_amigurumis");

    const btnAdicionar =
        document.getElementById("btnAdicionarAmigurumi");

    const modal =
        document.getElementById("modalConfirmacao");

    const btnCancelarRemocao =
        document.getElementById("btnCancelarRemocao");

    const btnConfirmarRemocao =
        document.getElementById("btnConfirmarRemocao");


    // =====================================================
    // VERIFICAÇÃO
    // =====================================================

    if (!listaAmigurumis || !btnAdicionar) {
        return;
    }


    // Item que está aguardando confirmação
    let itemParaRemover = null;


    // =====================================================
    // OBTER ITENS
    // =====================================================

    function obterItens() {

        return listaAmigurumis.querySelectorAll(
            ".item_encomenda"
        );

    }


    // =====================================================
    // ATUALIZAR NUMERAÇÃO DOS ITENS
    // =====================================================

    function atualizarItens() {

        const itens = obterItens();


        itens.forEach(function (item, indice) {

            const numero = indice + 1;


            // -------------------------------------------------
            // Número do item
            // -------------------------------------------------

            const rotulo =
                item.querySelector(".item_rotulo");

            if (rotulo) {

                rotulo.textContent =
                    "ITEM " + numero;

            }


            // -------------------------------------------------
            // Título do item
            // -------------------------------------------------

            const titulo =
                item.querySelector(".cabecalho_item h3");

            if (titulo) {

                titulo.textContent =
                    "Amigurumi " + numero;

            }


            // -------------------------------------------------
            // Botão Remover
            // -------------------------------------------------

            const btnRemover =
                item.querySelector(
                    ".btn_remover_amigurumi"
                );


            if (btnRemover) {

                if (numero === 1) {

                    // O primeiro item nunca pode ser removido.

                    btnRemover.style.display = "none";

                } else {

                    // A partir do segundo item,
                    // o botão fica disponível.

                    btnRemover.style.display = "inline-flex";

                }

            }

        });

    }


    // =====================================================
    // CRIAR NOVO ITEM
    // =====================================================

    function criarItem() {

        const item =
            document.createElement("div");

        item.className =
            "item_encomenda";


        item.innerHTML = `
            <div class="cabecalho_item">

                <div>

                    <span class="item_rotulo">
                        ITEM
                    </span>

                    <h3>
                        Amigurumi
                    </h3>

                </div>


                <button
                    type="button"
                    class="btn_remover_amigurumi"
                >
                    Remover
                </button>

            </div>


            <div class="grade_campos">


                <div class="campo campo_largo">

                    <label>
                        Nome do amigurumi
                        <span>*</span>
                    </label>

                    <input
                        type="text"
                        name="produto[]"
                        placeholder="Ex.: Pernalonga"
                        required
                    >

                </div>


                <div class="campo">

                    <label>
                        Quantidade
                        <span>*</span>
                    </label>

                    <input
                        type="number"
                        name="quantidade[]"
                        min="1"
                        value="1"
                        required
                    >

                </div>


                <div class="campo">

                    <label>
                        Tamanho (cm)
                        <span>*</span>
                    </label>

                    <input
                        type="number"
                        name="tamanho[]"
                        min="0.1"
                        step="0.1"
                        placeholder="Ex.: 20"
                        required
                    >

                </div>


                <div class="campo">

                    <label>
                        Tipo
                        <span>*</span>
                    </label>

                    <select
                        name="tipo[]"
                        required
                    >

                        <option value="">
                            Selecione
                        </option>

                        <option value="chaveiro">
                            Chaveiro
                        </option>

                        <option value="decoracao">
                            Decoração
                        </option>

                    </select>

                </div>


                <div class="campo">

                    <label>
                        Preço unitário
                        <span>*</span>
                    </label>

                    <input
                        type="number"
                        name="preco_unitario[]"
                        min="0.01"
                        step="0.01"
                        placeholder="Ex.: 35.00"
                        required
                    >

                </div>


                <div class="campo">

                    <label>
                        Data prevista de entrega
                        <span>*</span>
                    </label>

                    <input
                        type="date"
                        name="data_entrega_prevista[]"
                        required
                    >

                </div>


            </div>
        `;


        return item;

    }


    // =====================================================
    // ADICIONAR AMIGURUMI
    // =====================================================

    btnAdicionar.addEventListener(
        "click",
        function () {

            const novoItem =
                criarItem();


            listaAmigurumis.appendChild(
                novoItem
            );


            atualizarItens();


            // -------------------------------------------------
            // Leva o usuário para o novo item
            // -------------------------------------------------

            novoItem.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });


            // -------------------------------------------------
            // Coloca o cursor no nome do amigurumi
            // -------------------------------------------------

            const campoProduto =
                novoItem.querySelector(
                    'input[name="produto[]"]'
                );


            if (campoProduto) {

                setTimeout(function () {

                    campoProduto.focus();

                }, 300);

            }

        }
    );


    // =====================================================
    // ABRIR MODAL DE REMOÇÃO
    // =====================================================

    listaAmigurumis.addEventListener(
        "click",
        function (evento) {

            const btnRemover =
                evento.target.closest(
                    ".btn_remover_amigurumi"
                );


            if (!btnRemover) {
                return;
            }


            const item =
                btnRemover.closest(
                    ".item_encomenda"
                );


            if (!item) {
                return;
            }


            // -------------------------------------------------
            // Nunca permitir remover o primeiro item
            // -------------------------------------------------

            const itens =
                obterItens();


            const indice =
                Array.from(itens).indexOf(item);


            if (indice === 0) {

                return;

            }


            // -------------------------------------------------
            // Guardar item para confirmação
            // -------------------------------------------------

            itemParaRemover =
                item;


            abrirModal();

        }
    );


    // =====================================================
    // ABRIR MODAL
    // =====================================================

    function abrirModal() {

        if (!modal) {
            return;
        }


        modal.classList.add(
            "modal_aberto"
        );


        modal.setAttribute(
            "aria-hidden",
            "false"
        );


        document.body.classList.add(
            "modal_bloqueado"
        );

    }


    // =====================================================
    // FECHAR MODAL
    // =====================================================

    function fecharModal() {

        if (!modal) {
            return;
        }


        modal.classList.remove(
            "modal_aberto"
        );


        modal.setAttribute(
            "aria-hidden",
            "true"
        );


        document.body.classList.remove(
            "modal_bloqueado"
        );


        itemParaRemover =
            null;

    }


    // =====================================================
    // CANCELAR REMOÇÃO
    // =====================================================

    if (btnCancelarRemocao) {

        btnCancelarRemocao.addEventListener(
            "click",
            function () {

                fecharModal();

            }
        );

    }


    // =====================================================
    // CONFIRMAR REMOÇÃO
    // =====================================================

    if (btnConfirmarRemocao) {

        btnConfirmarRemocao.addEventListener(
            "click",
            function () {

                if (!itemParaRemover) {

                    fecharModal();

                    return;

                }


                // -------------------------------------------------
                // Verificação de segurança
                // -------------------------------------------------

                const itens =
                    obterItens();


                if (itens.length <= 1) {

                    fecharModal();

                    return;

                }


                const indice =
                    Array.from(itens)
                        .indexOf(itemParaRemover);


                // Nunca remover o primeiro
                if (indice === 0) {

                    fecharModal();

                    return;

                }


                // -------------------------------------------------
                // Remove o item
                // -------------------------------------------------

                itemParaRemover.remove();


                // -------------------------------------------------
                // Reorganiza os números
                // -------------------------------------------------

                atualizarItens();


                fecharModal();

            }
        );

    }


    // =====================================================
    // FECHAR MODAL CLICANDO FORA
    // =====================================================

    if (modal) {

        modal.addEventListener(
            "click",
            function (evento) {

                if (
                    evento.target === modal
                ) {

                    fecharModal();

                }

            }
        );

    }


    // =====================================================
    // FECHAR MODAL COM ESC
    // =====================================================

    document.addEventListener(
        "keydown",
        function (evento) {

            if (
                evento.key === "Escape" &&
                modal &&
                modal.classList.contains(
                    "modal_aberto"
                )
            ) {

                fecharModal();

            }

        }
    );


    // =====================================================
    // EVITAR SUBMISSÃO DUPLICADA
    // =====================================================

    const formulario =
        document.querySelector(
            ".formulario_encomenda"
        );


    if (formulario) {

        formulario.addEventListener(
            "submit",
            function () {

                const botao =
                    formulario.querySelector(
                        ".btn_registrar_encomenda"
                    );


                if (!botao) {
                    return;
                }


                // Evita múltiplos cliques
                if (
                    botao.dataset.enviando === "true"
                ) {

                    return;

                }


                botao.dataset.enviando =
                    "true";


                botao.disabled =
                    true;


                botao.dataset.textoOriginal =
                    botao.textContent;


                botao.textContent =
                    "Registrando...";

            }
        );

    }


    // =====================================================
    // INICIALIZAÇÃO
    // =====================================================

    atualizarItens();

});