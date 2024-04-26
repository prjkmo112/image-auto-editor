#!/bin/sh
echo "exec entry.sh"

set -e

# set environment
{ \
echo "IS_INSIDE_IN_DOCKER_NOT_VALUE_FOR_USER=$IS_INSIDE_IN_DOCKER_NOT_VALUE_FOR_USER"; \
echo "LANGUAGE=$LANGUAGE"; \
echo "FRONT_BACK_HOST=$FRONT_BACK_HOST"; \
echo "BACK_API_TIMEOUT=$BACK_API_TIMEOUT"; \
} > /home/src/iae-setter/.env

cd /home/src/iae-setter

npm run build

# run react
echo "done entry.sh"

exec "$@"