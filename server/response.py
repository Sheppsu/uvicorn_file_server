from dataclasses import dataclass, field
from typing import Any
import json


@dataclass
class Response:
    code: int
    headers: dict[str | bytes, Any] = field(default_factory=dict)
    body: bytes = b""
    is_file: bool = False
    cache_file: bool = False


class JsonResponse(Response):
    def __init__(self, code, json_object, headers: dict | None = None, encoding="utf-8"):
        if headers is None:
            headers = {}
        headers["Content-Type"] = "application/json"
        super().__init__(
            code,
            headers=headers,
            body=json.dumps(json_object).encode(encoding)
        )


class StaticFileResponse(Response):
    def __init__(self, code, path, headers: dict | None = None):
        if headers is None:
            headers = {}
        super().__init__(
            code,
            headers=headers,
            body=path,
            is_file=True,
            cache_file=True
        )
