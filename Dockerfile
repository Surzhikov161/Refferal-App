FROM python:3.10

ENV PYTHONUNBUFFERED=1



RUN pip install --upgrade pip "poetry"
RUN poetry config virtualenvs.create false --local
COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY /app /refferal_app/app

WORKDIR /refferal_app
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080" ]
