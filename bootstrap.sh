#!/usr/bin/env bash

set -o errexit -o pipefail -o noclobber -o nounset

source /local/node_config_properties.sh

echo "[INFO] Starting $APPLICATION_VARIANT services"
docker compose up -d /local/docker/$APPLICATION_VARIANT/docker-compose.yaml

echo "[INFO] Node bootstrapping suceeded"
