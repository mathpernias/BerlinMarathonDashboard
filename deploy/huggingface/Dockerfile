# Space-only Dockerfile: pulls the app from GitHub at build time,
# so the Space never needs Git LFS for the 35 MB dataset.
# To deploy a new version: Space › Settings › "Factory rebuild".
FROM python:3.11-slim

ARG REPO=https://github.com/mathpernias/BerlinMarathonDashboard.git
ARG BRANCH=redesign-berlin-nocturne

ENV PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
WORKDIR /app
RUN git clone --depth 1 --branch ${BRANCH} ${REPO} . \
    && rm -f src/assets/data/MyBerlin_1999-2023.csv \
    && pip install --no-cache-dir -r requirements.txt \
    && chown -R user /app
USER user

EXPOSE 7860
CMD ["gunicorn", "--pythonpath", "src", "app:server", "--bind", "0.0.0.0:7860", \
     "--workers", "1", "--threads", "4", "--timeout", "180"]
