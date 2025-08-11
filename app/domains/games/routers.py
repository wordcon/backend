from typing import Any
from uuid import UUID

from dishka.integrations.litestar import FromDishka
from litestar import Controller, Request, get, post
from litestar.security.jwt import Token

from app.domains.games.schemas import Game, GuessRequest
from app.domains.games.services import GameService
from app.domains.users.schemas import User


class RoomGamesController(Controller):
    path = '/rooms'
    tags = ['games']

    @post('/{room_id:uuid}/start')
    async def start_game(
        self,
        request: Request[User, Token, Any],
        games_service: FromDishka[GameService],
        room_id: UUID,
    ) -> Game:
        game = await games_service.start_game(room_id=room_id, actor_id=request.user.id)
        return await games_service.to_game_schema(game)


class GamesController(Controller):
    path = '/games'
    tags = ['games']

    @get('/{game_id:uuid}')
    async def get_game(self, games_service: FromDishka[GameService], game_id: UUID) -> Game:
        game = await games_service.get_game(game_id)
        return await games_service.to_game_schema(game)

    @post('/{game_id:uuid}/guess')
    async def send_guess(
        self,
        request: Request[User, Token, Any],
        games_service: FromDishka[GameService],
        game_id: UUID,
        data: GuessRequest,
    ) -> Game:
        game = await games_service.guess(game_id=game_id, user_id=request.user.id, text=data.text)
        return await games_service.to_game_schema(game)

    @post('/{game_id:uuid}/tick')
    async def tick_game(
        self,
        request: Request[User, Token, Any],
        games_service: FromDishka[GameService],
        game_id: UUID,
    ) -> Game:
        game = await games_service.tick(game_id=game_id, actor_id=request.user.id)
        return await games_service.to_game_schema(game)
