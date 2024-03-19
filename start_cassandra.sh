#!/bin/bash

set -e

DISTRIBUTION="${DISTRIBUTION:-tar}"
IMAGE="${IMAGE:-cassandra}"
GITHUB_USERNAME="${GITHUB_USERNAME:-"EngineersBox"}"
REPOSITORY="${REPOSITORY:-"cassandra"}"
BRANCH="${BRANCH:-"cassandra-5.0-beta1"}"
CASSANDRA_VERSION="${CASSANDRA_VERSION:-"5.0-beta1"}"
OTEL_JAR_VERSION="${OTEL_JAR_VERSION:-"v2.2.0"}"
OTEL_JAR_PATH="${OTEL_JAR_PATH:-"/var/lib/otel/opentelemetry-javaagent.jar"}"
OTEL_AGENT_CONFIG_FILE="${OTEL_AGENT_CONFIG_FILE:-"/etc/otel/otel.properties"}"
OTEL_SERVICE_NAME="${OTEL_SERVICE_NAME:-"OTEL-Cassandra"}"
PWD=$(pwd)

cat <<EOF
Parameters:

DISTRIBUTION = $DISTRIBUTION
IMAGE = $IMAGE
GITHUB_USERNAME = $GITHUB_USERNAME
REPOSITORY = $REPOSITORY
BRANCH = $BRANCH
CASSANDRA_VERSION = $CASSANDRA_VERSION

OTEL_JAR_VERSION = $OTEL_JAR_VERSION
OTEL_JAR_PATH = $OTEL_JAR_PATH
OTEL_AGENT_CONFIG_FILE = $OTEL_AGENT_CONFIG_FILE
OTEL_SERVICE_NAME = $OTEL_SERVICE_NAME

EOF

function unpack_tar() {
    curl -OL "https://downloads.apache.org/cassandra/$CASSANDRA_VERSION/apache-cassandra-$CASSANDRA_VERSION-bin.tar.gz"
    curl -OL "https://downloads.apache.org/cassandra/$CASSANDRA_VERSION/apache-cassandra-$CASSANDRA_VERSION-bin.tar.gz.sha256"
    echo "$(cat "apache-cassandra-$CASSANDRA_VERSION-bin.tar.gz.sha256") apache-cassandra-$CASSANDRA_VERSION-bin.tar.gz" > "apache-cassandra-$CASSANDRA_VERSION-bin.tar.gz.sha256"
    sha256sum --check --status "apache-cassandra-$CASSANDRA_VERSION-bin.tar.gz.sha256"
    tar xzf "apache-cassandra-$CASSANDRA_VERSION-bin.tar.gz"
    mv "apache-cassandra-$CASSANDRA_VERSION" "$REPOSITORY"
}

function build_repo() {
    if test -d "$PWD/$REPOSITORY"; then
        cd "$REPOSITORY"
    else
        git clone --depth 1 --single-branch "https://github.com/$GITHUB_USERNAME/$REPOSITORY.git"
        cd "$REPOSITORY"
        git pull --unshallow
        git add remote upstream https://github.com/apache/cassandra
        git fetch upstream
    fi
    docker run \
        -v "$PWD:/tmp/build" \
        -w /tmp/build \
        --rm \
        --user cassandra \
        $IMAGE \
        ./build_cassandra.sh "$REPOSITORY" "$BRANCH" "$CASSANDRA_VERSION"
}

function start_docker() {
    docker run \
        -p 3000:3000 \
        -p 4317:4317 \
        -p 4318:4318 \
        -v "$PWD/log:/var/log/otel" \
        -v "$PWD/otel-collector-config.yaml:/otel-lgtm/otelcol-config.yaml" \
        -v "$PWD/grafana-dashboard-jvm.json:/otel-lgtm/grafana-dashboard-jvm.json" \
        --name "otel" \
        -d \
        grafana/otel-lgtm
    # TODO: Fix user permissions, at the moment "cassandra" acts like root
        #-p 7000:7000 \
        #-p 7001:7001 \
        #-p 7199:7199 \
        #-p 9042:9042 \
        #-p 9160:9160 \
    docker run \
        --network=host \
        -v "$PWD/otel.properties:$OTEL_AGENT_CONFIG_FILE" \
        -v "$PWD/opentelemetry-javaagent.jar:$OTEL_JAR_PATH" \
        -v "$PWD/$REPOSITORY/conf:/etc/cassandra" \
        -v "$PWD/cassandra.yaml:/etc/cassandra/cassandra.yaml" \
        -v "$PWD/$REPOSITORY:/var/lib/cassandra" \
        --name "cassandra" \
        -d \
        $IMAGE
}

jvm_server_opts=(jvm-server.options jvm11-server.options jvm17-server.options)

function instrument_cassandra() {
    wget "https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/$OTEL_JAR_VERSION/opentelemetry-javaagent.jar"
    for opt in ${jvm_server_opts[@]}; do
        echo "-javaagent:$OTEL_JAR_PATH" >> "$PWD/$REPOSITORY/conf/$opt"
        echo "-Dotel.javaagent.configuration-file=$OTEL_AGENT_CONFIG_FILE" >> "$PWD/$REPOSITORY/conf/$opt"
        echo "-Dotel.service.name=$OTEL_SERVICE_NAME" >> "$PWD/$REPOSITORY/conf/$opt"
    done
}

case $DISTRIBUTION in
    tar) unpack_tar ;;
    repo) build_repo ;;
    *) echo "[ERROR] Invalid distribution option: $DISTRIBUTION, must be one of [tar,repo]"; exit 1 ;;
esac

instrument_cassandra
start_docker

