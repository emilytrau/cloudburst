#!/bin/sh
# Generate development credentials
docker-compose run munge /opt/munge/sbin/mungekey --verbose
