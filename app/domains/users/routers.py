from typing import Any

from advanced_alchemy.extensions.litestar.providers import create_service_dependencies
from litestar import Controller, Request, Response, get, patch, post
from litestar.security.jwt import Token

from app.core.auth import jwt_auth
from app.core.guards import admin_only_guard
from app.domains.users.schemas import (
    LoginRequest,
    RegisterRequest,
    UpdateUserRequest,
    User,
    UserBan,
    UserPublic,
)
from app.domains.users.services import UserService


class UsersController(Controller):
    path = "/users"
    dependencies = create_service_dependencies(
        UserService,
        key="users_service",
    )
    tags = ["users"]

    @post("/signup", exclude_from_auth=True)
    async def register(
            self, users_service: UserService, data: RegisterRequest
    ) -> Response[UserPublic]:
        user = await users_service.create(data.to_dict())
        public_user = users_service.to_schema(user, schema_type=UserPublic)
        return jwt_auth.login(
            identifier=str(user.id),
            response_body=public_user,
        )

    @post("/login", exclude_from_auth=True)
    async def login(
            self, users_service: UserService, data: LoginRequest
    ) -> Response[UserPublic]:
        user = await users_service.authenticate(
            email=data.email, password=data.password
        )
        public_user = users_service.to_schema(user, schema_type=UserPublic)
        return jwt_auth.login(
            identifier=str(user.id),
            response_body=public_user,
        )

    @get("/me")
    async def get_me(
            self, request: Request[User, Token, Any], users_service: UserService
    ) -> UserPublic:
        user_model = await users_service.get(item_id=request.user.id)
        return users_service.to_schema(user_model, schema_type=UserPublic)

    @patch("/me")
    async def update_me(
            self,
            request: Request[User, Token, Any],
            users_service: UserService,
            data: UpdateUserRequest,
    ) -> UserPublic:
        update_data = data.to_dict()
        updated = await users_service.update(item_id=request.user.id, data=update_data)
        return users_service.to_schema(updated, schema_type=UserPublic)


class AdminController(Controller):
    path = "/admin"
    guards = [admin_only_guard]
    dependencies = create_service_dependencies(
        UserService,
        key="users_service",
    )
    tags = ["admin"]

    @patch("/ban")
    async def ban_user(self, users_service: UserService, data: UserBan) -> UserPublic:
        updated_user = await users_service.update(
            item_id=data.id,
            data={"is_banned": data.banned},
        )
        return users_service.to_schema(updated_user, schema_type=UserPublic)
