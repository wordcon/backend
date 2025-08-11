from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Sequence
from uuid import UUID

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from litestar.exceptions import NotAuthorizedException, PermissionDeniedException

from app.domains.games.constants import (
    ERR_NO_PLAYERS_IN_ROOM,
    ERR_NOT_IN_GAME,
    ERR_ONLY_OWNER_CAN_START,
    ERR_ROOM_NOT_OPEN,
)
from app.domains.games.models import GameModel, GamePlayerModel, GameState
from app.domains.games.schemas import Game, GamePlace, GamePoint
from app.domains.rooms.models import RoomModel, RoomPlayerModel, RoomStatus
from app.domains.rooms.services import RoomPlayerRepository, RoomRepository


class GameRepository(SQLAlchemyAsyncRepository[GameModel]):
    model_type = GameModel


class GamePlayerRepository(SQLAlchemyAsyncRepository[GamePlayerModel]):
    model_type = GamePlayerModel


@dataclass
class _TimeInfo:
    now: datetime
    elapsed: int
    left: int


class GameService(SQLAlchemyAsyncRepositoryService[GameModel]):
    repository_type = GameRepository

    def _players_repo(self) -> GamePlayerRepository:
        return GamePlayerRepository(session=self.repository.session)

    def _rooms_repo(self) -> RoomRepository:
        return RoomRepository(session=self.repository.session)

    def _room_players_repo(self) -> RoomPlayerRepository:
        return RoomPlayerRepository(session=self.repository.session)

    async def get_game(self, game_id: UUID) -> GameModel:
        return await self.repository.get(game_id)

    async def start_game(self, room_id: UUID, actor_id: UUID) -> GameModel:
        rooms_repo = self._rooms_repo()
        room_players_repo = self._room_players_repo()

        room = await rooms_repo.get(room_id)

        if room.room_owner_id != actor_id:
            raise PermissionDeniedException(detail=ERR_ONLY_OWNER_CAN_START)
        if room.status != RoomStatus.OPEN.value:
            raise NotAuthorizedException(detail=ERR_ROOM_NOT_OPEN)

        players: Sequence[RoomPlayerModel] = await room_players_repo.list(RoomPlayerModel.room_id == room_id)
        if not players:
            raise NotAuthorizedException(detail=ERR_NO_PLAYERS_IN_ROOM)

        now = datetime.now(timezone.utc)

        game = await super().create(
            {
                'room_id': room.id,
                'state': GameState.RUNNING.value,
                'round': 1,
                'turn_time': room.turn_time,
                'last_tick_at': now,
                'end_date': None,
            }
        )

        gplayers_repo = self._players_repo()
        await gplayers_repo.add_many(
            [
                GamePlayerModel(
                    game_id=game.id,
                    user_id=rp.user_id,
                    points=0,
                    place=None,
                )
                for rp in players
            ],
        )

        await rooms_repo.get_and_update(
            RoomModel.id == room.id,
            attribute_names=('status',),
            status=RoomStatus.IN_GAME.value,
        )

        return await self.get_game(game.id)

    async def tick(self, game_id: UUID, actor_id: UUID) -> GameModel:
        game = await self.get_game(game_id)
        room = game.room
        if room.room_owner_id != actor_id:
            raise PermissionDeniedException(detail='Only room owner can tick the game')

        if game.state != GameState.RUNNING.value:
            return game

        t = self._compute_time(game)
        now = t.now

        new_round = game.round
        if t.left <= 0:
            new_round = game.round + 1

        await self.repository.get_and_update(
            GameModel.id == game.id,
            attribute_names=('round', 'last_tick_at'),
            round=new_round,
            last_tick_at=now,
        )

        return await self.get_game(game.id)

    async def guess(self, game_id: UUID, user_id: UUID, text: str) -> GameModel:
        game = await self.get_game(game_id)
        if game.state != GameState.RUNNING.value:
            return game

        gplayers_repo = self._players_repo()
        gplayer = await gplayers_repo.get_one_or_none(game_id=game_id, user_id=user_id)
        if not gplayer:
            raise NotAuthorizedException(detail=ERR_NOT_IN_GAME)

        await gplayers_repo.get_and_update(
            GamePlayerModel.id == gplayer.id,
            attribute_names=('points',),
            points=gplayer.points + 1,
        )

        return await self.get_game(game_id)

    def _compute_time(self, game: GameModel) -> _TimeInfo:
        now = datetime.now(timezone.utc)
        elapsed = int((now - game.last_tick_at).total_seconds())
        left = max(game.turn_time - elapsed, 0) if game.state == GameState.RUNNING.value else 0
        return _TimeInfo(now=now, elapsed=elapsed, left=left)

    async def _compute_places(self, game: GameModel) -> list[GamePlace]:
        explicit = [p for p in game.players if p.place is not None]
        if explicit and len(explicit) == len(game.players):
            return sorted(
                [GamePlace(user_id=p.user_id, place=int(p.place)) for p in explicit],
                key=lambda x: x.place,
            )

        ranked = sorted(
            game.players,
            key=lambda p: (-p.points, p.created_at),
        )
        places: list[GamePlace] = []
        place = 1
        last_points = None
        for idx, gp in enumerate(ranked):
            if last_points is None or gp.points < last_points:
                place = idx + 1
                last_points = gp.points
            places.append(GamePlace(user_id=gp.user_id, place=place))
        return places

    async def to_game_schema(self, game: GameModel) -> Game:
        t = self._compute_time(game)

        points: Iterable[GamePoint] = [
            GamePoint(user_id=gp.user_id, value=gp.points) for gp in sorted(game.players, key=lambda p: p.user_id.hex)
        ]
        places = await self._compute_places(game)

        return Game(
            id=game.id,
            room_id=game.room_id,
            name=game.room.name if game.room else '',
            state=game.state,
            round=game.round,
            turn_time=game.turn_time,
            time_left=t.left,
            points=list(points),
            places=places,
            end_date=game.end_date,
        )
