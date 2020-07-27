FROM python:3.8.3

ENV TZ=America/Montevideo

RUN pip install poetry

WORKDIR /random_daily_subject
COPY pyproject.toml .
COPY poetry.lock .

COPY random_daily_subject ./random_daily_subject

RUN useradd -m myuser
RUN chown -R myuser:myuser /random_daily_subject

USER myuser
RUN poetry install --no-dev

CMD ["poetry", "run", "python", "random_daily_subject/scheduler.py"]
