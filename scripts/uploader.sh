#!/bin/bash

# This is your CIRCUITPY_WEB_API_PASSWORD in settings.toml

source ./scripts/config.sh

echo "Uploading $RAW_CONTENT to $URL"

curl -u :$PASSWORD -T $RAW_CONTENT -L --location-trusted $URL
echo "Done"
