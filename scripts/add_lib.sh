#!/bin/bash

echo "Uploading $1 to the server"
cp $1 ./src/upload
./scripts/uploader.sh