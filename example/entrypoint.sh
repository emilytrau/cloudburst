#!/bin/sh

# Wait for database to come up
echo "Waiting for database..."
sleep 15

/opt/munge/sbin/munged --verbose
exec "$@"
