#!/bin/sh
# Remove all state and rebuild
docker-compose down -v
docker-compose build
./generate-keys.sh
