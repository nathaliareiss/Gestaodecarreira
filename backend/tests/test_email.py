import os
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

msg = MIMEText("Teste de envio de email", "plain")
msg["Subject"] = "Teste SMTP"
msg["From"] = SMTP_USER
msg["To"] = SMTP_USER
    
print("SMTP_USER:", SMTP_USER)
print("SMTP_PASSWORD existe?", bool(SMTP_PASSWORD))
print("Tamanho da senha:", len(SMTP_PASSWORD) if SMTP_PASSWORD else None)

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

    print("Email enviado com sucesso!")

except Exception as e:
    print("Erro ao enviar email:")
    print(e)