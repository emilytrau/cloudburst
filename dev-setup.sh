#!/bin/sh
# Remove all state and rebuild
docker-compose down --volumes --remove-orphans
docker-compose build
docker-compose run --no-deps --rm --entrypoint /opt/munge/sbin/mungekey slurmctl --verbose
docker-compose run --no-deps --rm --entrypoint /usr/bin/pip slurmctl install -e /client
docker-compose run --no-deps --rm --entrypoint /usr/local/bin/pip backend install -e /app
