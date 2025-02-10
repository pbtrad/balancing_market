FROM python:3.11

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini /app/
COPY ./migrations /app/migrations

COPY ./app /app/app
COPY start.sh /app/
RUN chmod +x /app/start.sh

ENV PYTHONUNBUFFERED=1

CMD ["/app/start.sh"]


