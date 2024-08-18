#!/usr/bin/env python3

import datetime
import json
import os
from pathlib import Path

import dotenv

dotenv.load_dotenv()
import click
import requests
from pydantic import BaseModel


def read_clients():
    path = Path("scripts/ips.txt")
    if not path.exists():
        path.touch()
        print("Created ips.txt")
        print("Please add the client IPs to the file")
        exit(1)

    with open(path) as f:
        ips = f.readlines()
    return list(set([ip.strip() for ip in ips if ip.strip() and not ip.startswith("#")]))


# Constants
DNS = "cpy-8a4f6c.local"
CLIENTS = read_clients()
if not CLIENTS:
    raise ValueError("No clients found in ips.txt")

DNSES = [
    "cpy-8a4f6c.local",
    "cpy-8a4f6c.local",
]

PASSWORD = os.getenv("CIRCUITPY_WEB_API_PASSWORD", "")
if not PASSWORD:
    raise ValueError("CIRCUITPY_WEB_API_PASSWORD is not set")


UPLOAD_DIR = Path("src/upload")
BASE_URL = "http://example.com"
FS_URL = f"{BASE_URL}/fs"

# Define color codes
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
GRAY = "\033[1;30m"
BOLD = "\033[1m"
NC = "\033[0m"  # No Color
DEFAULT_COLOR = GREEN


class CPYFile(BaseModel):
    name: str
    modified_ns: int
    directory: bool
    file_size: int
    path: str = ""
    level: int = 0

    @property
    def modified_at(self):
        return datetime.datetime.fromtimestamp(self.modified_ns / 1e9)


class CPYFileStructure(BaseModel):
    block_size: int
    files: list[CPYFile]


def echod_files(files: list[CPYFile]):
    # Sort files by path
    files.sort(key=lambda x: x.path)
    for file in files:
        indent = " " * (file.level * 4)
        prefix = "📁" if file.directory else "📄"
        echod(f"{indent}{prefix} {file.path} {file.modified_at}")


def get_files_from_client(ip: str) -> list[CPYFile]:
    def ls_path(path, level=0):
        path = path.strip("/")
        endpoint = f"http://{ip}/fs/{path}/"
        response = requests.get(endpoint, auth=("", PASSWORD), headers={"Accept": "application/json"})
        if response.status_code == 200:
            fs_structure = CPYFileStructure(**response.json())
            all_files = []
            for file in fs_structure.files:
                file.level = level
                file.path = f"{path}/{file.name}"
                if file.directory:
                    all_files.append(file)
                    all_files.extend(ls_path(f"{path}/{file.name}", level + 1))
                else:
                    all_files.append(file)
            return all_files
        else:
            echod(f"Failed to get files from {ip}, status code: {response.status_code}")
            return []

    """List files from all clients"""
    path = ""
    files = ls_path(path)
    return files


def echod(message, color=DEFAULT_COLOR):
    print(f"{GRAY}{BOLD}{datetime.datetime.now()}{NC} {color}{message}{NC}")


def upload(client_ip):
    base_url = f"http://{client_ip}"
    fs_url = f"{base_url}/fs"

    files = ["code.py", "decoders.py"]

    for file in files:
        raw_content = UPLOAD_DIR / file
        file_name = raw_content.name
        if file_name == "code.py":
            url = f"{fs_url}/{file_name}"
        else:
            url = f"{fs_url}/lib/{file_name}"

        echod(f"Uploading {raw_content} to {url}")
        requests.put(url, auth=("", PASSWORD), data=open(raw_content, "rb"))
        echod("Done")


def put_request(url, file_path: Path, is_directory=False):
    headers = {}
    modified_time = int(file_path.stat().st_mtime * 1000)
    headers["X-Timestamp"] = str(modified_time)

    if is_directory:
        response = requests.put(url, auth=("", PASSWORD), headers=headers)
    else:
        response = requests.put(url, auth=("", PASSWORD), data=open(file_path, "rb"), headers=headers)

    success = response.status_code == 204
    color = GREEN if success else RED
    message = "Directory Created" if success else "Directory create Failed"
    echod(f"\t\t{message} {file_path} {response.status_code}", color=color)
    return response


