#!/bin/sh
# Remove all state and rebuild
docker-compose down -v
docker-compose build
docker-compose run --rm --entrypoint /opt/munge/sbin/mungekey slurmctl --verbose
docker-compose run --rm --entrypoint /usr/bin/pip slurmctl install -e /client
