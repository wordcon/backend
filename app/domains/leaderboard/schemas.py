from app.core.schemas import CamelizedBaseStruct


class LeaderboardEntry(CamelizedBaseStruct):
    username: str
    points: int
    place: int
    avatar_url: str | None = None
