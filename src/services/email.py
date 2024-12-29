from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import create_email_token
from src.conf.config import settings

# Налаштування конфігурації для підключення до сервера електронної пошти
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_confirm_email(to_email: EmailStr, username: str, host: str) -> None:
    """
    Відправляє електронну пошту для підтвердження адреси електронної пошти.

    Створює токен для підтвердження електронної пошти та надсилає лист користувачеві
    з посиланням для підтвердження електронної пошти.

    Аргументи:
        to_email: Адреса електронної пошти отримувача.
        username: Ім'я користувача для персоналізації листа.
        host: Хост (домашня адреса), який використовується для побудови посилання.

    Викидає:
        ConnectionErrors: Якщо виникає помилка під час підключення до сервера електронної пошти.
    """
    try:
        # Створення токену для підтвердження електронної пошти
        token_verification = create_email_token({"sub": to_email})
        # Формування повідомлення для відправки
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[to_email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        # Ініціалізація FastMail та відправка повідомлення
        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)


async def send_reset_password_email(
    to_email: EmailStr, username: str, host: str, reset_token: str
) -> None:
    """
    Відправляє електронну пошту для скидання пароля.

    Формує посилання для скидання пароля і надсилає користувачу лист з інструкцією
    для зміни пароля.

    Аргументи:
        to_email: Адреса електронної пошти отримувача.
        username: Ім'я користувача для персоналізації листа.
        host: Хост (домашня адреса), який використовується для побудови посилання.
        reset_token: Токен для скидання пароля, що додається до посилання.

    Викидає:
        ConnectionErrors: Якщо виникає помилка під час підключення до сервера електронної пошти.
    """
    try:
        # Формування посилання для скидання пароля
        reset_link = f"{host}api/auth/confirm_reset_password/{reset_token}"

        # Формування повідомлення для відправки
        message = MessageSchema(
            subject="Important: Update your account information",
            recipients=[to_email],
            template_body={"reset_link": reset_link, "username": username},
            subtype=MessageType.html,
        )

        # Ініціалізація FastMail та відправка повідомлення
        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
    except ConnectionErrors as err:
        print(err)
