from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Отримати користувача за його ID.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Отримати користувача за його ім'ям користувача.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Отримати користувача за його email.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Створити нового користувача.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Підтвердити email користувача.
        """
        user = await self.get_user_by_email(email)
        if user:
            user.confirmed = True
            await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Оновити URL аватару користувача.
        """
        user = await self.get_user_by_email(email)
        if user:
            user.avatar = url
            await self.db.commit()
            await self.db.refresh(user)
        return user

    async def reset_password(self, user_id: int, password: str) -> User:
        """
        Скинути пароль користувача.
        """
        user = await self.get_user_by_id(user_id)
        if user:
            user.hashed_password = password
            await self.db.commit()
            await self.db.refresh(user)
        return user
