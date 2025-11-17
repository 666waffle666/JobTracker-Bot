FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y curl build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python -

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .

RUN chmod +x run.sh

EXPOSE 8000

CMD ["./run.sh"]