from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr

from src.database.models import UserRole


class ContactModel(BaseModel):
    """
    Модель для створення або оновлення контакту.

    Атрибути:
        name: ім'я контакту (мінімум 2 символи, максимум 50 символів)
        surname: прізвище контакту (мінімум 2 символи, максимум 50 символів)
        email: електронна пошта контакту (мінімум 7 символів, максимум 100 символів)
        phone: номер телефону контакту (мінімум 7 символів, максимум 20 символів)
        birthday: дата народження контакту
        info: додаткові відомості про контакт (необов'язково)
    """

    name: str = Field(min_length=2, max_length=50)
    surname: str = Field(min_length=2, max_length=50)
    email: EmailStr = Field(min_length=7, max_length=100)
    phone: str = Field(min_length=7, max_length=20)
    birthday: date
    info: Optional[str] = None


class ContactResponse(ContactModel):
    """
    Модель для відповіді при отриманні контакту з бази даних.

    Атрибути:
        id: унікальний ідентифікатор контакту
        created_at: дата та час створення контакту
        updated_at: дата та час останнього оновлення контакту (необов'язково)
    """

    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    """
    Модель для представлення користувача.

    Атрибути:
        id: унікальний ідентифікатор користувача
        username: ім'я користувача
        email: електронна пошта користувача
        avatar: URL до аватарки користувача
        role: роль користувача (наприклад, адміністратор чи користувач)
    """

    id: int
    username: str
    email: str
    avatar: str
    role: UserRole
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Модель для створення нового користувача.

    Атрибути:
        username: ім'я користувача
        email: електронна пошта користувача
        password: пароль користувача (мінімум 4 символи, максимум 128 символів)
        role: роль користувача (наприклад, адміністратор чи користувач)
    """

    username: str
    email: str
    password: str = Field(min_length=4, max_length=128)
    role: UserRole


class Token(BaseModel):
    """
    Модель для повернення токену доступу.

    Атрибути:
        access_token: токен доступу
        token_type: тип токену (наприклад, Bearer)
    """

    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    Модель для запиту електронної пошти для відновлення паролю.

    Атрибут:
        email: електронна пошта користувача
    """

    email: EmailStr


class ResetPassword(BaseModel):
    """
    Модель для скидання паролю.

    Атрибути:
        email: електронна пошта користувача
        password: новий пароль користувача (мінімум 4 символи, максимум 128 символів)
    """

    email: EmailStr
    password: str = Field(min_length=4, max_length=128, description="Новий пароль")
