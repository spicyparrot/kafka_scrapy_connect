#!/bin/bash

# Constants
SCRIPT_DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd)"

cd $SCRIPT_DIR

# Load in logging library
. "${SCRIPT_DIR}/../utilities/log.sh"

# Extract kafka version and topics from cmd line args
while [[ $# -gt 0 ]]; do
    case $1 in
        --input-topic)
            INPUT_TOPIC="$2"
            shift
            shift
            ;;
        --output-topic)
            OUTPUT_TOPIC="$2"
            shift
            shift
            ;;
        --error-topic)
            ERROR_TOPIC="$2"
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
if [[ -z $INPUT_TOPIC || -z $OUTPUT_TOPIC || -z $ERROR_TOPIC ]]; then
    error "Can't execute script"
    warn "Usage: $0 --input-topic inputTopic,1 --output-topic outputTopic,1 --error-topic errorTopic,1"
    exit 1
fi

# Function to validate topic format
validate_topic_format() {
    local topic="$1"
    if [[ ! "$topic" =~ ^[a-zA-Z0-9_-]+,[0-9]+$ ]]; then
        error "Invalid format for topic: $topic"
        warn "Usage: $0 --input-topic <topic_name>,<partitions> --output-topic <topic_name>,<partitions> --error-topic <topic_name>,<partitions>"
        exit 1
    fi
}

# Validate topic formats
validate_topic_format "$INPUT_TOPIC"
validate_topic_format "$OUTPUT_TOPIC"
validate_topic_format "$ERROR_TOPIC"

# Concatenate topics into one variable
TOPICS="$INPUT_TOPIC,$OUTPUT_TOPIC,$ERROR_TOPIC"


info "Bringing up local kafka cluster"
docker-compose up -d
sleep 10 

# Log information about connecting to Kafka
info "Please connect to the following localhost:29092 to access Kafka"

# Split the topics string into an array
IFS=',' read -ra TOPIC_PARTITIONS <<< "$TOPICS"

# Print the parsed topic-partition pairs for verification
for ((i=0; i<${#TOPIC_PARTITIONS[@]}; i+=2)); do
    TOPIC="${TOPIC_PARTITIONS[i]}"
    PARTITION="${TOPIC_PARTITIONS[i+1]}"
    info "Creating Kafka topic $TOPIC with $PARTITION partition[s]"
done


./scripts/create_topics.sh --topics $TOPICS