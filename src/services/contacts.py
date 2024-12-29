from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.openapi.models import Contact

from src.database.models import User
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel


class ContactService:
    """
    Сервіс для роботи з контактами користувача. Дозволяє створювати, оновлювати, видаляти та отримувати контакти.
    """

    def __init__(self, db: AsyncSession):
        """
        Ініціалізує сервіс з підключенням до бази даних.

        Аргументи:
            db: підключення до асинхронної сесії бази даних.
        """
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """
        Створює новий контакт.

        Перевіряє, чи існує контакт з таким email або номером телефону. Якщо такий контакт існує, викликає помилку.

        Аргументи:
            body: модель даних для створення контакту.
            user: поточний користувач, який створює контакт.

        Повертає:
            Створений контакт.

        Викидає:
            HTTPException, якщо контакт з таким email або телефоном вже існує.
        """
        if await self.repository.is_contact_exists(body.email, body.phone, user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contact with '{body.email}' email or '{body.phone}' phone number already exists.",
            )
        return await self.repository.create_contact(body, user)

    async def get_contacts(
        self, name: str, surname: str, email: str, skip: int, limit: int, user: User
    ) -> List[Contact]:
        """
        Отримує список контактів з можливістю фільтрації за параметрами.

        Аргументи:
            name: ім'я контакту для фільтрації.
            surname: прізвище контакту для фільтрації.
            email: електронна пошта контакту для фільтрації.
            skip: кількість контактів для пропуску (пагінація).
            limit: максимальна кількість контактів для отримання.
            user: поточний користувач для перевірки доступу до контактів.

        Повертає:
            Список контактів, що задовольняють умови фільтрації.
        """
        return await self.repository.get_contacts(
            name, surname, email, skip, limit, user
        )

    async def get_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Отримує контакт за його ID.

        Аргументи:
            contact_id: унікальний ідентифікатор контакту.
            user: поточний користувач для перевірки доступу до контакту.

        Повертає:
            Контакт або None, якщо контакт не знайдений.
        """
        return await self.repository.get_contact_by_id(contact_id, user)

    async def update_contact(
        self, contact_id: int, body: ContactModel, user: User
    ) -> Contact:
        """
        Оновлює дані контакту за його ID.

        Аргументи:
            contact_id: унікальний ідентифікатор контакту.
            body: нові дані для оновлення контакту.
            user: поточний користувач для перевірки доступу до контакту.

        Повертає:
            Оновлений контакт.
        """
        return await self.repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User) -> Contact:
        """
        Видаляє контакт за його ID.

        Аргументи:
            contact_id: унікальний ідентифікатор контакту.
            user: поточний користувач для перевірки доступу до контакту.

        Повертає:
            Видалений контакт.
        """
        return await self.repository.remove_contact(contact_id, user)

    async def get_upcoming_birthdays(self, days: int, user: User) -> List[Contact]:
        """
        Отримує список контактів з найближчими днями народження (за кількість днів).

        Аргументи:
            days: кількість днів для фільтрації найближчих днів народження.
            user: поточний користувач для перевірки доступу до контактів.

        Повертає:
            Список контактів з найближчими днями народження.
        """
        return await self.repository.get_upcoming_birthdays(days, user)
