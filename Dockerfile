FROM python:3.11-slim

LABEL org.opencontainers.image.title="Operations Root Cause Analytics with NLP"
LABEL org.opencontainers.image.ref.name="operations-root-cause-analytics-nlp"
LABEL org.opencontainers.image.description="Operations intelligence NLP API for root-cause-related factor classification and analyst review support."

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY artifacts ./artifacts

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
