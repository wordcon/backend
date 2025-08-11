from enum import StrEnum
from typing import List, Optional
from uuid import UUID

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domains.users.models import UserModel


class RoomStatus(StrEnum):
    OPEN = 'open'
    IN_GAME = 'in_game'
    FINISHED = 'finished'


class RoomModel(UUIDAuditBase):
    __tablename__ = 'rooms'

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)

    room_owner_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    owner: Mapped[UserModel] = relationship('UserModel', lazy='selectin')

    players_limit: Mapped[int] = mapped_column(nullable=False)
    turn_time: Mapped[int] = mapped_column(nullable=False)  # seconds

    is_private: Mapped[bool] = mapped_column(default=False, nullable=False)
    has_password: Mapped[bool] = mapped_column(default=False, nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(nullable=True)

    status: Mapped[str] = mapped_column(String(20), default=RoomStatus.OPEN.value, nullable=False, index=True)

    players: Mapped[List['RoomPlayerModel']] = relationship(
        'RoomPlayerModel',
        back_populates='room',
        cascade='all, delete-orphan',
        lazy='selectin',
    )


class RoomPlayerModel(UUIDAuditBase):
    __tablename__ = 'room_players'
    __table_args__ = (UniqueConstraint('room_id', 'user_id', name='uq_room_user'),)

    room_id: Mapped[UUID] = mapped_column(ForeignKey('rooms.id', ondelete='CASCADE'), index=True, nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True, nullable=False)

    is_owner: Mapped[bool] = mapped_column(default=False, nullable=False)

    room: Mapped[RoomModel] = relationship('RoomModel', back_populates='players')
    user: Mapped[UserModel] = relationship('UserModel', lazy='selectin')
