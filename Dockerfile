FROM python:3.13-slim

WORKDIR /app

RUN python -m pip install --no-cache-dir uv && \
    useradd -m -u 1000 shine2mqtt && \
    chown -R shine2mqtt:shine2mqtt /app

COPY README.md pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src

RUN uv sync --frozen --no-dev

USER shine2mqtt

EXPOSE 5279

ENTRYPOINT ["uv", "run", "--no-sync", "shine2mqtt"]
CMD []