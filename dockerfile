# Dockerfile
FROM python:3.12-slim

# Install system deps (for PyAudio, builds, etc.)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      gcc \
      libportaudio2 \
      portaudio19-dev \
      libffi-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy & install Python deps + Gunicorn
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the rest of your code
COPY . .

# Expose Flask’s default port
EXPOSE 5000

# Launch via Gunicorn, binding to all interfaces
CMD ["gunicorn", "-b", "0.0.0.0:5000", "api:app"]
