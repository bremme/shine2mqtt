FROM python:3.13-slim

WORKDIR /app

RUN python -m pip install --no-cache-dir uv && \
    useradd -m -u 1000 shine2mqtt && \
    chown -R shine2mqtt:shine2mqtt /app

COPY README.md pyproject.toml uv.lock ./

USER shine2mqtt

RUN uv sync --frozen --no-dev

COPY --chown=shine2mqtt:shine2mqtt src ./src

EXPOSE 5279

ENTRYPOINT ["uv", "run", "shine2mqtt"]
CMD []