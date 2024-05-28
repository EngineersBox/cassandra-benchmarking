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

### Configuration

Ensure you set the addresses for the Cassandra instance and collector instances within the
`config/otel/otel-collector.properties` and `config/otel/otel-instance.properties` config
files.

Choose any additional appropriate configurations for Cassandra within the `config/cassandra`
directory.

This repo relies on the `vmprobe` utility, so make sure that is installed with your favourite
package manager.

### Casandra

Starting cassandra is straightforward, it requires the usage of the following and a parameter
denoting whether to remove all data and flush page cache. It can also be supplimented with
additional arguments to the `docker run` command.

```bash
sudo ./scripts/run_cassandra.sh <refresh: y|n> [...<docker args>]
```

### OpenTelemetry Collector

Similarly for the OTEL collector with:

```bash
sudo ./scripts/run_otel.sh <refresh: y|n> [... <docker args>]
```

## Remote Access

Deploying the collector or cassandra on a remote instance will require you to access the services
by forwarding the relevant port to your local machine via SSH (if it is not publically visible).

```bash
ssh -L <port>:localhost:<port> <remote instance>
```

## User Permissions

Assuming that you have the container user congiured as `1000:1000` and your user on the host mapped
as `<user>:100000:65536` in both `/etc/subuid` and `/etc/subgid`, then you will need ensure that any
directories/files mounted into the container used by the cassandra user are owned by `100999:100999`.

The reason for this is that the mapping will move any host users from 0 to 100000 up by 100000. As such
a host uid:gid binding of `1000:1000` corresponds to `100999:100999`. To do this, just run the following
over anything you intend to mount into the Cassandra container:

```bash
sudo chmod -R 100999:100999 <path>
```

## Configuration

* See the `start_cassandra.sh` script header for variables that can be set to customise the deployment.
* Cassandra can be configured via the `cassandra.yaml` file, there is documentation within the file describing all avilable properties and their usage.
* The OTEL agent can be configured via `otel.properties`, see <https://opentelemetry.io/docs/languages/java/automatic/configuration/> for details on valid properties.
* OTEL collector can be configured via `otel-collector-config.yaml`.

## Collector

![OTEL, Loki, Prometheus, Tempo, Grafana](./docs/otel_lgtm.png)
