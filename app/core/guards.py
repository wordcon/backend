from typing import Any

from litestar.connection import ASGIConnection
from litestar.exceptions import PermissionDeniedException
from litestar.handlers.base import BaseRouteHandler

from app.domains.users.schemas import User


def admin_only_guard(connection: ASGIConnection[Any, User, Any, Any], _: BaseRouteHandler) -> None:
    if not connection.user or not connection.user.is_admin:
        raise PermissionDeniedException(detail='You do not have permission to perform this action.')
