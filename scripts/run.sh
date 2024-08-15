#!/bin/bash

# nodemon -i venv -i .git -i lib -i sabersocket -e py --exec ./scripts/uploader.sh
MODE=$1

# mode can be "all" or "code"
if [ "$MODE" = "all" ]; then
    nodemon -i venv -i .git -i lib -i sabersocket -e py --exec ./scripts/syncer.py sync-to-clients
elif [ "$MODE" = "code" ]; then
    nodemon -i venv -i .git -i lib -i sabersocket -e py --exec ./scripts/syncer.py upload-to-clients
else
    echo "Invalid mode"
fi
