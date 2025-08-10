from litestar.plugins.sqlalchemy import (
    AlembicAsyncConfig,
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)

from app.core.settings import settings

DATABASE_URL = settings.database_url

sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string=DATABASE_URL,
    before_send_handler="autocommit",
    session_config=AsyncSessionConfig(expire_on_commit=False),
    alembic_config=AlembicAsyncConfig(script_location="./migrations"),
    create_all=False,
)
alchemy = SQLAlchemyPlugin(config=sqlalchemy_config)
