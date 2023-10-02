import re
from inspect import iscoroutinefunction


class Path:
    def __init__(self, fn, path: str, method: str, regex=False, ignorecase=True):
        self.fn = fn
        self.path: str | re.Pattern = path
        self.method = method.upper()
        self.regex = regex
        self.ignorecase = ignorecase
        if self.regex:
            self.path = re.compile(self.path, re.IGNORECASE if ignorecase else 0)

    def match(self, req_path: str):
        if self.regex:
            m = re.match(self.path, req_path)
            return (False, {}) if m is None else (True, m.groupdict())

        path = self.path
        if self.ignorecase:
            req_path = req_path.lower()
            path = path.lower()
        return path == req_path, {}


class Router:
    def __init__(self):
        self.paths: list[Path] = []

    def get_handler(self, req_path, method):
        for path in self.paths:
            if path.method != method:
                continue
            match, kwargs = path.match(req_path)
            if match:
                return path.fn, kwargs
        return None, {}

    def route(self, path: str, method="GET", regex=False):
        def decorator(fn):
            if not iscoroutinefunction(fn):
                raise TypeError("Must use coroutine functions to handle requests")
            self.paths.append(Path(fn, path, method, regex))
        return decorator