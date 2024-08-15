#!/bin/bash

echo "Uploading $1 to the server"
cp -r $1 ./src/upload
# ./scripts/uploader.sh