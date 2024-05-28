#!/bin/bash

set -e

PWD=$(pwd)

case $(basename "$PWD") in
    cassandra-benchmarking) ;;
    *) echo "[ERROR] Script should be run from cassandra-benchmarking directory, not from '$PWD' Exiting.";
       exit 1;;
esac

if [ "$#" -lt 1 ]; then
    echo "Usage: run_otel <refresh: y|n> [... <docker args>]"
    exit 1
fi

source scripts/parameters.sh

CLEAR_ALL="$1"
if [ "${CLEAR_ALL,,}" = "y" ]; then
    sudo vmprobe cache evict data
    rm -rf data
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
    ${@:2} \
    ghcr.io/engineersbox/otel-lgtm:latest
