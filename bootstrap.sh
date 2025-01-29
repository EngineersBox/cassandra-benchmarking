#!/usr/bin/env bash

set -o errexit -o pipefail -o noclobber

source /var/lib/cluster/node_env
pushd /var/lib/cluster


echo "[INFO] Starting $APPLICATION_VARIANT services"
docker compose -f /var/lib/cluster/docker/$APPLICATION_VARIANT/docker-compose.yaml up -d

if [ "x$INVOKE_INIT" = "x" ]; then
    echo "[INFO] No init invocation required, bootstrapping succeeded"
    popd
    exit 0
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
    *)
        ;;
esac

popd
echo "[INFO] Node bootstrapping suceeded"
