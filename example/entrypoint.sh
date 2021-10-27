#!/bin/sh

# Wait for database to come up
echo "Waiting for database..."
sleep 15

/opt/munge/sbin/munged --verbose
test -f /etc/munge-db/munge.key && /opt/munge/sbin/munged --verbose --key-file=/etc/munge-db/munge.key --socket=/opt/munge/var/run/munge/munge.socket.db
exec "$@"
