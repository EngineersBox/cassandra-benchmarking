#!/usr/bin/env bash

set -o errexit -o pipefail -o noclobber

source /var/lib/cluster/node_env

function preInitStage() {
    case "$APPLICATION_VARIANT" in
        otel_collector)
            echo "[INFO] Invoking OTEL collector initialisation"
            set -a
            source /var/lib/cluster/node_env
            python3 ./init/otel.py
            set +a
            ;;
        *)
            echo "[INFO] No pre-init operations for $APPLICATION_VARIANT, skipping"
            ;;
    esac
}

function startServicesStage() {
    echo "[INFO] Starting $APPLICATION_VARIANT services"
    docker compose -f /var/lib/cluster/docker/$APPLICATION_VARIANT/docker-compose.yaml up -d
}

function postInitStage() {
    case "$APPLICATION_VARIANT" in
        cassandra)
            # Only run once on node marked to handle it
            if [[ -z "$INVOKE_INIT" || "$INVOKE_INIT" != "true" ]]; then
                return
            fi
            echo "[INFO] Invoking cassandra initialisation"
            set -a
            source /var/lib/cluster/node_env
            python3 ./init/cass.py
            set +a
            ;;
        *)
            echo "[INFO] No post-init operations for $APPLICATION_VARIANT, skipping"
            ;;
    esac
}

declare -A BOOSTRAP_STAGES
BOOTSTRAP_STAGES["PRE_INIT"]=preInitStage
BOOTSTRAP_STAGES["START_SERVICES"]=startServicesStage
BOOTSTRAP_STAGES["POST_INIT"]=postInitStage

function performStages() {
    for stage in "${!BOOTSTRAP_STAGES[@]}"; do
        echo "[INFO] Running stage: ${stage}"
        ${BOOTSTRAP_STAGES[$stage]}
    done
}

# === MAIN === #


pushd /var/lib/cluster

echo "[INFO] Updating and installing dependencies"
sudo apt-get update -y
sudo apt-get install -y python3.10-venv
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt

performStages

popd
echo "[INFO] Node bootstrapping suceeded"
