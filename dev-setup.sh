#!/bin/sh
# Remove all state and rebuild
docker-compose down --volumes --remove-orphans
docker-compose build
docker-compose run --no-deps --rm --entrypoint /opt/munge/sbin/mungekey cloud-slurmctl --verbose
docker-compose run --no-deps --rm --entrypoint /opt/munge/sbin/mungekey static-slurmctl --verbose
docker-compose run --no-deps --rm --entrypoint /opt/munge/sbin/mungekey slurmdb --verbose
docker-compose run --no-deps --rm --entrypoint /usr/bin/pip cloud-slurmctl install -e /client
docker-compose run --no-deps --rm --entrypoint /usr/bin/pip backend install -e /app
