from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import ContactModel, ContactResponse, User
from src.services.auth import get_current_user
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/birthdays", response_model=List[ContactResponse])
async def get_upcoming_birthdays(
    days: int = Query(default=7, ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Отримання списку контактів, які мають день народження протягом вказаної кількості днів.

    Параметри:
    - days (int): Кількість днів для пошуку (мінімум 1).
    - db (AsyncSession): Сесія бази даних.
    - user (User): Поточний авторизований користувач.

    Повертає:
    - List[ContactResponse]: Список контактів із найближчими днями народження.
    """
    contact_service = ContactService(db)
    return await contact_service.get_upcoming_birthdays(days, user)


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    name: str = "",
    surname: str = "",
    email: str = "",
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Пошук контактів за фільтрами.

    Параметри:
    - name (str): Ім'я контакту (необов'язкове).
    - surname (str): Прізвище контакту (необов'язкове).
    - email (str): Email контакту (необов'язкове).
    - skip (int): Кількість записів, які потрібно пропустити (за замовчуванням 0).
    - limit (int): Максимальна кількість записів, які потрібно повернути (за замовчуванням 100).
    - db (AsyncSession): Сесія бази даних.
    - user (User): Поточний авторизований користувач.

    Повертає:
    - List[ContactResponse]: Список контактів, які відповідають критеріям пошуку.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(
        name, surname, email, skip, limit, user
    )
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Отримання інформації про контакт за його ID.

    Параметри:
    - contact_id (int): ID контакту.
    - db (AsyncSession): Сесія бази даних.
    - user (User): Поточний авторизований користувач.

    Повертає:
    - ContactResponse: Дані контакту.

    Викликає:
    - HTTPException (404): Якщо контакт не знайдено.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Створення нового контакту.

    Параметри:
    - body (ContactModel): Дані нового контакту.
    - db (AsyncSession): Сесія бази даних.
    - user (User): Поточний авторизований користувач.

    Повертає:
    - ContactResponse: Дані створеного контакту.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactModel,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Оновлення даних контакту за його ID.

    Параметри:
    - body (ContactModel): Нові дані контакту.
    - contact_id (int): ID контакту.
    - db (AsyncSession): Сесія бази даних.
    - user (User): Поточний авторизований користувач.

    Повертає:
    - ContactResponse: Оновлені дані контакту.

    Викликає:
    - HTTPException (404): Якщо контакт не знайдено.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Видалення контакту за його ID.

    Параметри:
    - contact_id (int): ID контакту.
    - db (AsyncSession): Сесія бази даних.
    - user (User): Поточний авторизований користувач.

    Повертає:
    - ContactResponse: Дані видаленого контакту.

    Викликає:
    - HTTPException (404): Якщо контакт не знайдено.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
