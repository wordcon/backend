import sys
from typing import Any

from advanced_alchemy.exceptions import IntegrityError, RepositoryError
from litestar.connection import Request
from litestar.exceptions import (
    HTTPException,
    InternalServerException,
    NotFoundException,
)
from litestar.exceptions.responses import create_debug_response, create_exception_response
from litestar.middleware.exceptions.middleware import ExceptionResponseContent
from litestar.repository.exceptions import ConflictError, NotFoundError
from litestar.response import Response
from litestar.status_codes import HTTP_409_CONFLICT
from litestar.types import Scope
from structlog.contextvars import bind_contextvars


class ApplicationError(Exception):
    detail: str

    def __init__(self, *args: Any, detail: str = "") -> None:
        self.detail = detail or getattr(self, "detail", "")
        super().__init__(*args)


class _HTTPConflictException(HTTPException):
    status_code = HTTP_409_CONFLICT


async def after_exception_hook_handler(exc: Exception, _scope: Scope) -> None:
    if isinstance(exc, HTTPException) and exc.status_code < 500:
        return
    bind_contextvars(exc_info=sys.exc_info())


def exception_to_http_response(
        request: Request[Any, Any, Any],
        exc: RepositoryError,
) -> Response[ExceptionResponseContent]:
    if request.app.debug:
        return create_debug_response(request, exc)

    http_exc: type[HTTPException]
    detail: str

    if isinstance(exc, NotFoundError):
        http_exc = NotFoundException
        detail = "The requested resource was not found."

    elif isinstance(exc, IntegrityError):
        http_exc = _HTTPConflictException
        detail = "A resourse already exists."

    elif isinstance(exc, ConflictError):
        http_exc = _HTTPConflictException
        detail = "A conflict occurred with the current state of the resource."

    else:
        http_exc = InternalServerException
        detail = "An unexpected database error occurred."

    return create_exception_response(request, http_exc(detail=detail))
