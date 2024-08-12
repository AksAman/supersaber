#!/bin/bash

# This is your CIRCUITPY_WEB_API_PASSWORD in settings.toml

source ./scripts/config.sh


# curl to /cp/serial/
URL="$BASE_URL/cp/serial/"
echo "Uploading $RAW_CONTENT to $URL"

curl -v -u :$PASSWORD -L --location-trusted $URL