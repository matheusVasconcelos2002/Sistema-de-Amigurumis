document.addEventListener("DOMContentLoaded", () => {
    const botaoSuporte = document.querySelector(".botao_suporte");

    if (!botaoSuporte) {
        return;
    }

    botaoSuporte.addEventListener("click", () => {
        botaoSuporte.classList.add("clicado");

        setTimeout(() => {
            botaoSuporte.classList.remove("clicado");
        }, 300);
    });
});