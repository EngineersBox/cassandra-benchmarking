#!/bin/bash

set -e

PWD=$(pwd)

case "$PWD" in
    */cassandra-benchmarking)
        echo "[ERROR] Script should be run from cassandra-benchmarking directory, not from '$PWD' Exiting.";
        exit 1;;
    *) ;;
esac

source scripts/parameters.sh

if [ "$#" -lt 1 ]; then
    echo "Usage: run_otel <refresh: y|n> [... <docker args>]"
    exit 1
fi

if [ "$1" -eq "y" ]; then
    rm -rf data
    sudo vmprobe evict data
fi

docker run \
    -p 3000:3000 \
    -p 4317:4317 \
    -p 4318:4318 \
    -v "$PWD/log:/var/log/otel" \
    -v "$PWD/config/otel/otel-collector-config.yaml:/otel-lgtm/otelcol-config.yaml" \
    -v "$PWD/config/otel/grafana-dashboard-jvm.json:/otel-lgtm/grafana-dashboard-jvm.json" \
    -v "$PWD/config/otel/grafana-dashboard-jvm.json:/otel-lgtm/grafana-dashboard-data-serializer.json" \
    -v "$PWD/config/otel/grafana-dashboards.yaml:/otel-lgtm/grafana-dashboards.yaml" \
    -v "$PWD/data:/otel-lgtm/data" \
    -v "$PWD/opentelemetry-jmx-metrics.jar:$OTEL_JMX_JAR_PATH" \
    --name "otel" \
    -d \
    grafana/otel-lgtm
