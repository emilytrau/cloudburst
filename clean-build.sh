#!/bin/sh
# Remove all state and rebuild
docker-compose down -v
docker-compose build
docker-compose run munge /opt/munge/sbin/mungekey --verbose
docker-compose run slurmctl pip install -e /client
