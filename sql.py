import sqlite3 as sql
import threading
from time import time


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
        cursor.execute(f"UPDATE files SET views = views + 1, lastviewed = {round(time())} WHERE code = '{code}")
        self.db.commit()
