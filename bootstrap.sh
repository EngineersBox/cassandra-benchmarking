#!/usr/bin/env bash

set -o errexit -o pipefail -o noclobber -o nounset

source /var/lib/node_env

echo "[INFO] Starting $APPLICATION_VARIANT services"
docker compose up -d /var/lib/docker/$APPLICATION_VARIANT/docker-compose.yaml

if [ "x$INVOKE_INIT" != "x"]; then
    python3 -m venv venv
    python3 -m pip install -r requirements.txt
    set > /tmp/$$_env
    case "$APPLICATION_VARIANT" in
        cassandra)
            python3 init/cassandra.py --environment=/tmp/$$_env
            ;;
        *)
            ;;
    esac
fi

echo "[INFO] Node bootstrapping suceeded"
