import os
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText

from backend.logger import logger

load_dotenv()

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

msg = MIMEText("Teste de envio de email", "plain")
msg["Subject"] = "Teste SMTP"
msg["From"] = SMTP_USER
msg["To"] = SMTP_USER

logger.info("SMTP_USER: %s", SMTP_USER)
logger.info("SMTP_PASSWORD existe? %s", bool(SMTP_PASSWORD))
logger.info(
    "Tamanho da senha: %s",
    len(SMTP_PASSWORD) if SMTP_PASSWORD else None,
)

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

    logger.info("Email enviado com sucesso!")

except Exception as e:
    logger.exception("Erro ao enviar email")
