FROM python:3.12-slim

WORKDIR /workspace

RUN apt-get update \
  && apt-get install -y --no-install-recommends docker.io ca-certificates \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir aws-sam-cli

ENV DOCKER_HOST=unix:///var/run/docker.sock

ENTRYPOINT ["sam"]
