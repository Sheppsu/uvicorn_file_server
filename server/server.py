from .response import Response
from .routing import Router
from .file_handling import FileHandler

import asyncio
import logging


__all__ = [
    "RequestInfo",
    "router",
    "app"
]


_log = logging.getLogger(__name__)


class RequestInfo:
    __slots__ = (
        "server",
        "client",
        "scheme",
        "method",
        "root_path",
        "path",
        "query_string",
        "headers",
        "_receive",
        "body"
    )
    server: tuple[str, int]  # host, port
    client: tuple[str, int]  # host, port
    scheme: str
    method: str
    root_path: str
    path: str
    query_string: bytes
    headers: dict[str, bytes]

    def __init__(self, receive, *args, **kwargs):
        self._receive = receive
        self.body: bytes | None = None
        for i, arg in enumerate(args):
            setattr(self, self.__slots__[i], arg)
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def from_scope(cls, scope, receive):
        headers = {}
        for header in scope["headers"]:
            headers[header[0].decode()] = header[1]
        return cls(
            receive,
            scope["server"],
            scope["client"],
            scope["scheme"],
            scope["method"],
            scope["root_path"],
            scope["path"],
            scope["query_string"],
            headers
        )

    async def read_body(self):
        if self.body is not None:
            return
        self.body = b""
        more = True
        while more:
            msg = await self._receive()
            self.body += msg.get("body", b"")
            more = msg.get("more_body", False)


_file_handler = FileHandler()
router = Router()


def _convert_headers(headers: dict):
    headers_list = []
    for k, v in headers.items():
        if type(k) != bytes:
            k = k.encode("utf-8")
        if type(v) != bytes:
            v = str(v).encode("utf-8")
        headers_list.append((k, v))
    return headers_list


async def _send_response(send, response: Response):

    await send({
        "type": "http.response.start",
        "status": response.code,
        "headers": _convert_headers(response.headers)
    })
    await send({
        "type": "http.response.body",
        "body": response.body if not response.is_file else _file_handler.get_file_contents(response.body, response.cache_file)
    })


async def app(scope, receive, send):
    assert scope['type'] == 'http'

    req = RequestInfo.from_scope(scope, receive)
    handler, kwargs = router.get_handler(req.path, req.method)
    if handler is None:
        return await _send_response(send, Response(404))
    resp = await handler(req, **kwargs)
    if not isinstance(resp, Response):
        raise TypeError(f"{handler.__code__.co_name} handler did not return a Response object")
    await _send_response(send, resp)
