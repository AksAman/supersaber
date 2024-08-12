PASSWORD="peace2103"
IP="192.168.0.123"
DNS="cpy-8a4f6c.local"
BASE_URL="http://$IP"
UPLOAD_DIR="src/upload"

FS_URL="$BASE_URL/fs"

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
GRAY='\033[1;30m'
BOLD='\033[1m'
NC='\033[0m' # No Color
# Default color
DEFAULT_COLOR=$GREEN
echod() {
    local message=$1
    local color=${2:-$DEFAULT_COLOR}
    printf "${GRAY}${BOLD}$(date)${NC} ${color}${message}${NC}\n"
}



upload() {
    RAW_CONTENT="$UPLOAD_DIR/code.py"
  file_name=$(basename $RAW_CONTENT)
  URL="$FS_URL/$file_name"
  echod "Uploading $RAW_CONTENT to $URL"
  curl -u :$PASSWORD -T $RAW_CONTENT -L --location-trusted $URL
  echod "Done"
}

sync_dir() {
    echod "Syncing $UPLOAD_DIR to $FS_URL"
    for file in $UPLOAD_DIR/*; do
        if [ "$(basename $file)" = "code.py" ]; then
            URL="$FS_URL/$(basename $file)"
        else
            URL="$FS_URL/lib/$(basename $file)"
        fi
        echod "\tUploading $file to $URL"
        curl -u :$PASSWORD -T $file -L --location-trusted $URL
    done
    echod "Done"
}
echod "Config loaded"
