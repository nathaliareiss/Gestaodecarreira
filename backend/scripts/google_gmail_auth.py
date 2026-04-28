from __future__ import annotations

from backend.services.email_service import autorizar_gmail_interativamente


def main() -> None:
    caminho = autorizar_gmail_interativamente()
    print(f"Token do Gmail salvo em: {caminho}")
    print("Agora o backend ja pode enviar emails de confirmacao pelo Gmail API.")


if __name__ == "__main__":
    main()

