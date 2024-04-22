# cassandra-benchmarking
Cassandra Benchmarking Utilities

## Build

In order to create a cassandra image, run the following

```bash
docker build -t ghcr.io/engineersbox/:5.0 -f docker/instance/cassandra.dockerfile .
```

You can optionally supply a repo and commit-ish marker to build from:

* `--build-arg="REPOSITORY=<repo>"` defaulting to <https://github.com/engineersbox/cassandra>
* `--build-arg="COMMIT_ISH=<commit | branch | tag>"` defaulting to `cassandra-5.0`

The image can then be pushed to the GitHub container repository

```bash
docker push ghcr.io/engineersbox/cassandra:5.0
```

## Startup

Run the `start_cassandra.sh` script to create a container with Cassandra (called cassandra) and another container with an OpenTelemetry collector.

Both of these containers are mapped to the host network deployable in a manner acceptable for a server.

## Configuration

* See the `start_cassandra.sh` script header for variables that can be set to customise the deployment.
* Cassandra can be configured via the `cassandra.yaml` file, there is documentation within the file describing all avilable properties and their usage.
* The OTEL agent can be configured via `otel.properties`, see <https://opentelemetry.io/docs/languages/java/automatic/configuration/> for details on valid properties.
* OTEL collector can be configured via `otel-collector-config.yaml`.

## Collector

![OTEL, Loki, Prometheus, Tempo, Grafana](./docs/otel_lgtm.png)
