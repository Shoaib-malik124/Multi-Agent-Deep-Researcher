FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for some packages
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY authentication/ ./authentication/
COPY components/ ./components/
COPY db/ ./db/
COPY prompts/ ./prompts/
COPY routes/ ./routes/
COPY schemas/ ./schemas/
COPY utils/ ./utils/
COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]