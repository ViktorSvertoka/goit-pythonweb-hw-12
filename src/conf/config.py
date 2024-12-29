from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Клас конфігурації для налаштувань додатка.

    Цей клас автоматично завантажує налаштування з середовища або файлу `.env`, використовуючи бібліотеку Pydantic.

    Атрибути:
    - DB_URL (str): URL для підключення до бази даних.
    - JWT_SECRET (str): Секретний ключ для підпису JWT-токенів.
    - JWT_ALGORITHM (str): Алгоритм для генерації JWT-токенів (за замовчуванням: HS256).
    - JWT_EXPIRATION_SECONDS (int): Час життя токенів у секундах (за замовчуванням: 3600).
    - MAIL_USERNAME (EmailStr): Логін для SMTP сервера.
    - MAIL_PASSWORD (str): Пароль для SMTP сервера.
    - MAIL_FROM (EmailStr): Електронна адреса, від якої надсилаються листи.
    - MAIL_PORT (int): Порт для підключення до SMTP сервера.
    - MAIL_SERVER (str): Доменне ім'я SMTP сервера.
    - MAIL_FROM_NAME (str): Ім'я відправника для листів (за замовчуванням: "API Service").
    - MAIL_STARTTLS (bool): Чи використовувати STARTTLS для SMTP (за замовчуванням: False).
    - MAIL_SSL_TLS (bool): Чи використовувати SSL/TLS для SMTP (за замовчуванням: True).
    - USE_CREDENTIALS (bool): Чи використовувати облікові дані для SMTP (за замовчуванням: True).
    - VALIDATE_CERTS (bool): Чи перевіряти сертифікати SSL (за замовчуванням: True).
    - CLOUDINARY_NAME (str): Ім'я облікового запису Cloudinary.
    - CLOUDINARY_API_KEY (int): API-ключ для Cloudinary.
    - CLOUDINARY_API_SECRET (str): Секретний ключ для Cloudinary.

    Методи:
    - model_config: Конфігурація для завантаження налаштувань із файлу `.env`.

    Приклад використання:
    ```
    from src.conf.config import settings
    print(settings.DB_URL)
    ```
    """

    DB_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600

    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str = "API Service"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: int
    CLOUDINARY_API_SECRET: str

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


# Ініціалізація об'єкта налаштувань
settings = Settings()
