import os
from typing import Any

from microbootstrap import LitestarSettings


class Settings(LitestarSettings):
    service_debug: bool = os.getenv('SERVICE_DEBUG', 'false').lower() in {
        '1',
        'true',
        'yes',
        'on',
    }
    service_name: str = os.getenv('SERVICE_NAME', 'wordcon')
    service_description: str = os.getenv('SERVICE_DESCRIPTION', 'Wordcon backend service')
    service_version: str = os.getenv('SERVICE_VERSION', '0.0.1')
    service_static_path: str = os.getenv('SERVICE_STATIC_PATH', '/static')
    app_url: str = os.getenv('APP_URL', 'http://localhost:8000')

    swagger_path: str = os.getenv('SWAGGER_PATH', '/docs')
    swagger_offline_docs: bool = os.getenv('SWAGGER_OFFLINE_DOCS', 'false').lower() in {
        '1',
        'true',
        'yes',
        'on',
    }
    swagger_extra_params: dict[str, Any] = {}

    health_checks_enabled: bool = os.getenv('HEALTH_CHECKS_ENABLED', 'true').lower() in {'1', 'true', 'yes', 'on'}
    health_checks_path: str = os.getenv('HEALTH_CHECKS_PATH', '/health/')
    health_checks_include_in_schema: bool = os.getenv('HEALTH_CHECKS_INCLUDE_IN_SCHEMA', 'false').lower() in {
        '1',
        'true',
        'yes',
        'on',
    }

    prometheus_metrics_path: str = os.getenv('PROMETHEUS_METRICS_PATH', '/metrics')
    prometheus_additional_params: dict[str, Any] = {}

    cors_allowed_origins: list[str] = []
    cors_allowed_methods: list[str] = []
    cors_allowed_headers: list[str] = []
    cors_exposed_headers: list[str] = []
    cors_allowed_credentials: bool = False
    cors_allowed_origin_regex: str | None = None
    cors_max_age: int = 600

    jwt_secret: str = os.getenv('JWT_SECRET', 'change-me')
    database_url: str = os.getenv('DATABASE_URL', 'postgresql+asyncpg://app:app@db:5432/app')


settings = Settings()
