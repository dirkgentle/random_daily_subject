FROM python:3.8.3

ENV TZ=America/Montevideo

RUN pip install pipenv

WORKDIR /random_daily_subject
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install

COPY random_daily_subject ./random_daily_subject

WORKDIR /random_daily_subject/random_daily_subject

CMD ["pipenv", "run", "python", "bot.py"]
