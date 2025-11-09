FROM python:3.11-slim AS app

ENV POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get install -y curl \
 && curl -sSL https://install.python-poetry.org | python -

WORKDIR /app

COPY . .

RUN poetry install --no-root

ENTRYPOINT ["poetry", "run", "python", "src/main.py"]
