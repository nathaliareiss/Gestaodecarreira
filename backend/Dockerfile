FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./backend

EXPOSE 8000

# Backend FastAPI isolado para deploy.
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
