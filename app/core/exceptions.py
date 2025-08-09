from typing import Any

from advanced_alchemy.exceptions import IntegrityError, RepositoryError
from litestar import MediaType, Request, Response
from litestar.exceptions import NotFoundException
from litestar.repository.exceptions import ConflictError, NotFoundError
from litestar.status_codes import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


def repository_exception_handler(
        request: Request[Any, Any, Any],
        exc: RepositoryError,
) -> Response[dict[str, Any]]:
    if isinstance(exc, NotFoundError):
        status_code = HTTP_404_NOT_FOUND
        detail = "The requested resource was not found."
    elif isinstance(exc, (IntegrityError, ConflictError)):
        status_code = HTTP_409_CONFLICT
        detail = "A conflict occurred with the current state of the resource."
    else:
        status_code = HTTP_500_INTERNAL_SERVER_ERROR
        detail = "Internal Server Error"

    return Response[dict[str, Any]](
        media_type=MediaType.JSON,
        content={
            "status_code": status_code,
            "detail": detail,
            "extra": {},
        },
        status_code=status_code,
    )


def not_found_exception_handler(
        request: Request[Any, Any, Any],
        exc: NotFoundException,
) -> Response[dict[str, Any]]:
    return Response[dict[str, Any]](
        media_type=MediaType.JSON,
        content={
            "status_code": HTTP_404_NOT_FOUND,
            "detail": "The requested resource was not found.",
            "extra": {},
        },
        status_code=HTTP_404_NOT_FOUND,
    )
