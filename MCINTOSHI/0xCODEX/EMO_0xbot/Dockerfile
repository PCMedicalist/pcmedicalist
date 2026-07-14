FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Hermes CLI globally in container.
RUN pip install --no-cache-dir "https://github.com/NousResearch/hermes-agent/archive/refs/heads/main.zip"

# Create isolated runtime venv for EMO bot deps (avoid Hermes dependency collisions)
COPY requirements.txt /tmp/requirements.txt
RUN python -m venv /opt/emvenv \
    && /opt/emvenv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/emvenv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

# Copy the EMO code into the image (build context is EMO_0xbot)
COPY . /app

# Ensure workspace directory exists and remains writable.
RUN mkdir -p /app/workspace

WORKDIR /app

ENTRYPOINT ["/bin/sh", "./entrypoint.sh"]