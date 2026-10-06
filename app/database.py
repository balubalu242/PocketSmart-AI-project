import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any

from app.config import get_settings


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connection():
    settings = get_settings()
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                planner_type TEXT NOT NULL,
                request_json TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """
        )


def create_user(email: str, password_hash: str, full_name: str) -> dict[str, Any]:
    with connection() as conn:
        created_at = utc_now()
        cur = conn.execute(
            "INSERT INTO users(email, password_hash, full_name, created_at) VALUES (?, ?, ?, ?)",
            (email.lower().strip(), password_hash, full_name.strip(), created_at),
        )
        return {
            "id": int(cur.lastrowid),
            "email": email.lower().strip(),
            "password_hash": password_hash,
            "full_name": full_name.strip(),
            "created_at": created_at,
        }


def get_user(user_id: int) -> dict[str, Any] | None:
    with connection() as conn:
        row = conn.execute(
            "SELECT id, email, password_hash, full_name, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def get_user_by_email(email: str) -> dict[str, Any] | None:
    with connection() as conn:
        row = conn.execute(
            "SELECT id, email, password_hash, full_name, created_at FROM users WHERE email = ?",
            (email.lower().strip(),),
        ).fetchone()
    return dict(row) if row else None


def save_recommendation(
    user_id: int,
    planner_type: str,
    request_data: dict[str, Any],
    result_data: dict[str, Any],
) -> int:
    with connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO recommendations(
                user_id, planner_type, request_json, result_json, created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                planner_type,
                json.dumps(request_data, ensure_ascii=False),
                json.dumps(result_data, ensure_ascii=False),
                utc_now(),
            ),
        )
        return int(cur.lastrowid)


def list_history(user_id: int, limit: int = 50) -> list[dict[str, Any]]:
    with connection() as conn:
        rows = conn.execute(
            """
            SELECT id, planner_type, request_json, result_json, created_at
            FROM recommendations
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()

    output = []
    for row in rows:
        output.append(
            {
                "id": row["id"],
                "planner_type": row["planner_type"],
                "request": json.loads(row["request_json"]),
                "result": json.loads(row["result_json"]),
                "created_at": row["created_at"],
            }
        )
    return output


def get_recommendation(user_id: int, recommendation_id: int) -> dict[str, Any] | None:
    with connection() as conn:
        row = conn.execute(
            """
            SELECT id, planner_type, request_json, result_json, created_at
            FROM recommendations
            WHERE id = ? AND user_id = ?
            """,
            (recommendation_id, user_id),
        ).fetchone()

    if not row:
        return None

    return {
        "id": row["id"],
        "planner_type": row["planner_type"],
        "request": json.loads(row["request_json"]),
        "result": json.loads(row["result_json"]),
        "created_at": row["created_at"],
    }
