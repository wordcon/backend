from typing import Any
from uuid import UUID, uuid4

from advanced_alchemy.extensions.litestar.providers import create_service_dependencies
from litestar import Controller, Request, delete, get, patch, post
from litestar.security.jwt import Token

from app.domains.rooms.schemas import (
    Category,
    CreateRoomRequest,
    JoinRoomRequest,
    Player,
    Room,
    UpdateRoomRequest,
)
from app.domains.rooms.services import RoomService
from app.domains.users.schemas import User

_DEFAULT_CATEGORIES = [  # TODO: убрать
    Category(id=uuid4(), name='Animals'),
    Category(id=uuid4(), name='Food'),
    Category(id=uuid4(), name='Geography'),
    Category(id=uuid4(), name='Movies'),
    Category(id=uuid4(), name='Music'),
]


class CategoriesController(Controller):
    path = '/categories'
    tags = ['rooms']

    @get()
    async def list_categories(self) -> list[Category]:
        return _DEFAULT_CATEGORIES


class RoomsController(Controller):
    path = '/rooms'
    tags = ['rooms']

    dependencies = create_service_dependencies(RoomService, key='rooms_service')

    @get()
    async def list_rooms(
        self,
        rooms_service: RoomService,
        category: str | None = None,
        q: str | None = None,
        status: str | None = None,
    ) -> list[Room]:
        rooms = await rooms_service.list_rooms(category=category, q=q, status=status)
        return [await rooms_service.to_room_schema(r) for r in rooms]

    @post()
    async def create_room(
        self,
        request: Request[User, Token, Any],
        rooms_service: RoomService,
        data: CreateRoomRequest,
    ) -> Room:
        room = await rooms_service.create_room(owner_id=request.user.id, data=data.to_dict())
        return await rooms_service.to_room_schema(room)

    @get('/{room_id:uuid}')
    async def get_room(
        self,
        rooms_service: RoomService,
        room_id: UUID,
    ) -> Room:
        room = await rooms_service.get_room(room_id)
        return await rooms_service.to_room_schema(room)

    @patch('/{room_id:uuid}')
    async def update_room(
        self,
        request: Request[User, Token, Any],
        rooms_service: RoomService,
        room_id: UUID,
        data: UpdateRoomRequest,
    ) -> Room:
        updated = await rooms_service.update_room(room_id=room_id, actor_id=request.user.id, data=data.to_dict())
        return await rooms_service.to_room_schema(updated)

    @delete('/{room_id:uuid}', status_code=204)
    async def delete_room(
        self,
        request: Request[User, Token, Any],
        rooms_service: RoomService,
        room_id: UUID,
    ) -> None:
        await rooms_service.delete_room(room_id=room_id, actor_id=request.user.id)

    @post('/{room_id:uuid}/join')
    async def join_room(
        self,
        request: Request[User, Token, Any],
        rooms_service: RoomService,
        room_id: UUID,
        data: JoinRoomRequest | None = None,
    ) -> Room:
        password = data.password if data is not None else None
        room = await rooms_service.join_room(room_id=room_id, user_id=request.user.id, password=password)
        return await rooms_service.to_room_schema(room)

    @post('/{room_id:uuid}/leave', status_code=204)
    async def leave_room(
        self,
        request: Request[User, Token, Any],
        rooms_service: RoomService,
        room_id: UUID,
    ) -> None:
        await rooms_service.leave_room(room_id=room_id, user_id=request.user.id)

    @get('/{room_id:uuid}/players')
    async def list_room_players(
        self,
        rooms_service: RoomService,
        room_id: UUID,
    ) -> list[Player]:
        room = await rooms_service.get_room(room_id)
        return [await rooms_service.to_player_schema(p) for p in room.players]

    @delete('/{room_id:uuid}/players/{user_id:uuid}', status_code=204)
    async def kick_player(
        self,
        request: Request[User, Token, Any],
        rooms_service: RoomService,
        room_id: UUID,
        user_id: UUID,
    ) -> None:
        await rooms_service.kick_player(room_id=room_id, actor_id=request.user.id, target_user_id=user_id)
