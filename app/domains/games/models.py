from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional
from uuid import UUID

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domains.rooms.models import RoomModel
from app.domains.users.models import UserModel


class GameState(StrEnum):
    WAITING = 'waiting'
    RUNNING = 'running'
    ENDED = 'ended'


class GameModel(UUIDAuditBase):
    __tablename__ = 'games'

    room_id: Mapped[UUID] = mapped_column(ForeignKey('rooms.id', ondelete='CASCADE'), index=True, nullable=False)
    state: Mapped[str] = mapped_column(String(20), default=GameState.WAITING.value, index=True, nullable=False)
    round: Mapped[int] = mapped_column(default=1, nullable=False)

    turn_time: Mapped[int] = mapped_column(nullable=False)  # seconds
    last_tick_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)

    end_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    room: Mapped[RoomModel] = relationship('RoomModel', lazy='selectin')
    players: Mapped[list['GamePlayerModel']] = relationship(
        'GamePlayerModel',
        back_populates='game',
        cascade='all, delete-orphan',
        lazy='selectin',
    )


class GamePlayerModel(UUIDAuditBase):
    __tablename__ = 'game_players'
    __table_args__ = (UniqueConstraint('game_id', 'user_id', name='uq_game_user'),)

    game_id: Mapped[UUID] = mapped_column(ForeignKey('games.id', ondelete='CASCADE'), index=True, nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True, nullable=False)

    points: Mapped[int] = mapped_column(default=0, nullable=False)
    place: Mapped[Optional[int]] = mapped_column(nullable=True)

    game: Mapped[GameModel] = relationship('GameModel', back_populates='players')
    user: Mapped[UserModel] = relationship('UserModel', lazy='selectin')
