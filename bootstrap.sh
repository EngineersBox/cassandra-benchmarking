#!/usr/bin/env bash

set -o errexit -o pipefail -o noclobber -o nounset

source /var/lib/node_env

echo "[INFO] Starting $APPLICATION_VARIANT services"
docker compose up -d /var/lib/docker/$APPLICATION_VARIANT/docker-compose.yaml

if [ "$APPLICATION_VARIANT" != "otel_collector" ]; then
    echo "[INFO] Node bootstrapping suceeded"
    exit 0
fi

function join() {
    local IFS="$1"
    shift
    echo "$*"
}

BASE_PROFILE_PATH="/var/lib/ycsb-$YCSB_VERSION/base_profile.dat"
case "$CLUSTER_APPLICATION" in
    "cassandra")
        cat <<-EOF > "$BASE_PROFILE_PATH"
        hosts=$(join , "${NODE_ALL_IPS[@]}")
        port=9042
        EOF
        ;;
    "elasticsearch")
        # TODO: Complete this
        cat <<-EOF > "$BASE_PROFILE_PATH"
        EOF
        ;;
    "mongodb")
        # TODO: Complete this
        cat <<-EOF > "$BASE_PROFILE_PATH"
        EOF
        ;;
    "scylla")
        cat <<-EOF > "$BASE_PROFILE_PATH"
        scylla.hosts=$(join , "${NODE_ALL_IPS[@]}")
        scylla.port=9042
        EOF
        ;;
    "*")
        echo "[ERROR] Unknown cluster application: $CLUSTER_APPLICATION";
        exit 1
        ;;
esac

echo "[INFO] Node bootstrapping suceeded"
