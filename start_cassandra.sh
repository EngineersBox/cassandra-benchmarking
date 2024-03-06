#!/bin/bash

set -e

DISTRIBUTION="${DISTRIBUTION:-tar}"
IMAGE="${IMAGE:-cassandra}"
GITHUB_USERNAME="${GITHUB_USERNAME:-"EngineersBox"}"
REPOSITORY="${REPOSITORY:-"cassandra"}"
BRANCH="${BRANCH:-"cassandra-5.0-beta1"}"
CASSANDRA_VERSION="${CASSANDRA_VERSION:-"5.0-beta1"}"
PWD=$(pwd)

cat <<EOF
Parameters:

DISTRIBUTION = $DISTRIBUTION
IMAGE = $IMAGE
GITHUB_USERNAME = $GITHUB_USERNAME
REPOSITORY = $REPOSITORY
BRANCH = $BRANCH
CASSANDRA_VERSION = $CASSANDRA_VERSION

EOF

function unpack_tar() {
    curl -OL "https://downloads.apache.org/cassandra/$CASSANDRA_VERSION/apache-cassandra-$CASSANDRA_VERSION-bin.tar.gz"
    curl -OL "https://downloads.apache.org/cassandra/$CASSANDRA_VERSION/apache-cassandra-$CASSANDRA_VERSION-bin.tar.gz.sha256"
    echo "$(cat "apache-cassandra-$CASSANDRA_VERSION-bin.tar.gz.sha256") apache-cassandra-$CASSANDRA_VERSION-bin.tar.gz" > "apache-cassandra-$CASSANDRA_VERSION-bin.tar.gz.sha256"
    sha256sum --check --status "apache-cassandra-$CASSANDRA_VERSION-bin.tar.gz.sha256"
    tar xzf "apache-cassandra-$CASSANDRA_VERSION-bin.tar.gz"
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
        $IMAGE \
        ./build_cassandra.sh "$REPOSITORY" "$BRANCH" "$CASSANDRA_VERSION"
}

function start_docker() {
    docker run \
        -p 127.0.0.1:7000:7000 \
        -p 127.0.0.1:7001:1001 \
        -p 127.0.0.1:7199:7199 \
        -p 127.0.0.1:9042:9042 \
        -p 127.0.0.1:9160:9160 \
        -v "$PWD/cassandra.yaml:/etc/cassandra/cassandra.yaml" \
        -v "$PWD/apache-cassandra-$CASSANDRA_VERSION:/var/lib/cassandra" \
        --name "cassandra" \
        -d \
        $IMAGE \
        /var/lib/cassandra/bin/cassandra -R -f
}

case $DISTRIBUTION in
    tar) unpack_tar ;;
    repo) build_repo ;;
    *) echo "[ERROR] Invalid distribution option: $DISTRIBUTION, must be one of [tar,repo]"; exit 1 ;;
esac

start_docker