def __sync__(relative_path: Path, file_path: Path, fs_url: str, server_files_lut: dict[str, int] | None = None):
    def __sync_dir__(dir_path: Path):
        dir_path_relative = dir_path.relative_to(UPLOAD_DIR)
        dir_url = f"{fs_url}/lib/{dir_path_relative}/"
        if server_files_lut:
            server_dir_modified_ns = server_files_lut.get(str(dir_path_relative), 0)
            local_dir_modified_ns = dir_path.stat().st_mtime_ns
            local_dir_modified_ns = int(int(local_dir_modified_ns / 1e9) * 1e9)
            if local_dir_modified_ns <= server_dir_modified_ns:
                echod(f"\tSkipping {dir_url}, no changes detected", color=YELLOW)
                return
        echod(f"\tCreating directory {dir_url}", color=YELLOW)
        put_request(dir_url, file_path, is_directory=True)

    if relative_path.name == "code.py":
        url = f"{fs_url}/{relative_path}"
    else:
        url = f"{fs_url}/lib/{relative_path}"

    # Create subdirectories if necessary
    if relative_path.parent != Path("."):
        dir_path = file_path.parent
        __sync_dir__(dir_path)
    echod(f"\tUploading {file_path} to {url}", color=BLUE)
    put_request(url, file_path)


def sync_dir(client_ip):
    base_url = f"http://{client_ip}"
    fs_url = f"{base_url}/fs"

    echod(f"Syncing {UPLOAD_DIR} to {fs_url}")
    for file_path in UPLOAD_DIR.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(UPLOAD_DIR)
            __sync__(relative_path, file_path, fs_url)
    echod("Done")


def sync_dir_if_changed(client_ip):
    server_files = get_files_from_client(client_ip)
    echod(f"Received {len(server_files)} files from {client_ip}")
    server_files_lut = {file.path: file.modified_ns for file in server_files}

    with open("s1.json", "w") as f:
        json.dump(server_files, f, default=lambda x: x.dict(), indent=4)
    with open("s.json", "w") as f:
        json.dump(server_files_lut, f, default=lambda x: x.dict(), indent=4)

    base_url = f"http://{client_ip}"
    fs_url = f"{base_url}/fs"

    echod(f"Syncing {UPLOAD_DIR} to {fs_url}")

    for file_path in UPLOAD_DIR.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(UPLOAD_DIR)
            local_modified_ns = file_path.stat().st_mtime_ns
            local_modified_ns = int(int(local_modified_ns / 1e9) * 1e9)
            prefix = "lib/" if relative_path.name != "code.py" else ""
            key = prefix + str(relative_path)
            server_modified_ns = server_files_lut.get(key, 0)
            echod(f"{str(relative_path)} Local {local_modified_ns} Server {server_modified_ns}")

            if local_modified_ns > server_modified_ns:
                __sync__(relative_path, file_path, fs_url, server_files_lut)
            else:
                echod(f"\tSkipping {file_path}, no changes detected", color=YELLOW)

    echod("Done")


@click.group()
def cli():
    """CLI for managing uploads and syncs"""
    echod("Config loaded")


@cli.command()
@click.argument("client_ip")
def upload_code(client_ip):
    """Upload code.py to a specific client"""
    upload(client_ip)


@cli.command()
@click.argument("client_ip")
def sync_dir_cmd(client_ip):
    """Sync directory to a specific client"""
    sync_dir(client_ip)


@cli.command()
def sync_to_clients():
    """Sync directory to all clients"""
    for client_ip in CLIENTS:
        sync_dir(client_ip)


@cli.command()
def sync_to_clients2():
    """Sync directory to all clients"""
    for client_ip in CLIENTS:
        print(f"Syncing to {client_ip}")
        sync_dir_if_changed(client_ip)


@cli.command()
def upload_to_clients():
    """Upload code.py to all clients"""
    for client_ip in CLIENTS:
        upload(client_ip)


@cli.command()
def ls():
    """List files from all clients"""
    for client_ip in CLIENTS:
        files = get_files_from_client(client_ip)
        echod_files(files)


if __name__ == "__main__":
    cli()
