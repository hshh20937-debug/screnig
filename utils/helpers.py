import json
from datetime import datetime


def load_json(path: str, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default or {}


def save_json(path: str, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
