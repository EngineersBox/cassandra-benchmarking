#!/usr/bin/env bash

PWD="$(pwd)"

endpath=$(basename "$PWD")
case "$(basename "$PWD")" in
  cassandra-benchmarking) echo "yeah" ;;
  *) echo "nah" ;;
esac
