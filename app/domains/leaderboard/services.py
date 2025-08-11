from typing import Sequence

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from app.domains.users.models import UserModel


class LeaderboardRepository(SQLAlchemyAsyncRepository[UserModel]):
    model_type = UserModel


class LeaderboardService(SQLAlchemyAsyncRepositoryService[UserModel]):
    repository_type = LeaderboardRepository

    async def list_top_users(self, limit: int = 100, offset: int = 0) -> Sequence[UserModel]:
        return await self.repository.list(
            order_by=[('points', True), ('username', False)],
            limit=limit,
            offset=offset,
        )
