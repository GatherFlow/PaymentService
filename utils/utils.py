

from uuid import uuid3, NAMESPACE_URL
from datetime import datetime, timezone


def group_by(target, k=5) -> list:
    return [target[i:i+k] for i in range(0, len(target), k)]


def now() -> int:
    return round(datetime.now(timezone.utc).timestamp())


def string_to_uuid(string: str) -> str:
    return uuid3(NAMESPACE_URL, string.lower()).hex
