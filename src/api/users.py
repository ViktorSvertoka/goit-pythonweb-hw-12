from fastapi import APIRouter, Depends, Request, UploadFile, File
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.db import get_db
from src.schemas import User
from src.services.auth import get_current_user, get_current_admin_user
from src.services.upload_file import UploadFileService
from src.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me", response_model=User, description="No more than 10 requests per minute"
)
@limiter.limit("10 per minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Отримання інформації про поточного авторизованого користувача.

    Обмеження:
    - Не більше 10 запитів на хвилину.

    Параметри:
    - request (Request): HTTP-запит для відстеження ліміту.
    - user (User): Поточний авторизований користувач.

    Повертає:
    - User: Дані користувача.
    """
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Оновлення аватара для поточного адміністратора.

    Параметри:
    - file (UploadFile): Завантажений файл аватара.
    - user (User): Поточний авторизований адміністратор.
    - db (AsyncSession): Сесія бази даних.

    Повертає:
    - User: Оновлені дані користувача з новим URL аватара.
    """
    # Завантаження аватара на хмарне сховище
    avatar_service = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    )
    avatar_url = avatar_service.upload_file(file, user.username)

    # Оновлення URL аватара в базі даних
    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
