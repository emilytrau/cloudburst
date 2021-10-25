#!/bin/sh

# Wait for database to come up
sleep 15

/opt/munge/sbin/munged --verbose
exec "$@"
