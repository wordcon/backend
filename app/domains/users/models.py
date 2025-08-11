from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy.orm import Mapped, mapped_column


class UserModel(UUIDAuditBase):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(index=True, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    username: Mapped[str] = mapped_column(index=True, unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(nullable=True)
    status: Mapped[str | None] = mapped_column(nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(nullable=True)
    banner_url: Mapped[str | None] = mapped_column(nullable=True)

    points: Mapped[int] = mapped_column(default=0, nullable=False)

    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_banned: Mapped[bool] = mapped_column(default=False, nullable=False)
