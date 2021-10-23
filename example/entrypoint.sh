#!/bin/sh

/opt/munge/sbin/munged --verbose
exec "$@"
