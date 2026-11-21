"""Tiny per-chat key/value store on SQLite."""
import sqlite3
import threading

from .config import DB_PATH

_lock = threading.Lock()
_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
_conn.execute(
    "CREATE TABLE IF NOT EXISTS kv (chat_id INTEGER, k TEXT, v TEXT, PRIMARY KEY (chat_id, k))"
)
_conn.commit()


def get(chat_id, k, default=None):
    with _lock:
        row = _conn.execute("SELECT v FROM kv WHERE chat_id=? AND k=?", (chat_id, k)).fetchone()
    return row[0] if row else default


def put(chat_id, k, v):
    with _lock:
        _conn.execute("INSERT OR REPLACE INTO kv VALUES (?,?,?)", (chat_id, k, str(v)))
        _conn.commit()


def delete(chat_id, k):
    with _lock:
        cur = _conn.execute("DELETE FROM kv WHERE chat_id=? AND k=?", (chat_id, k))
        _conn.commit()
        return cur.rowcount > 0


def items(chat_id, prefix):
    """Return [(key_without_prefix, value)] for keys starting with prefix."""
    with _lock:
        rows = _conn.execute(
            "SELECT k, v FROM kv WHERE chat_id=? AND substr(k,1,?)=? ORDER BY k",
            (chat_id, len(prefix), prefix),
        ).fetchall()
    return [(k[len(prefix):], v) for k, v in rows]


def clear(chat_id, prefix):
    with _lock:
        cur = _conn.execute(
            "DELETE FROM kv WHERE chat_id=? AND substr(k,1,?)=?", (chat_id, len(prefix), prefix)
        )
        _conn.commit()
        return cur.rowcount
