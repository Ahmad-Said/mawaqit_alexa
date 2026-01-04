import sqlite3
import time
import functools
import pickle
import hashlib
import os
import random
from pathlib import Path
from typing import Any, Callable


class FileCacheManager:
    """
    Manages the SQLite DB and File storage for the cache.
    Kept separate from the decorator to allow multiple functions to share
    the same cache folder if needed.
    """

    def __init__(self, cache_dir: str, db_name: str = "metadata.db"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / db_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            # OPTIMIZATION: WAL mode allows simultaneous readers and writers
            conn.execute("PRAGMA journal_mode=WAL;")
            # OPTIMIZATION: NORMAL is faster and safe enough for cache data
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("""
                         CREATE TABLE IF NOT EXISTS cache_index
                         (
                             key        TEXT PRIMARY KEY,
                             filename   TEXT NOT NULL,
                             expires_at REAL NOT NULL
                         )
                         """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expires ON cache_index (expires_at)")

    def get_key(self, args, kwargs) -> str:
        """Create a stable SHA256 hash based on function arguments."""
        # We sort kwargs to ensure {'a': 1, 'b': 2} is same as {'b': 2, 'a': 1}
        payload = pickle.dumps((args, sorted(kwargs.items())))
        return hashlib.sha256(payload).hexdigest()

    def get(self, key: str) -> Any:
        """Retrieve value if exists and not expired."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT filename, expires_at FROM cache_index WHERE key = ?", (key,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            filename, expires_at = row

            # Check Expiration
            if time.time() > expires_at:
                # Lazy cleanup: found it, but it's dead. Delete it.
                self.delete(key, filename)
                return None

            # Attempt to load file
            file_path = self.cache_dir / filename
            try:
                with open(file_path, "rb") as f:
                    return pickle.load(f)
            except (FileNotFoundError, EOFError, pickle.UnpicklingError):
                # File corrupted or missing, remove entry
                self.delete(key, filename)
                return None

    def set(self, key: str, value: Any, ttl_seconds: int):
        """Save value to disk and update DB."""
        filename = f"{key}.pkl"
        file_path = self.cache_dir / filename
        expires_at = time.time() + ttl_seconds

        # Write to file first
        with open(file_path, "wb") as f:
            pickle.dump(value, f)

        # Update DB
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO cache_index (key, filename, expires_at)
                VALUES (?, ?, ?)
            """, (key, filename, expires_at))

    def delete(self, key: str, filename: str):
        """Remove file and DB entry."""
        try:
            (self.cache_dir / filename).unlink(missing_ok=True)
        except OSError:
            pass

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache_index WHERE key = ?", (key,))

    def prune_expired(self):
        """Cleanup utility to remove all expired entries."""
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT key, filename FROM cache_index WHERE expires_at < ?", (now,))
            rows = cursor.fetchall()

            if not rows:
                return

            for key, filename in rows:
                try:
                    (self.cache_dir / filename).unlink(missing_ok=True)
                except OSError:
                    pass

            conn.execute("DELETE FROM cache_index WHERE expires_at < ?", (now,))


def persistent_ttl_cache(cache_dir: str, seconds: int, logger_callback=None):
    """
    Decorator that caches results to a folder using SQLite for tracking.
    """
    # Initialize the manager once per decorator usage
    manager = FileCacheManager(cache_dir)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Generate Key
            key = manager.get_key(args, kwargs)

            # 2. Try to get from Cache
            cached_result = manager.get(key)

            if cached_result is not None:
                if logger_callback:
                    logger_callback(f"⚡ [Hit] {key[:8]}...")
                return cached_result

            # 3. Cache Miss - Run Function
            if logger_callback:
                logger_callback(f"🐢 [Miss] Running function...")

            result = func(*args, **kwargs)

            # 4. Save to Cache
            manager.set(key, result, seconds)

            # 5. Occasional Maintenance (1% chance to prune expired items)
            # This prevents the cache from growing infinitely without blocking every call
            if random.random() < 0.01:
                manager.prune_expired()

            return result

        return wrapper

    return decorator
