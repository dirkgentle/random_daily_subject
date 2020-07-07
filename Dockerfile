FROM python:3.8.3

ENV TZ=America/Montevideo

RUN pip install poetry

WORKDIR /random_daily_subject
COPY pyproject.toml .
COPY poetry.lock .
COPY random_daily_subject ./random_daily_subject

RUN poetry install --no-dev

WORKDIR /random_daily_subject/random_daily_subject

CMD ["poetry", "run", "python", "bot.py"]
