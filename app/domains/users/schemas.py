from uuid import UUID

from app.core.schemas import CamelizedBaseStruct
from app.core.types import Password, Email, Name


class UserCreate(CamelizedBaseStruct):
    email: Email
    password: Password
    name: Name


class UserLogin(CamelizedBaseStruct):
    email: Email
    password: Password


class User(CamelizedBaseStruct):
    id: UUID
    email: Email
    name: Name
    is_admin: bool
    is_banned: bool


class UserBan(CamelizedBaseStruct):
    id: UUID
    banned: bool
