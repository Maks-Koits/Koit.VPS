FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps + zlib1g security update (CVE-2026-76844 / DSA-6613-1)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    ca-certificates \
 && apt-get install -y --only-upgrade --no-install-recommends zlib1g \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py ./

# The token is provided via env var at runtime
ENV TELEGRAM_BOT_TOKEN=""

CMD ["python", "bot.py"]



