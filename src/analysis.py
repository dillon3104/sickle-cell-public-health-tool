# src/analysis.py
from __future__ import annotations

import sqlite3
from typing import Optional


def get_distinct_values(conn: sqlite3.Connection, column: str) -> list[str]:
    """
    Safely return DISTINCT values for a whitelisted column.
    """
    allowed = {"location", "measure", "metric", "sex", "age_group", "cause", "year"}
    if column not in allowed:
        raise ValueError(f"Column not allowed: {column}")

    if column == "year":
        rows = conn.execute("SELECT DISTINCT year FROM scd_estimates ORDER BY year;").fetchall()
        return [str(r[0]) for r in rows]

    rows = conn.execute(f"SELECT DISTINCT {column} FROM scd_estimates ORDER BY {column};").fetchall()
    return [r[0] for r in rows]


def get_trend(
    conn: sqlite3.Connection,
    location: str,
    measure: str,
    metric: str,
    sex: str = "Both",
    age_group: str = "All Ages",
    cause: Optional[str] = None,
) -> list[tuple[int, float]]:
    """
    Returns a time series: [(year, value), ...] for the selected filters.
    Rows with NULL value are excluded.
    """
    sql = """
        SELECT year, value
        FROM scd_estimates
        WHERE location = ?
          AND measure = ?
          AND metric = ?
          AND sex = ?
          AND age_group = ?
          AND value IS NOT NULL
    """
    params: list = [location, measure, metric, sex, age_group]

    if cause:
        sql += " AND cause = ?"
        params.append(cause)

    sql += " ORDER BY year;"

    rows = conn.execute(sql, params).fetchall()
    return [(int(y), float(v)) for (y, v) in rows]


def summary_stats(
    conn: sqlite3.Connection,
    measure: str,
    metric: str,
    year: Optional[int] = None,
    sex: str = "Both",
    age_group: str = "All Ages",
    cause: Optional[str] = None,
) -> dict:
    """
    Summary across locations for a given measure/metric (+ optional year).
    Returns count/min/mean/max.
    """
    sql = """
        SELECT
            COUNT(value) AS n,
            MIN(value) AS min_value,
            AVG(value) AS mean_value,
            MAX(value) AS max_value
        FROM scd_estimates
        WHERE measure = ?
          AND metric = ?
          AND sex = ?
          AND age_group = ?
          AND value IS NOT NULL
    """
    params: list = [measure, metric, sex, age_group]

    if year is not None:
        sql += " AND year = ?"
        params.append(year)

    if cause:
        sql += " AND cause = ?"
        params.append(cause)

    row = conn.execute(sql, params).fetchone()
    n, min_v, mean_v, max_v = row

    return {
        "n": int(n or 0),
        "min": float(min_v) if min_v is not None else None,
        "mean": float(mean_v) if mean_v is not None else None,
        "max": float(max_v) if max_v is not None else None,
        "filters": {
            "measure": measure,
            "metric": metric,
            "year": year,
            "sex": sex,
            "age_group": age_group,
            "cause": cause,
        },
    }


def compare_locations(
    conn: sqlite3.Connection,
    measure: str,
    metric: str,
    year: int,
    sex: str = "Both",
    age_group: str = "All Ages",
    cause: Optional[str] = None,
    top_n: int = 10,
    order: str = "desc",
) -> list[tuple[str, float]]:
    """
    Compare locations for a given year.
    Returns list of (location, value), sorted.
    """
    if order not in {"asc", "desc"}:
        raise ValueError("order must be 'asc' or 'desc'")

    sql = f"""
        SELECT location, value
        FROM scd_estimates
        WHERE measure = ?
          AND metric = ?
          AND year = ?
          AND sex = ?
          AND age_group = ?
          AND value IS NOT NULL
    """
    params: list = [measure, metric, year, sex, age_group]

    if cause:
        sql += " AND cause = ?"
        params.append(cause)

    sql += f" ORDER BY value {order.upper()} LIMIT ?;"
    params.append(top_n)

    rows = conn.execute(sql, params).fetchall()
    return [(loc, float(val)) for (loc, val) in rows]
