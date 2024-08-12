#!/bin/bash

# This is your CIRCUITPY_WEB_API_PASSWORD in settings.toml
source ./scripts/config.sh

upload
fswatch -o $RAW_CONTENT | while read f; do
  upload
done




# while true; do
#   inotifywait -e modify $RAW_CONTENT
#   echo "Uploading $RAW_CONTENT to $URL"
#   curl -v -u :$PASSWORD -T $RAW_CONTENT -L --location-trusted $URL
# done