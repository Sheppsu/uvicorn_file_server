import sqlite3 as sql
import threading
from time import time
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileInfo:
    code: str
    path: str
    views: int
    last_viewed: datetime
    content_type: str

    @classmethod
    def from_data(cls, data):
        return cls(
            code=data[0],
            path=data[1],
            views=data[2],
            last_viewed=datetime.fromtimestamp(data[3]),
            content_type=data[4]
        )


class Database:
    def __init__(self):
        self.db = sql.connect("files.db")
        self._lock = threading.Lock()

    def add_file(self, code: str, filename: str, content_type: str):
        cursor = self.db.cursor()
        cursor.execute(f"INSERT INTO files (code, filename, content_type) VALUES ('{code}', '{filename}', '{content_type}')")
        self.db.commit()

    def get_file(self, code):
        cursor = self.db.cursor()
        cursor.execute(f"SELECT filename, content_type FROM files WHERE code = '{code}'")
        return cursor.fetchone()

    def update_file_stats(self, code):
        cursor = self.db.cursor()
        cursor.execute(f"UPDATE files SET views = views + 1, lastviewed = {round(time())} WHERE code = '{code}'")
        self.db.commit()

    def get_top_files(self, limit=10):
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM files ORDER BY views DESC LIMIT {limit}")
        return map(FileInfo.from_data, cursor.fetchall())

    def get_recent_files(self, limit=10):
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM files ORDER BY lastviewed DESC LIMIT {limit}")
        return map(FileInfo.from_data, cursor.fetchall())

    def get_mimetype_files(self, mimetype, limit=10):
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM files WHERE content_type = '{mimetype}' LIMIT {limit}")
        return map(FileInfo.from_data, cursor.fetchall())

    def print_files(self, files):
        print("-" * 106)
        for file in files:
            print(
                f"| {file.code: <8} | {file.path: <20} | {file.views: <3} | {file.last_viewed.isoformat(): <19} | {file.content_type: <10} |")
            print("-" * 106)
