FROM python:3.12.10-slim

WORKDIR /usr/src/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        nano iputils-ping vim tmux \
        # WeasyPrint native deps (Pango/GLib/Cairo stack)
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libharfbuzz0b \
        libharfbuzz-subset0 \
        libglib2.0-0 \
        libcairo2 \
        libgdk-pixbuf-2.0-0 \
        shared-mime-info \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --retries=20 --timeout=60 --resume-retries=20 -r requirements.txt

ENV PYTHONPATH=/usr/src/app/src

COPY .env ./
COPY src/ src/
COPY prompts/ prompts/
