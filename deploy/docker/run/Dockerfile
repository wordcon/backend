ARG PYTHON_IMAGE=python:3.13-slim-bookworm

FROM ${PYTHON_IMAGE} AS python-base
RUN apt-get update \
  && apt-get upgrade -y \
  && apt-get install -y --no-install-recommends tini \
  && apt-get autoremove -y \
  && apt-get clean -y \
  && rm -rf /root/.cache \
  && rm -rf /var/lib/apt/lists/* \
  && mkdir -p /workspace/app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

FROM python-base AS builder
ARG UV_INSTALL_ARGS="--no-dev"
ENV UV_LINK_MODE=copy \
  UV_NO_CACHE=1 \
  UV_COMPILE_BYTECODE=1 \
  UV_INSTALL_ARGS="${UV_INSTALL_ARGS}" \
  UV_SYSTEM_PYTHON=1 \
  PATH="/workspace/app/.venv/bin:/usr/local/bin:$PATH" \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONFAULTHANDLER=1 \
  LANG=C.UTF-8 \
  LC_ALL=C.UTF-8

WORKDIR /workspace/app
COPY pyproject.toml uv.lock ./
COPY app ./app
RUN uv venv \
  && uv sync ${UV_INSTALL_ARGS} --frozen

FROM python-base AS runner
ENV PATH="/workspace/app/.venv/bin:/usr/local/bin:$PATH" \
  UV_LINK_MODE=copy \
  UV_NO_CACHE=1 \
  UV_COMPILE_BYTECODE=1 \
  UV_SYSTEM_PYTHON=1 \
  LITESTAR_APP="app.app:app" \
  LITESTAR_HOST="0.0.0.0" \
  LITESTAR_PORT="8000"

RUN addgroup --system --gid 65532 nonroot \
  && adduser --no-create-home --system --uid 65532 nonroot \
  && mkdir -p /workspace/app \
  && chown -R nonroot:nonroot /workspace
WORKDIR /workspace/app
COPY --from=builder --chown=65532:65532 /workspace/app/.venv /workspace/app/.venv
COPY --from=builder --chown=65532:65532 /workspace/app/app /workspace/app/app
RUN chown -R nonroot:nonroot /workspace/app
USER nonroot
STOPSIGNAL SIGINT
EXPOSE 8000
ENTRYPOINT ["tini","--" ]
CMD ["litestar","run"]
VOLUME /workspace/app
