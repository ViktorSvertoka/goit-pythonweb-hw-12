from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db

router = APIRouter(tags=["utils"])


@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Перевірка здоров'я сервісу та підключення до бази даних.

    Цей ендпоінт виконує простий запит до бази даних, щоб перевірити, чи налаштована база даних коректно,
    і чи може додаток успішно до неї підключатися.

    Параметри:
    - db (AsyncSession): Асинхронна сесія бази даних, отримана через залежність.

    Повертає:
    - dict: Повідомлення про стан сервісу.

    Випадки помилок:
    - 500 INTERNAL_SERVER_ERROR: Якщо база даних не налаштована або виникає помилка під час підключення.
    """
    try:
        # Виконуємо тестовий запит до бази даних
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )

        # Успішна відповідь, якщо запит виконався
        return {"message": "Welcome to FastAPI!"}

    except Exception as e:
        # Логування помилки та повернення повідомлення про невдачу
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )
