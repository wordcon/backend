from typing import Any, Iterable, Sequence
from uuid import UUID

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from litestar.exceptions import (
    NotAuthorizedException,
    NotFoundException,
    PermissionDeniedException,
)

from app.core import crypt
from app.domains.rooms.constants import (
    ERR_INVALID_ROOM_PASSWORD,
    ERR_ONLY_OWNER_DELETE,
    ERR_ONLY_OWNER_KICK,
    ERR_ONLY_OWNER_UPDATE,
    ERR_OWNER_CANNOT_KICK_SELF,
    ERR_PASSWORD_REQUIRED,
    ERR_PLAYER_NOT_IN_ROOM,
    ERR_ROOM_FULL,
    ERR_ROOM_NOT_FOUND,
)
from app.domains.rooms.models import RoomModel, RoomPlayerModel, RoomStatus
from app.domains.rooms.schemas import Player, Room
from app.domains.users.schemas import UserPublic
from app.domains.users.services import UserService


class RoomRepository(SQLAlchemyAsyncRepository[RoomModel]):
    model_type = RoomModel


class RoomPlayerRepository(SQLAlchemyAsyncRepository[RoomPlayerModel]):
    model_type = RoomPlayerModel


class RoomService(SQLAlchemyAsyncRepositoryService[RoomModel]):
    repository_type = RoomRepository

    def _players_repo(self) -> RoomPlayerRepository:
        return RoomPlayerRepository(session=self.repository.session)

    async def create_room(self, owner_id: UUID, data: dict[str, Any]) -> RoomModel:
        password = data.pop('password', None)
        hashed_password: str | None = None
        has_password = False
        if password:
            hashed_password = await crypt.get_password_hash(password)
            has_password = True

        room = await self.repository.add(
            RoomModel(
                name=data['name'],
                category=data['category'],
                room_owner_id=owner_id,
                players_limit=int(data['players_limit']),
                turn_time=int(data['turn_time']),
                is_private=bool(data.get('is_private', False)),
                has_password=has_password,
                hashed_password=hashed_password,
                status=RoomStatus.OPEN.value,
            ),
            auto_refresh=True,
        )

        await self._players_repo().add(
            RoomPlayerModel(room_id=room.id, user_id=owner_id, is_owner=True),
            auto_refresh=False,
        )

        return await self.repository.get(room.id)

    async def list_rooms(
        self,
        category: str | None = None,
        q: str | None = None,
        status: str | None = None,
    ) -> Sequence[RoomModel]:
        filters = []
        if category:
            filters.append(RoomModel.category == category)
        if q:
            filters.append(RoomModel.name.ilike(f'%{q}%'))
        if status:
            filters.append(RoomModel.status == status)

        rooms = await self.repository.list(
            *filters,
            order_by=[('created_at', True)],
        )
        return rooms

    async def get_room(self, room_id: UUID) -> RoomModel:
        try:
            return await self.repository.get(room_id)
        except Exception as err:
            raise NotFoundException(ERR_ROOM_NOT_FOUND) from err

    async def update_room(self, room_id: UUID, actor_id: UUID, data: dict[str, Any]) -> RoomModel:
        room = await self.get_room(room_id)
        if room.room_owner_id != actor_id:
            raise PermissionDeniedException(ERR_ONLY_OWNER_UPDATE)

        patch: dict[str, Any] = {}

        if 'password' in data:
            password = data.pop('password')
            if not password:
                patch['hashed_password'] = None
                patch['has_password'] = False
            else:
                patch['hashed_password'] = await crypt.get_password_hash(password)
                patch['has_password'] = True

        for field in ('name', 'players_limit', 'turn_time', 'category', 'status'):
            if field in data and data[field] is not None:
                patch[field] = data[field]

        if patch:
            await super().update(item_id=room_id, data=patch, attribute_names=patch.keys())

        return await self.get_room(room_id)

    async def delete_room(self, room_id: UUID, actor_id: UUID) -> None:
        room = await self.get_room(room_id)
        if room.room_owner_id != actor_id:
            raise PermissionDeniedException(ERR_ONLY_OWNER_DELETE)
        await self.repository.delete(room_id)

    async def join_room(self, room_id: UUID, user_id: UUID, password: str | None = None) -> RoomModel:
        room = await self.get_room(room_id)

        players_repo = self._players_repo()

        if await players_repo.exists(room_id=room_id, user_id=user_id):
            return room

        current_players = await players_repo.count(room_id=room_id)
        if current_players >= room.players_limit:
            raise NotAuthorizedException(detail=ERR_ROOM_FULL)

        if room.has_password:
            if not password:
                raise NotAuthorizedException(detail=ERR_PASSWORD_REQUIRED)
            if not room.hashed_password or not await crypt.verify_password(password, room.hashed_password):
                raise NotAuthorizedException(detail=ERR_INVALID_ROOM_PASSWORD)

        await players_repo.add(RoomPlayerModel(room_id=room.id, user_id=user_id, is_owner=False))
        return await self.get_room(room_id)

    async def leave_room(self, room_id: UUID, user_id: UUID) -> None:
        room = await self.get_room(room_id)
        players_repo = self._players_repo()

        await players_repo.delete_where(room_id=room_id, user_id=user_id, sanity_check=False)

        if room.room_owner_id == user_id:
            remaining = await players_repo.list(
                RoomPlayerModel.room_id == room_id,
                order_by=[('created_at', False)],
            )
            if not remaining:
                await self.repository.delete(room_id)
                return
            new_owner = remaining[0]
            await players_repo.get_and_update(
                RoomPlayerModel.id == new_owner.id,
                attribute_names=('is_owner',),
                is_owner=True,
            )
            await super().update(
                item_id=room_id,
                data={'room_owner_id': new_owner.user_id},
                attribute_names=('room_owner_id',),
            )

    async def kick_player(self, room_id: UUID, actor_id: UUID, target_user_id: UUID) -> None:
        room = await self.get_room(room_id)
        if room.room_owner_id != actor_id:
            raise PermissionDeniedException(ERR_ONLY_OWNER_KICK)
        if target_user_id == actor_id:
            raise PermissionDeniedException(ERR_OWNER_CANNOT_KICK_SELF)

        players_repo = self._players_repo()
        deleted = await players_repo.delete_where(room_id=room_id, user_id=target_user_id, sanity_check=False)
        if not deleted:
            raise NotFoundException(ERR_PLAYER_NOT_IN_ROOM)

    async def to_player_schema(self, link: RoomPlayerModel) -> Player:
        user_service = UserService(session=self.repository.session)
        user_public = user_service.to_schema(link.user, schema_type=UserPublic)
        return Player(user=user_public, joined_at=link.created_at, is_owner=link.is_owner)

    async def to_room_schema(self, room: RoomModel) -> Room:
        players: Iterable[Player] = [await self.to_player_schema(p) for p in room.players]
        return Room(
            id=room.id,
            name=room.name,
            category=room.category,
            room_owner=room.room_owner_id,
            players_limit=room.players_limit,
            turn_time=room.turn_time,
            is_private=room.is_private,
            has_password=room.has_password,
            players=list(players),
            status=room.status,
            created_at=room.created_at,
        )
