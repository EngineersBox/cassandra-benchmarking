#!/bin/bash

if [ $# -lt 1 ]; then
	echo "Usage: ./run_cassandra <clear all: Y|N> [<docker args ...>]"
	exit 1
fi

CLEAR_ALL="$1"
if [ "${CLEAR_ALL,,}" = "y" ]; then
	sudo /proc/sys/vm/drop_caches
	echo "[INFO] Evicted all page cache entries"
	sudo rm -rf /mnt/nvme/cassandra_data/*
	echo "[INFO] Cleaned cassandra data mount"
	docker container stop cassandra
	docker container rm cassandra
fi

echo "${@:2}"

echo "[INFO] Starting Cassandra..."

# Parameters that don't help with RLIMIT_MEMORY issue
#	--cap-add="CAP_SYS_RESOURCE" \
#	--cap-add="CAP_SYS_ADMIN" \
#	--privileged \
#	--ulimit memlock=-1:-1 \
docker run \
	-v "$HOME/cassandra-benchmarking/config/cassandra:/etc/cassandra" \
	-v "$HOME/cassandra-benchmarking/log:/var/lib/cassandra/logs" \
	-v "$HOME/cassandra-benchmarking/config/otel/otel.properties:/etc/otel/otel.properties" \
	-v "/mnt/nvme/cassandra_data:/var/lib/cassandra/data" \
	-p 9042:9042 \
	-p 7000:7000 \
	-p 7199:7199 \
	-p 9160:9160 \
	-u cassandra:cassandra \
	--name=cassandra \
	-d \
	${@:2} \
	ghcr.io/engineersbox/cassandra:5.0
	#sh -c "ulimit -a"

docker logs -f cassandra
