#!/usr/bin/env bash

set -o errexit -o pipefail -o noclobber -o nounset

source /var/lib/node_env

echo "[INFO] Starting $APPLICATION_VARIANT services"
docker compose up -d /var/lib/docker/$APPLICATION_VARIANT/docker-compose.yaml

echo "[INFO] Node bootstrapping suceeded"
