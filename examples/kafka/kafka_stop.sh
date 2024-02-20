#!/bin/bash

# Constants
SCRIPT_DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd)"

cd $SCRIPT_DIR

# Load in logging library
. "${SCRIPT_DIR}/../utilities/log.sh"

warn "Bringing down local kafka cluster 🫳"
docker-compose down
sleep 5

# Log information about connecting to Kafka
warn "Nuking images ☢️"
docker system prune -a -f
