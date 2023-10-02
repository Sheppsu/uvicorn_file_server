import logging
import threading
import queue
import time


_log = logging.getLogger(__name__)


class FileHandler:
    def __init__(self):
        self._buffer = {}
        self._lock = threading.Lock()
        self._uncache_thread_running = threading.Event()
        self._uncache_queue = queue.Queue()

    def get_file_contents(self, path, cache=False):
        self._lock.acquire()
        if path in self._buffer:
            content = self._buffer[path]
            self._lock.release()
            return content
        if cache:
            self._cache_file(path)
            content = self._buffer[path]
            self._lock.release()
            return content
        self._lock.release()
        with open(path, "rb") as f:
            return f.read()

    def _cache_file(self, path):
        _log.info(f"Caching {path}")
        with open(path, "rb") as f:
            self._buffer[path] = f.read()
        self._uncache_queue.put((path, time.monotonic()+60))
        if not self._uncache_thread_running.is_set():
            threading.Thread(target=self._uncache_loop).start()
            if not self._uncache_thread_running.wait(timeout=1):
                _log.warning("Uncache thread did not start after a full second")

    def _uncache_loop(self):
        self._uncache_thread_running.set()
        while True:
            try:
                path, wait_until = self._uncache_queue.get(timeout=3)
            except queue.Empty:
                break
            time.sleep(wait_until-time.monotonic())
            self._uncache_file(path)
        self._uncache_thread_running.clear()

    def _uncache_file(self, path):
        self._lock.acquire()
        _log.info(f"Uncaching {path}")
        del self._buffer[path]
        self._lock.release()
