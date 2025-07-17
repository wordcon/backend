import os
from typing import Any

from litestar.connection import ASGIConnection
from litestar.security.jwt import JWTAuth, Token

from app.core.database import sqlalchemy_config
from app.domains.users.schemas import User
from app.domains.users.services import UserService

JWT_SECRET = os.environ.get("JWT_SECRET", "a-very-secure-secret")


async def retrieve_user_handler(token: Token, connection: ASGIConnection[Any, Any, Any, Any]) -> User | None:
    db_session = sqlalchemy_config.provide_session(
        state=connection.app.state, scope=connection.scope
    )
    user_service = UserService(session=db_session)

    user_id = token.sub
    try:
        user_model = await user_service.get(item_id=user_id)
    except (ValueError, TypeError):
        return None

    if not user_model or user_model.is_banned:
        return None

    return user_service.to_schema(user_model, schema_type=User)


jwt_auth = JWTAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=JWT_SECRET,
    exclude=["/schema"],
)
