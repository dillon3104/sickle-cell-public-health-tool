# src/db.py
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Optional

from src.loader import SCDRecord


DEFAULT_DB_PATH = Path("database/scd.db")


def connect(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Connect to SQLite DB (creates file if missing).
    Enables foreign keys + reasonable defaults.
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")  # better write performance
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """
    Create tables + indexes if they don't exist.
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scd_estimates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            measure_id INTEGER,
            location_id INTEGER,
            sex_id INTEGER,
            age_group_id INTEGER,
            cause_id INTEGER,
            metric_id INTEGER,

            measure TEXT NOT NULL,
            location TEXT NOT NULL,
            sex TEXT NOT NULL,
            age_group TEXT NOT NULL,
            cause TEXT NOT NULL,
            metric TEXT NOT NULL,

            year INTEGER NOT NULL,

            value REAL,
            upper REAL,
            lower REAL
        );
        """
    )

    # Helpful uniqueness constraint to prevent accidental duplicate loads.
    # (If your dataset contains multiple rows that truly collide on these fields,
    # you can remove/relax this later.)
    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_scd_estimates_key
        ON scd_estimates (measure, location, sex, age_group, cause, metric, year);
        """
    )

    # Indexes for fast filtering / grouping
    conn.execute("CREATE INDEX IF NOT EXISTS ix_scd_location ON scd_estimates (location);")
    conn.execute("CREATE INDEX IF NOT EXISTS ix_scd_year ON scd_estimates (year);")
    conn.execute("CREATE INDEX IF NOT EXISTS ix_scd_measure ON scd_estimates (measure);")
    conn.execute("CREATE INDEX IF NOT EXISTS ix_scd_metric ON scd_estimates (metric);")
    conn.execute("CREATE INDEX IF NOT EXISTS ix_scd_cause ON scd_estimates (cause);")

    conn.commit()


def clear_data(conn: sqlite3.Connection) -> None:
    """
    Remove all rows (useful for re-loading).
    """
    conn.execute("DELETE FROM scd_estimates;")
    conn.commit()


def insert_many(
    conn: sqlite3.Connection,
    records: Iterable[SCDRecord],
    batch_size: int = 5000,
) -> int:
    """
    Insert many records efficiently in batches.
    Uses INSERT OR IGNORE to avoid duplicates (based on unique index).
    Returns number of attempted inserts (not exact rows inserted).
    """
    sql = """
        INSERT OR IGNORE INTO scd_estimates (
            measure_id, location_id, sex_id, age_group_id, cause_id, metric_id,
            measure, location, sex, age_group, cause, metric,
            year, value, upper, lower
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    cur = conn.cursor()
    buffer = []
    attempted = 0

    for r in records:
        buffer.append(
            (
                r.measure_id, r.location_id, r.sex_id, r.age_group_id, r.cause_id, r.metric_id,
                r.measure, r.location, r.sex, r.age_group, r.cause, r.metric,
                r.year, r.value, r.upper, r.lower
            )
        )
        if len(buffer) >= batch_size:
            cur.executemany(sql, buffer)
            conn.commit()
            attempted += len(buffer)
            buffer.clear()

    if buffer:
        cur.executemany(sql, buffer)
        conn.commit()
        attempted += len(buffer)

    return attempted


# ---------- Simple query helpers (used by analysis/cli) ----------

def row_count(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM scd_estimates;").fetchone()[0]


def list_locations(conn: sqlite3.Connection, limit: Optional[int] = None) -> list[str]:
    q = "SELECT DISTINCT location FROM scd_estimates ORDER BY location"
    if limit:
        q += " LIMIT ?"
        rows = conn.execute(q, (limit,)).fetchall()
    else:
        rows = conn.execute(q).fetchall()
    return [r[0] for r in rows]


def list_measures(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT DISTINCT measure FROM scd_estimates ORDER BY measure;").fetchall()
    return [r[0] for r in rows]


def list_metrics(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT DISTINCT metric FROM scd_estimates ORDER BY metric;").fetchall()
    return [r[0] for r in rows]


def list_years(conn: sqlite3.Connection) -> list[int]:
    rows = conn.execute("SELECT DISTINCT year FROM scd_estimates ORDER BY year;").fetchall()
    return [int(r[0]) for r in rows]
