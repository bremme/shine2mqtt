# FROM python:3.14-slim

# WORKDIR /app

# RUN python -m pip install --no-cache-dir uv && \
#     useradd -m -u 1000 shine2mqtt && \
#     chown -R shine2mqtt:shine2mqtt /app

# COPY README.md pyproject.toml uv.lock ./

# RUN uv sync --frozen --no-dev --no-install-project

# COPY src ./src

# RUN uv sync --frozen --no-dev

# USER shine2mqtt

# EXPOSE 5279

# ENTRYPOINT ["uv", "run", "--no-sync", "shine2mqtt"]
# CMD []


FROM python:3.14-slim AS build

WORKDIR /app

RUN python -m pip install --no-cache-dir uv

COPY README.md pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY src ./src

RUN uv sync --frozen --no-dev

# --------------------------------------------------

FROM python:3.14-slim

WORKDIR /app

RUN useradd -m -u 1000 shine2mqtt

COPY --from=build /app /app

USER shine2mqtt

EXPOSE 5279

ENTRYPOINT ["/app/.venv/bin/shine2mqtt"]

CMD []