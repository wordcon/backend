from advanced_alchemy.exceptions import RepositoryError
from litestar import Litestar
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin

from app.core.auth import jwt_auth
from app.core.database import alchemy
from app.core.exceptions import exception_to_http_response, after_exception_hook_handler
from app.domains.users.routers import AuthController, AdminController

app = Litestar(
    route_handlers=[AuthController, AdminController],
    plugins=[alchemy],
    openapi_config=OpenAPIConfig(title="words-game", version="0.0.1", render_plugins=[ScalarRenderPlugin()]),
    exception_handlers={
        RepositoryError: exception_to_http_response,
    },
    after_exception=[after_exception_hook_handler],
    on_app_init=[jwt_auth.on_app_init],
)
