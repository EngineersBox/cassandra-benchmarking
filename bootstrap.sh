#!/usr/bin/env bash

set -o errexit -o pipefail -o noclobber

source /var/lib/cluster/node_env

function validate_service_start_timing {
    case "$SERVICE_START_TIMING" in
        BEFORE_INIT | AFTER_INIT)
            ;;
        *)
            echo "[ERROR] Invalid value for SERVICE_START_TIMING, must be one of [BEFORE_INIT, AFTER_INIT]"
            exit 1
            ;;
    esac
}

function start_services() {
    echo "[INFO] Starting $APPLICATION_VARIANT services"
    docker compose -f /var/lib/cluster/docker/$APPLICATION_VARIANT/docker-compose.yaml up -d
}

function node_init() {
    if [[ -z "$INVOKE_INIT" || "$INVOKE_INIT" == "false" ]]; then
        echo "[INFO] No init invocation required"
        return
    fi

    echo "[INFO] Updating and installing dependencies"
    sudo apt-get update -y
    sudo apt-get install -y python3.10-venv
    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install -r requirements.txt

    case "$APPLICATION_VARIANT" in
        cassandra)
            echo "[INFO] Invoking cassandra initialisation"
            set -a
            source /var/lib/cluster/node_env
            python3 ./init/cass.py
            set +a
            ;;
        otel_collector)
            echo "[INFO] Invoking OTEL collector initialisation"
            set -a
            source /var/lib/cluster/node_env
            python3 ./init/otel.py
            set +a
            ;;
        *)
            ;;
    esac
}

# === MAIN === #

validate_service_start_timing

pushd /var/lib/cluster

if [[ "$SERVICE_START_TIMING" == "BEFORE_INIT" ]]; then
    start_services
fi

node_init

if [[ "$SERVICE_START_TIMING" == "AFTER_INIT" ]]; then
    start_services
fi

popd
echo "[INFO] Node bootstrapping suceeded"
