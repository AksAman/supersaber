#!/bin/bash

# This is your CIRCUITPY_WEB_API_PASSWORD in settings.toml
source ./scripts/config.sh

curl -u :$PASSWORD -T $RAW_CONTENT -L --location-trusted $URL
fswatch -o $RAW_CONTENT | while read f; do
  echo "Uploading $RAW_CONTENT to $URL"
  curl -u :$PASSWORD -T $RAW_CONTENT -L --location-trusted $URL
    echo "Done"
done




# while true; do
#   inotifywait -e modify $RAW_CONTENT
#   echo "Uploading $RAW_CONTENT to $URL"
#   curl -v -u :$PASSWORD -T $RAW_CONTENT -L --location-trusted $URL
# done