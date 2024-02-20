#!/bin/bash

# ANSI colour palette
RESET='\033[0m'
GREEN='\033[38;5;2m'
RED='\033[38;5;1m'
YELLOW='\033[38;5;3m'
MAGENTA='\033[38;5;5m'
CYAN='\033[38;5;6m'

# Log message to stderr
log() {
    printf "%b\n" "$*" >&2
}

logColoured() {
    local colour="$1"
    local message="$2"
    local before="${message%%:*}" # Extracts text before the first ":"
    local after="${message#*:}"  # Extracts text after the first ":"
    echo -e "\n${before} ==> ${colour}${after}${RESET}"
}

logColouredWrapper() {
    local colour="$1"
    local prefix="$2"
    logColoured "$colour" "$prefix: $*"
}

logGreen() {
    logColouredWrapper "$GREEN" "INFO"
}

logYellow() {
    logColouredWrapper "$YELLOW" "WARN"
}

logPurple() {
    logColouredWrapper "$MAGENTA" "OTHER"
}

logCyan() {
    logColouredWrapper "$CYAN" "OTHER"
}

# Log info message
info() {
    logColoured "$GREEN" "INFO: $*"
}

# Log warning message
warn() {
    logColoured "$YELLOW" "WARN: $*"
}

# Log error message
error() {
    logColoured "$RED" "ERROR: $*"
}

silence() {
    if ${DEBUG_MODE:-false}; then
        "$@"
    else
        "$@" >/dev/null 2>&1
    fi
}