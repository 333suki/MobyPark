FROM python:3.12-slim

WORKDIR /app

RUN useradd -m appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

RUN chown -R appuser:appuser /app
USER appuser

CMD cd app && alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000
