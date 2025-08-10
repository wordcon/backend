from datetime import datetime
from uuid import UUID

from app.core.schemas import CamelizedBaseStruct
from app.core.types import Email, Name, Password


class User(CamelizedBaseStruct):
    id: UUID
    email: Email
    name: Name | None = None
    is_admin: bool = False
    is_banned: bool = False


class RegisterRequest(CamelizedBaseStruct):
    email: Email
    password: Password
    username: Name


class LoginRequest(CamelizedBaseStruct):
    email: Email
    password: Password


class UpdateUserRequest(CamelizedBaseStruct):
    name: Name | None = None
    username: Name | None = None
    status: str | None = None
    avatar_url: str | None = None
    banner_url: str | None = None


class UserPublic(CamelizedBaseStruct):
    id: UUID
    email: Email
    username: str
    name: str | None = None
    status: str | None = None
    avatar_url: str | None = None
    banner_url: str | None = None
    points: int = 0
    created_at: datetime | None = None


class AuthResponse(CamelizedBaseStruct):
    access_token: str
    user: UserPublic


class UserBan(CamelizedBaseStruct):
    id: UUID
    banned: bool
