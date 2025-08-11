from datetime import datetime
from typing import Any
from uuid import UUID

from app.core.schemas import CamelizedBaseStruct


class Category(CamelizedBaseStruct):
    id: UUID
    name: str


class CreateRoomRequest(CamelizedBaseStruct):
    name: str
    players_limit: int
    turn_time: int
    category: str
    password: str | None = None
    is_private: bool = False


class UpdateRoomRequest(CamelizedBaseStruct):
    name: str | None = None
    password: str | None = None
    players_limit: int | None = None
    turn_time: int | None = None
    category: str | None = None
    status: str | None = None


class Player(CamelizedBaseStruct):
    user: Any
    joined_at: datetime | None = None
    is_owner: bool = False


class Room(CamelizedBaseStruct):
    id: UUID
    name: str
    category: str
    room_owner: UUID
    players_limit: int
    turn_time: int
    players: list[Player]
    status: str
    is_private: bool = False
    has_password: bool = False
    created_at: datetime | None = None


class JoinRoomRequest(CamelizedBaseStruct):
    password: str | None = None
