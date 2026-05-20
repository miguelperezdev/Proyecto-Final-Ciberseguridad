import sqlite3
import datetime
import os
from app.config import DB_FILE

def init_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    con = sqlite3.connect(DB_FILE)
    con.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            task TEXT NOT NULL,
            user_msg TEXT NOT NULL,
            ia_resp TEXT,
            blocked INTEGER DEFAULT 0,
            block_reason TEXT
        )
    """)
    con.commit()
    con.close()

def log_interaction(task: str, user_msg: str, ia_resp: str = None,
                    blocked: bool = False, block_reason: str = None):
    con = sqlite3.connect(DB_FILE)
    con.execute(
        "INSERT INTO interactions(timestamp,task,user_msg,ia_resp,blocked,block_reason) VALUES(?,?,?,?,?,?)",
        (datetime.datetime.now().isoformat(), task, user_msg, ia_resp, int(blocked), block_reason)
    )
    con.commit()
    con.close()

def get_recent_logs(limit: int = 50):
    con = sqlite3.connect(DB_FILE)
    rows = con.execute(
        "SELECT id,timestamp,task,user_msg,ia_resp,blocked,block_reason "
        "FROM interactions ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    con.close()

    return [
        {
            "id": r[0],
            "timestamp": r[1],
            "task": r[2],
            "user_msg": r[3],
            "ia_resp": r[4],
            "blocked": bool(r[5]),
            "block_reason": r[6],
        }
        for r in rows
    ]

def get_blocked_logs():
    con = sqlite3.connect(DB_FILE)
    rows = con.execute(
        "SELECT id,timestamp,task,user_msg,block_reason "
        "FROM interactions WHERE blocked=1 ORDER BY id DESC"
    ).fetchall()
    con.close()

    return [
        {
            "id": r[0],
            "timestamp": r[1],
            "task": r[2],
            "user_msg": r[3],
            "block_reason": r[4],
        }
        for r in rows
    ]