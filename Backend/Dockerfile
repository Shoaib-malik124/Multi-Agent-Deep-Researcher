FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY authentication/ ./authentication/
COPY components/ ./components/
COPY db/ ./db/
COPY prompts/ ./prompts/
COPY routes/ ./routes/
COPY schemas/ ./schemas/
COPY utils/ ./utils/
COPY main.py .
COPY celery_app.py .

EXPOSE 8000