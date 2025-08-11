from dishka.integrations.litestar import FromDishka
from litestar import Controller, get

from app.domains.leaderboard.schemas import LeaderboardEntry
from app.domains.leaderboard.services import LeaderboardService


class LeaderboardController(Controller):
    path = '/leaderboard'
    tags = ['leaderboard']

    @get()
    async def get_leaderboard(
        self,
        leaderboard_service: FromDishka[LeaderboardService],
        limit: int = 100,
        offset: int = 0,
    ) -> list[LeaderboardEntry]:
        users = await leaderboard_service.list_top_users(limit=limit, offset=offset)
        return [
            LeaderboardEntry(
                username=u.username,
                avatar_url=u.avatar_url,
                points=u.points,
                place=offset + i + 1,
            )
            for i, u in enumerate(users)
        ]
