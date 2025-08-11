from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.litestar import LitestarProvider
from litestar import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import sqlalchemy_config
from app.core.settings import Settings, settings
from app.domains.games.services import GameService
from app.domains.leaderboard.services import LeaderboardService
from app.domains.rooms.services import RoomService
from app.domains.users.services import UserService


class AppProvider(Provider):
    scope = Scope.APP

    @provide
    def get_settings(self) -> Settings:
        return settings


class RequestProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_session(self, request: Request) -> AsyncSession:
        return sqlalchemy_config.provide_session(state=request.app.state, scope=request.scope)


class ServicesProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def user_service(self, session: AsyncSession) -> UserService:
        return UserService(session=session)

    @provide
    def room_service(self, session: AsyncSession) -> RoomService:
        return RoomService(session=session)

    @provide
    def game_service(self, session: AsyncSession) -> GameService:
        return GameService(session=session)

    @provide
    def leaderboard_service(self, session: AsyncSession) -> LeaderboardService:
        return LeaderboardService(session=session)


container = make_async_container(
    AppProvider(),
    RequestProvider(),
    ServicesProvider(),
    LitestarProvider(),
)
