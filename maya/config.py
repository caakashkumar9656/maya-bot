import os
from pathlib import Path


def _load_env():
    p = Path(__file__).resolve().parent.parent / ".env"
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env()

BOT_NAME = "Maya"
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
SUDO_USERS = {int(x) for x in os.getenv("SUDO_USERS", "").replace(" ", "").split(",") if x.isdigit()}
DB_PATH = os.getenv("DB_PATH", "maya.db")
REPO_URL = os.getenv("REPO_URL", "https://github.com/YOUR_USERNAME/maya-bot")
