import litestar
from advanced_alchemy.exceptions import RepositoryError
from litestar.exceptions import NotFoundException
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar_granian import GranianPlugin
from microbootstrap.bootstrappers.litestar import LitestarBootstrapper
from microbootstrap.config.litestar import LitestarConfig

from app.core.auth import jwt_auth
from app.core.database import alchemy
from app.core.exceptions import repository_exception_handler, not_found_exception_handler
from app.core.settings import settings
from app.domains.users.routers import AuthController, AdminController

bootstrapper = LitestarBootstrapper(settings)

bootstrapper.configure_application(
    LitestarConfig(
        route_handlers=[AuthController, AdminController],
        plugins=[alchemy, GranianPlugin()],
        openapi_config=OpenAPIConfig(
            title=settings.service_name,
            version=settings.service_version,
            render_plugins=[ScalarRenderPlugin()],
        ),
        exception_handlers={
            RepositoryError: repository_exception_handler,
            NotFoundException: not_found_exception_handler,
        },
        on_app_init=[jwt_auth.on_app_init],
    )
)

app: litestar.Litestar = bootstrapper.bootstrap()
