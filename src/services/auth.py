from datetime import datetime, timedelta, timezone
from typing import Optional
from aiocache import cached
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_db
from src.database.models import User, UserRole
from src.conf.config import settings
from src.services.users import UserService


class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password) -> bool:
        """
        Перевіряє, чи співпадає відкритий пароль з захешованим.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Генерує хеш для пароля.
        """
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Створює токен доступу з переданими даними та часом життя.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            seconds=settings.JWT_EXPIRATION_SECONDS
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def cache_key_builder(func, args, kwargs) -> str:
    """
    Генерує ключ для кешування за допомогою імені користувача.
    """
    return f"username: {args[0]}"


@cached(ttl=300, key_builder=cache_key_builder)
async def get_user_from_db(username: str, db: AsyncSession) -> User:
    """
    Отримує користувача з бази даних, використовуючи кешування.
    """
    print("NOT CACHED USER")
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)

    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """
    Отримує поточного користувача на основі наданого токену.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Перевіряє, чи є поточний користувач адміністратором.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Permission denied")
    return current_user


def create_email_token(data: dict) -> str:
    """
    Створює токен для перевірки електронної пошти.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def get_email_from_token(token: str) -> str:
    """
    Отримує email з токену для підтвердження електронної пошти.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неправильний токен для перевірки електронної пошти",
        )


async def get_password_from_token(token: str) -> str:
    """
    Отримує пароль з токену для скидання пароля.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        password = payload["password"]
        return password
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Wrong token",
        )
