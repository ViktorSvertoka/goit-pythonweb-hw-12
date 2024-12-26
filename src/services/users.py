from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar
from src.database.models import User
from src.repository.users import UserRepository
from src.schemas import UserCreate


class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate) -> User:
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str) -> User | None:
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str) -> None:
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str) -> User:
        return await self.repository.update_avatar_url(email, url)

    async def reset_password(self, user_id: int, password: str) -> User:

        return await self.repository.reset_password(user_id, password)
