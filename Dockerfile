# Berlin Marathon Dash — production image (Hugging Face Spaces, Render, Koyeb, local)
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8 PORT=7860
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

# Hugging Face Spaces runs containers as uid 1000
RUN useradd -m -u 1000 user && chown -R user /app
USER user

EXPOSE 7860
# 1 worker: the dataset (~330 MB) is loaded once per worker; threads handle concurrency.
# Data paths are relative to /app, so run from here and add src to the import path.
CMD gunicorn --pythonpath src app:server \
    --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 180
