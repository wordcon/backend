from typing import Any

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService, schema_dump
from litestar.exceptions import NotAuthorizedException

from app.core import crypt
from app.domains.users.models import UserModel


class UserService(SQLAlchemyAsyncRepositoryService[UserModel]):
    class Repository(SQLAlchemyAsyncRepository[UserModel]):
        model_type = UserModel

    repository_type = Repository

    async def create(self, data: Any) -> UserModel:  # type: ignore[override]
        dumped = schema_dump(data)
        dumped = await self._populate_with_hashed_password(dumped)
        return await super().create(dumped)

    async def update(self, item_id: Any, data: Any) -> UserModel:  # type: ignore[override]
        dumped = schema_dump(data)
        dumped = await self._populate_with_hashed_password(dumped)
        return await super().update(item_id=item_id, data=dumped)

    async def _populate_with_hashed_password(self, data: dict[str, Any]) -> dict[str, Any]:
        if isinstance(data, dict) and 'password' in data:
            password = data.pop('password')
            data['hashed_password'] = await crypt.get_password_hash(password)
        return data

    async def authenticate(self, email: str, password: str) -> UserModel:
        db_obj = await self.get_one_or_none(email=email)
        if not db_obj or not await crypt.verify_password(password, db_obj.hashed_password):
            msg = 'Неправильный email или пароль'  # TODO: потом убрать
            raise NotAuthorizedException(detail=msg)
        return db_obj
