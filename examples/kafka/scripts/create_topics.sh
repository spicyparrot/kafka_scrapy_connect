#!/bin/bash
# Script directory
SCRIPT_DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd)"

# Load in logging library
. "${SCRIPT_DIR}/../../utilities/log.sh"

# Parse command line arguments
while [[ $# -gt 0 ]];do
    case $1 in
        --topics)
            KAFKA_TOPIC_LIST="$2"
            shift
            shift
            ;;
        *)
            error "Invalid argument: $1"
            exit 1
            ;;
    esac
done

# Check that the arguments were passed correctly
if [[ -z $KAFKA_TOPIC_LIST ]]; then
    warn "Usage: $0 --topics foobar,1,test,3"
    exit 1
fi

if [ -n "$KAFKA_TOPIC_LIST" ]; then
  IFS=',' read -ra TOPICS <<< "$KAFKA_TOPIC_LIST"

  DOCKER_COMMAND="docker exec kafka bash -c \""

  for (( i=0; i<${#TOPICS[@]}; i+=2 )); do
    topic=${TOPICS[i]}
    partitions=${TOPICS[i+1]}
    DOCKER_COMMAND+=" kafka-topics --create --bootstrap-server localhost:9092 --topic $topic --partitions $partitions;"
  done
  DOCKER_COMMAND+="\" "
  eval $DOCKER_COMMAND
else
  info "No kafka topics to create."
fi