from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STORAGE_DIR = BASE_DIR / "storage"
WORKSPACE_DIR = BASE_DIR / "workspaces"

REDIS_HOST = "localhost"
REDIS_PORT = 6378

CMD_BINARY = "/www/server/nodejs/v20.13.1/bin/cmd"

API_KEY = "sk-wempy-9d8f4a2c7b1e6f3a8c5d9e2f7b4a1c6d"