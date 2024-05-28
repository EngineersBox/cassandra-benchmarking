#!/usr/bin/env bash

set -e

PWD=$(pwd)

case $(basename "$PWD") in
    cassandra-benchmarking) ;;
    *) echo "[ERROR] Script should be run from cassandra-benchmarking directory, not from '$PWD' Exiting.";
       exit 1;;
esac

source scripts/parameters.sh

if [ $# -lt 1 ]; then
    echo "Usage: run_cassandra.sh <refresh: y|n> [... <docker args>]"
    exit 1
fi

CLEAR_ALL="$1"
if [ "${CLEAR_ALL,,}" = "y" ]; then
  sudo vmprobe cache evict /mnt/nvme/cassandra_data  
	echo "[INFO] Evicted all page cache entries"
	sudo rm -rf /mnt/nvme/cassandra_data/*
	echo "[INFO] Cleaned cassandra data mount"
	docker container stop cassandra
	docker container rm cassandra
fi

echo "${@:2}"

echo "[INFO] Starting Cassandra..."

if [ "$1" -eq "y" ]; then
    rm -rf /mnt/nvme/cassandra_data/*
    sudo vmprobe evict /mnt/nvme/cassandra_data  
fi

docker run \
    -p 7000:7000 \
    -p 7001:7001 \
    -p 7199:7199 \
    -p 9042:9042 \
    -p 9160:9160 \
    -v "$PWD/log:/var/log/cassandra" \
    -v "$PWD/config/otel/otel.properties:$OTEL_AGENT_CONFIG_FILE" \
    -v "$PWD/$REPOSITORY/conf:/etc/cassandra" \
    -v "$PWD/config/cassandra/cassandra.yaml:/etc/cassandra/cassandra.yaml" \
    -v "$PWD/$REPOSITORY:/var/lib/cassandra" \
    -v "/mnt/nvme/cassandra_data:/var/lib/cassandra/data" \
    --name="cassandra" \
    -d \
    ${@:2} \
    "$CASSANDRA_IMAGE:$CASSANDRA_TAG"
