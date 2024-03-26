#!/bin/bash

./otelcol-contrib-$OPENTELEMETRY_COLLECTOR_VERSION/otelcol-contrib \
	--config=file:./otelcol-config.yaml \
	1> /var/log/otel/otel.log 2> /var/log/otel/otel_debug.log
