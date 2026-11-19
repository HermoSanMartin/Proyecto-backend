FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY migrations ./migrations
COPY app ./app

RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && python -m app.infrastructure.seeders.seed && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]