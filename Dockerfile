FROM python:3.11.7-slim-bullseye as build

RUN pip install --upgrade pip

RUN pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry config installer.max-workers 10

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-interaction --no-ansi -vvv

COPY . .

RUN sed -i 's/\r$//' scripts/*

RUN chmod +x scripts/*

RUN prisma generate

FROM build as app

CMD ["/bin/bash", "./scripts/start.sh"]