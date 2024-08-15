
IP="192.168.0.149"
IP="192.168.0.100"
DNS="cpy-8a4f6c.local"
CLIENTS=("192.168.0.109" "192.168.0.108" "192.168.0.106")
DNSES=("cpy-8a4f6c.local" "cpy-8a4f6c.local")

# Update these variables
PASSWORD="peace2103"
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
    local client_ip=$1
    local base_url="http://$client_ip"
    local fs_url="$base_url/fs"
    local raw_content="$UPLOAD_DIR/code.py"
    local file_name=$(basename $raw_content)
    local url="$fs_url/$file_name"
    
    echod "Uploading $raw_content to $url"
    curl -u :$PASSWORD -T $raw_content -L --location-trusted $url
    echod "Done"
}

sync_dir() {
    local client_ip=$1
    local base_url="http://$client_ip"
    local fs_url="$base_url/fs"
    
    echod "Syncing $UPLOAD_DIR to $fs_url"
    for file in $UPLOAD_DIR/*; do
        if [ "$(basename $file)" = "code.py" ]; then
            url="$fs_url/$(basename $file)"
        else
            url="$fs_url/lib/$(basename $file)"
        fi
        echod "\tUploading $file to $url"
        curl -u :$PASSWORD -T $file -L --location-trusted $url
    done
    echod "Done"
}


sync_to_clients() {
    for client_ip in "${CLIENTS[@]}"; do
        sync_dir $client_ip
    done
}

upload_to_clients() {
    for client_ip in "${CLIENTS[@]}"; do
        upload $client_ip
    done
}

echod "Config loaded"
