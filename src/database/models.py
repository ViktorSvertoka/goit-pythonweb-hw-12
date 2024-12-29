from enum import Enum
from sqlalchemy import (
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    Column,
    ForeignKey,
    func,
    Enum as SqlEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class UserRole(str, Enum):
    """
    Перерахунок ролей користувачів.

    Значення:
    - USER: Звичайний користувач.
    - ADMIN: Адміністратор.
    """

    USER = "user"
    ADMIN = "admin"


class Contact(Base):
    """
    Модель для таблиці 'contacts'.

    Атрибути:
    - id: Первинний ключ.
    - name: Ім'я контакту (обов'язкове).
    - surname: Прізвище контакту (обов'язкове).
    - email: Електронна пошта контакту (унікальна, обов'язкова).
    - phone: Телефонний номер контакту (унікальний, обов'язковий).
    - birthday: Дата народження контакту (обов'язкова).
    - created_at: Дата створення запису (автоматично).
    - updated_at: Дата останнього оновлення запису (автоматично).
    - info: Додаткова інформація про контакт.
    - user_id: Зовнішній ключ для прив'язки до користувача.
    - user: Відношення до моделі User.
    """

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(20), nullable=False, unique=True)
    birthday = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    info = Column(String(500), nullable=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", backref="contacts")


class User(Base):
    """
    Модель для таблиці 'users'.

    Атрибути:
    - id: Первинний ключ.
    - username: Унікальне ім'я користувача.
    - email: Унікальна електронна пошта.
    - hashed_password: Зашифрований пароль.
    - created_at: Дата створення запису (автоматично).
    - avatar: URL-адреса аватара користувача.
    - confirmed: Чи підтверджений користувач.
    - role: Роль користувача (USER або ADMIN).
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)
