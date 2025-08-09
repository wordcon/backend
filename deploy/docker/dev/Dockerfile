ARG PYTHON_IMAGE=python:3.13-slim-bookworm

FROM ${PYTHON_IMAGE} AS python-base
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8
RUN apt-get update \
  && apt-get upgrade -y \
  && apt-get install -y --no-install-recommends git build-essential curl tini \
  && apt-get autoremove -y \
  && apt-get clean -y \
  && rm -rf /root/.cache \
  && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

FROM python-base AS dev
ARG UV_INSTALL_ARGS="--all-groups"
ARG LITESTAR_APP="app.app:app"
ENV PATH="/workspace/app/.venv/bin:/usr/local/bin:$PATH" \
    VIRTUAL_ENV="/workspace/app/.venv" \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_INSTALL_ARGS="${UV_INSTALL_ARGS}" \
    LITESTAR_APP="${LITESTAR_APP}"

WORKDIR /workspace/app
COPY pyproject.toml uv.lock ./
RUN uv venv \
  && uv sync ${UV_INSTALL_ARGS} --no-install-project

COPY app ./app

STOPSIGNAL SIGINT
EXPOSE 8000
ENTRYPOINT ["tini","--" ]
CMD ["litestar","run","--reload","--host","0.0.0.0","--port","8000"]
VOLUME /workspace/app
