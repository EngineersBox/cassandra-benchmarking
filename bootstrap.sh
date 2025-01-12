#!/usr/bin/env bash

set -o errexit -o pipefail -o noclobber -o nounset

source /var/lib/node_env

echo "[INFO] Starting $APPLICATION_VARIANT services"
docker compose up -d /var/lib/docker/$APPLICATION_VARIANT/docker-compose.yaml

if [ "x$INVOKE_INIT" != "x"]; then
    case "$APPLICATION_VARIANT" in
        cassandra)
            ./scripts/cassandra_init_ycsb.sh
            ;;
        *)
            ;;
    esac
fi

echo "[INFO] Node bootstrapping suceeded"
