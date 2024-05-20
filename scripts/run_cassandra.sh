#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Usage: run_cassandra.sh <refresh: y|n> [... <docker args>]"
    exit 1
fi

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
    -v "$PWD/opentelemetry-jmx-metrics.jar:$OTEL_JMX_JAR_PATH" \
    -v "$PWD/opentelemetry-javaagent.jar:$OTEL_COLLECTOR_JAR_PATH" \
    -v "$PWD/$REPOSITORY/conf:/etc/cassandra" \
    -v "$PWD/config/cassandra/cassandra.yaml:/etc/cassandra/cassandra.yaml" \
    -v "$PWD/$REPOSITORY:/var/lib/cassandra" \
    -v "/mnt/nvme/cassandra_data:/var/lib/cassandra/data" \
    --name "cassandra" \
    -d \
    $@ \
    ghcr.io/engineersbox/cassandra:5.0
