# src/loader.py
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, Optional


@dataclass(frozen=True)
class SCDRecord:
    # IDs (useful for DB keys / joins / deduping)
    measure_id: Optional[int]
    location_id: Optional[int]
    sex_id: Optional[int]
    age_group_id: Optional[int]
    cause_id: Optional[int]
    metric_id: Optional[int]

    # Names (useful for CLI display)
    measure: str
    location: str
    sex: str
    age_group: str
    cause: str
    metric: str

    year: int
    value: Optional[float]
    upper: Optional[float]
    lower: Optional[float]


DEFAULT_COLUMN_ALIASES: Dict[str, list[str]] = {
    "measure_id": ["measure_id"],
    "measure": ["measure_name", "measure"],
    "location_id": ["location_id"],
    "location": ["location_name", "location"],
    "sex_id": ["sex_id"],
    "sex": ["sex_name", "sex"],
    "age_group_id": ["age_group_id"],
    "age_group": ["age_group_name", "age_name", "age"],
    "cause_id": ["cause_id"],
    "cause": ["cause_name", "cause"],
    "metric_id": ["metric_id"],
    "metric": ["metric_name", "metric"],
    "year": ["year_id", "year"],
    "value": ["val", "value"],
    "upper": ["upper", "upper_val", "upper_value"],
    "lower": ["lower", "lower_val", "lower_value"],
}


def preview_header(csv_path: str | Path) -> list[str]:
    csv_path = Path(csv_path)
    with csv_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        return next(reader)


def _find_column(header_map: Dict[str, str], aliases: list[str]) -> Optional[str]:
    for a in aliases:
        key = a.strip().lower()
        if key in header_map:
            return header_map[key]
    return None


def _to_int(x: str) -> Optional[int]:
    x = (x or "").strip()
    if x == "" or x.upper() == "NA":
        return None
    try:
        return int(float(x))
    except ValueError:
        return None


def _to_float(x: str) -> Optional[float]:
    x = (x or "").strip()
    if x == "" or x.upper() == "NA":
        return None
    try:
        return float(x)
    except ValueError:
        return None


def iter_records(
    csv_path: str | Path,
    column_aliases: Dict[str, list[str]] = DEFAULT_COLUMN_ALIASES,
) -> Iterator[SCDRecord]:
    """
    Stream records from the IHME sickle cell disorders estimates CSV.

    This is memory-safe for large files: it yields one record at a time.
    """
    csv_path = Path(csv_path)

    with csv_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row (fieldnames missing).")

        header_map = {h.strip().lower(): h for h in reader.fieldnames}

        resolved: Dict[str, str] = {}
        missing_required = []

        # Required for your analysis/CLI
        required_fields = {"measure", "location", "sex", "age_group", "cause", "metric", "year", "value"}

        for field, aliases in column_aliases.items():
            col = _find_column(header_map, aliases)
            if col is not None:
                resolved[field] = col
            elif field in required_fields:
                missing_required.append((field, aliases))

        if missing_required:
            problems = "\n".join(
                f"- Could not find '{field}' using aliases: {aliases}"
                for field, aliases in missing_required
            )
            found = ", ".join(reader.fieldnames)
            raise ValueError(
                "Could not map required columns from CSV.\n"
                f"{problems}\n\nColumns found:\n{found}"
            )

        for row in reader:
            # IDs (optional)
            measure_id = _to_int(row.get(resolved.get("measure_id", ""), ""))
            location_id = _to_int(row.get(resolved.get("location_id", ""), ""))
            sex_id = _to_int(row.get(resolved.get("sex_id", ""), ""))
            age_group_id = _to_int(row.get(resolved.get("age_group_id", ""), ""))
            cause_id = _to_int(row.get(resolved.get("cause_id", ""), ""))
            metric_id = _to_int(row.get(resolved.get("metric_id", ""), ""))

            # Names (required)
            measure = (row.get(resolved["measure"], "") or "").strip()
            location = (row.get(resolved["location"], "") or "").strip()
            sex = (row.get(resolved["sex"], "") or "").strip()
            age_group = (row.get(resolved["age_group"], "") or "").strip()
            cause = (row.get(resolved["cause"], "") or "").strip()
            metric = (row.get(resolved["metric"], "") or "").strip()

            year = _to_int(row.get(resolved["year"], ""))
            if year is None:
                continue

            value = _to_float(row.get(resolved["value"], ""))
            upper = _to_float(row.get(resolved.get("upper", ""), "")) if "upper" in resolved else None
            lower = _to_float(row.get(resolved.get("lower", ""), "")) if "lower" in resolved else None

            # Minimal sanity check
            if not location or not measure or not metric or not cause:
                continue

            yield SCDRecord(
                measure_id=measure_id,
                location_id=location_id,
                sex_id=sex_id,
                age_group_id=age_group_id,
                cause_id=cause_id,
                metric_id=metric_id,
                measure=measure,
                location=location,
                sex=sex,
                age_group=age_group,
                cause=cause,
                metric=metric,
                year=year,
                value=value,
                upper=upper,
                lower=lower,
            )


def load_records(csv_path: str | Path, limit: Optional[int] = None) -> list[SCDRecord]:
    out: list[SCDRecord] = []
    for rec in iter_records(csv_path):
        out.append(rec)
        if limit is not None and len(out) >= limit:
            break
    return out
