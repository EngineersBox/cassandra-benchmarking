# cassandra-benchmarking
Cassandra Benchmarking Utilities

## Build

### Cassandra

In order to create a cassandra image, run the following

```bash
docker build -t ghcr.io/engineersbox/cassandra:5.0 -f docker/instance/cassandra.dockerfile .
```

You can optionally supply a repo and commit-ish marker to build from:

* `--build-arg="REPOSITORY=<repo>"` defaulting to <https://github.com/engineersbox/cassandra>
* `--build-arg="COMMIT_ISH=<commit | branch | tag>"` defaulting to `cassandra-5.0`
* `--build-arg="UID=<cassandra user uid>"` defaulting to `1000`
* `--build-arg="GID=<casasndra group id>"` defaulting to `1000`
* `--build-arg="OTEL_COLLECTOR_JAR_VERSION=<version>"` defaulting to `v2.2.0`
* `--build-arg="OTEL_JMX_JAR_VERSION=<version>"` defaulting to `v1.32.0`

The image can then be pushed to the GitHub container repository

```bash
docker push ghcr.io/engineersbox/cassandra:5.0
```

## OpenTelemetry Collector

```bash
docker build -t ghcr.io/engineersbox/otel-collector:latest -f docker/collector/otel.dockerfile .
```

* `--build-arg="OTEL_JMX_JAR_VERSION=<version>"` defaulting to `v1.32.0`

```bash
docker push ghcr.io/engineersbox/otel-collector:latest
```

## Startup

### Casandra

Starting cassandra is straightforward, it requires

```bash
docker run \
    -v "./config/cassandra:/etc/cassandra" \
    -v "./log:/var/lib/cassandra/logs" \
    -v "./config/otel/otel.properties:/etc/otel/otel.properties" \
    -p 7000:7000 \
    -p 7001:7001 \
    -p 7199:7199 \
    -p 9160:9160 \
    -p 9042:9042 \
    -u cassandra:cassandra \
    --name=cassandra \
    -d \
    ghcr.io/engineersbox/cassandra:5.0
```

### OpenTelemetry Collector

```bash
docker run \
    -v "./config/otel/otel-collector-config.yaml:/otel-lgtm/otelcol-config.yaml" \
    -v "./log:/var/log/otel" \
    -p 3000:3000 \
    -p 4317:4317 \
    -p 4318:4318 \
    --name=otel \
    -d \
    ghcr.io/engineersbox/otel-collector:latest
```

## Remote Access

Deploying the collector or cassandra on a remote instance will require you to access the services
by forwarding the relevant port to your local machine via SSH (if it is not publically visible).

```bash
ssh -L <port>:localhost:<port> <remote instance>
```

## Configuration

* See the `start_cassandra.sh` script header for variables that can be set to customise the deployment.
* Cassandra can be configured via the `cassandra.yaml` file, there is documentation within the file describing all avilable properties and their usage.
* The OTEL agent can be configured via `otel.properties`, see <https://opentelemetry.io/docs/languages/java/automatic/configuration/> for details on valid properties.
* OTEL collector can be configured via `otel-collector-config.yaml`.

## Collector

![OTEL, Loki, Prometheus, Tempo, Grafana](./docs/otel_lgtm.png)
