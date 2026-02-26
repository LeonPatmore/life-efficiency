#!/usr/bin/env bash
set -euo pipefail

IMAGE="life-efficiency-sam"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
AWS_REGION="${AWS_DEFAULT_REGION:-eu-west-1}"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  docker build -t "$IMAGE" -f "$REPO/docker/sam/Dockerfile" "$REPO"
fi

docker run --rm \
  -v "$REPO:/workspace" \
  -w /workspace \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e DOCKER_HOST="unix:///var/run/docker.sock" \
  -e AWS_DEFAULT_REGION="$AWS_REGION" \
  "$IMAGE" "$@"

