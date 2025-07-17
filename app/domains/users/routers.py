from typing import Any

from advanced_alchemy.extensions.litestar.providers import create_service_dependencies
from litestar import Controller, patch
from litestar import get, post, Request, Response
from litestar.security.jwt import Token

from app.core.auth import jwt_auth
from app.core.guards import admin_only_guard
from app.domains.users.schemas import User, UserBan
from app.domains.users.schemas import UserCreate, UserLogin
from app.domains.users.services import UserService


class AuthController(Controller):
    path = "/auth"
    dependencies = create_service_dependencies(
        UserService,
        key="users_service",
    )
    tags = ["Users"]

    @post(exclude_from_auth=True)
    async def signup(self, users_service: UserService, data: UserCreate) -> User:
        user_data = data.to_dict()
        user = await users_service.create(user_data)
        return users_service.to_schema(user, schema_type=User)

    @post("/login", exclude_from_auth=True)
    async def login(self, users_service: UserService, data: UserLogin) -> Response[User]:
        user = await users_service.authenticate(email=data.email, password=data.password)

        return jwt_auth.login(
            identifier=str(user.id),
            response_body=users_service.to_schema(user, schema_type=User),
        )

    @get("/me")
    async def profile(self, request: Request[User, Token, Any]) -> User:
        return request.user


class AdminController(Controller):
    path = "/admin"
    guards = [admin_only_guard]
    dependencies = create_service_dependencies(
        UserService,
        key="users_service",
    )
    tags = ["Admin"]

    @patch("/ban")
    async def ban_user(self, users_service: UserService, data: UserBan) -> User:
        updated_user = await users_service.update(
            item_id=data.id,
            data={"is_banned": data.banned},
        )

        return users_service.to_schema(updated_user, schema_type=User)
