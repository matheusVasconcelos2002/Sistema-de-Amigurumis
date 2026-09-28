import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv


load_dotenv()


class EmailService:

    SERVIDOR_SMTP = "smtp.gmail.com"
    PORTA_SMTP = 587

    @staticmethod
    def enviar_email(destinatario, assunto, mensagem_html):
        email_remetente = os.getenv("EMAIL_REMETENTE")
        senha_aplicativo = os.getenv("SENHA_APLICATIVO")

        if not email_remetente:
            raise ValueError(
                "A variável EMAIL_REMETENTE não foi configurada."
            )

        if not senha_aplicativo:
            raise ValueError(
                "A variável SENHA_APLICATIVO não foi configurada."
            )

        mensagem = MIMEMultipart("alternative")

        mensagem["From"] = email_remetente
        mensagem["To"] = destinatario
        mensagem["Subject"] = assunto

        corpo_html = MIMEText(
            mensagem_html,
            "html",
            "utf-8"
        )

        mensagem.attach(corpo_html)

        with smtplib.SMTP(
            EmailService.SERVIDOR_SMTP,
            EmailService.PORTA_SMTP
        ) as servidor:

            servidor.ehlo()
            servidor.starttls()
            servidor.ehlo()

            servidor.login(
                email_remetente,
                senha_aplicativo
            )

            servidor.sendmail(
                email_remetente,
                destinatario,
                mensagem.as_string()
            )

    @staticmethod
    def enviar_recuperacao(destinatario, nome, link):
        assunto = "Recuperação de senha - Sistema de Amigurumis"

        mensagem_html = f"""
        <html>
            <body>
                <h2>Recuperação de senha</h2>

                <p>Olá, {nome}!</p>

                <p>
                    Recebemos uma solicitação para redefinir
                    a senha da sua conta no Sistema de Amigurumis.
                </p>

                <p>
                    Clique no botão abaixo para criar uma nova senha:
                </p>

                <p>
                    <a href="{link}">
                        Redefinir minha senha
                    </a>
                </p>

                <p>
                    Se você não solicitou a recuperação da senha,
                    ignore este e-mail.
                </p>

                <p>
                    Sistema de Amigurumis
                </p>
            </body>
        </html>
        """

        EmailService.enviar_email(
            destinatario=destinatario,
            assunto=assunto,
            mensagem_html=mensagem_html
        )