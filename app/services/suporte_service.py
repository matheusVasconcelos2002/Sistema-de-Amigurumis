from urllib.parse import quote


class SuporteService:

    EMAIL_SUPORTE = "mvds.lic22@uea.edu.br"
    ASSUNTO_EMAIL = "Suporte - Sistema de Amigurumis"

    @staticmethod
    def obter_email():
        return SuporteService.EMAIL_SUPORTE

    @staticmethod
    def obter_assunto():
        return SuporteService.ASSUNTO_EMAIL

    @staticmethod
    def gerar_link_contato():
        assunto = quote(SuporteService.ASSUNTO_EMAIL)

        return (
            f"mailto:{SuporteService.EMAIL_SUPORTE}"
            f"?subject={assunto}"
        )

    @staticmethod
    def obter_dados():
        return {
            "email": SuporteService.obter_email(),
            "assunto": SuporteService.obter_assunto(),
            "link_contato": SuporteService.gerar_link_contato(),
        }