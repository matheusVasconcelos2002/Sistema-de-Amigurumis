document.addEventListener("DOMContentLoaded", () => {

    const btnAbrirMenu =
        document.getElementById("btnAbrirMenu");

    const btnFecharMenu =
        document.getElementById("btnFecharMenu");

    const menuLateral =
        document.getElementById("menuLateral");

    const sobreposicaoMenu =
        document.getElementById("sobreposicaoMenu");


    if (
        !btnAbrirMenu ||
        !btnFecharMenu ||
        !menuLateral ||
        !sobreposicaoMenu
    ) {
        return;
    }


    function abrirMenu() {

        menuLateral.classList.add("aberto");

        sobreposicaoMenu.classList.add("visivel");

        document.body.classList.add("menu_aberto");

        btnAbrirMenu.setAttribute(
            "aria-expanded",
            "true"
        );

        sobreposicaoMenu.setAttribute(
            "aria-hidden",
            "false"
        );

        btnAbrirMenu.style.display = "none";

        btnFecharMenu.style.display = "flex";

        btnFecharMenu.focus();
    }


    function fecharMenu() {

        menuLateral.classList.remove("aberto");

        sobreposicaoMenu.classList.remove("visivel");

        document.body.classList.remove("menu_aberto");

        btnAbrirMenu.setAttribute(
            "aria-expanded",
            "false"
        );

        sobreposicaoMenu.setAttribute(
            "aria-hidden",
            "true"
        );

        btnFecharMenu.style.display = "none";

        btnAbrirMenu.style.display = "flex";
    }


    btnAbrirMenu.addEventListener(
        "click",
        abrirMenu
    );


    btnFecharMenu.addEventListener(
        "click",
        fecharMenu
    );


    sobreposicaoMenu.addEventListener(
        "click",
        fecharMenu
    );


    document.addEventListener(
        "keydown",
        (evento) => {

            if (
                evento.key === "Escape" &&
                menuLateral.classList.contains("aberto")
            ) {

                fecharMenu();
            }
        }
    );


    const itensMenu =
        document.querySelectorAll(".menu_item");


    itensMenu.forEach((item) => {

        item.addEventListener(
            "click",
            () => {

                const href =
                    item.getAttribute("href");

                if (
                    href &&
                    href !== "#"
                ) {

                    fecharMenu();
                }
            }
        );
    });


    /* Estado inicial */

    fecharMenu();
});