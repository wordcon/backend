from datetime import datetime
from uuid import UUID

from app.core.schemas import CamelizedBaseStruct


class GuessRequest(CamelizedBaseStruct):
    text: str


class GamePoint(CamelizedBaseStruct):
    user_id: UUID
    value: int


class GamePlace(CamelizedBaseStruct):
    user_id: UUID
    place: int


class Game(CamelizedBaseStruct):
    id: UUID
    room_id: UUID
    name: str
    state: str
    round: int
    turn_time: int
    time_left: int
    points: list[GamePoint]
    places: list[GamePlace] = []
    end_date: datetime | None = None
