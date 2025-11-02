"""Utility helpers for analyzing USAspending prime transactions data.

This module centralizes data access and derived indicators so that notebooks
can focus on storytelling and visualization.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Iterable, Optional, Sequence

import pandas as pd

# Resolve project-level paths relative to repository root.
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = REPO_ROOT / "db" / "prime_transactions_filtered.sqlite"
NAICS_FILE = REPO_ROOT / "NAICs.md"

# Keywords that hint how quality was evaluated.
QUALITY_SOLICITATION_KEYWORDS = {
    "negotiated",
    "best value",
    "tradeoff",
    "comparative evaluation",
    "multi-step",
    "part 15",
}

PRICE_DRIVEN_SOLICITATION_KEYWORDS = {
    "sealed bid",
    "lowest price",
    "lpta",
    "simplified acquisition",
    "sap",
    "commercial item procedures",
}

# Pricing structures that typically include quality or performance incentives.
QUALITY_PRICING_KEYWORDS = {
    "award fee",
    "incentive",
    "cost plus",
    "cost-reimbursement",
    "labor-hour",
    "time-and-material",
    "performance-based",
    "indefinite delivery with incentive",
}

# Competition labels suggesting qualitative or capability-driven awards.
LIMITED_COMPETITION_KEYWORDS = {
    "not competed",
    "limited sources",
    "only one source",
    "urgent",
    "follow-on",
    "authorized by law",
    "competed under sap - non-competitive",
    "not available for competition",
    "cse/limited",
}

# NAICS codes are sourced from NAICs.md so that analysts can update the list without
# touching the code.
def load_naics_codes(source: Path | str = NAICS_FILE) -> tuple[str, ...]:
    """Read six-digit NAICS codes from the project documentation."""
    path = Path(source).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"NAICS definition file not found at {path}")

    text = path.read_text(encoding="utf-8")
    raw_codes = re.findall(r"\b\d{6}\b", text)
    codes = tuple(dict.fromkeys(raw_codes))
    if not codes:
        preview = text[:120].replace("\n", " ")
        raise ValueError(
            f"No six-digit NAICS codes detected in {path}. "
            f"Content preview: {preview!r}"
        )
    return codes


DEFAULT_SECURITY_NAICS = load_naics_codes()

SOLICITATION_PATTERN = re.compile("|".join(re.escape(item) for item in QUALITY_SOLICITATION_KEYWORDS))
PRICE_SOLICITATION_PATTERN = re.compile("|".join(re.escape(item) for item in PRICE_DRIVEN_SOLICITATION_KEYWORDS))
PRICING_PATTERN = re.compile("|".join(re.escape(item) for item in QUALITY_PRICING_KEYWORDS))
COMPETITION_PATTERN = re.compile("|".join(re.escape(item) for item in LIMITED_COMPETITION_KEYWORDS))


def _dedupe_preserve_order(items: Sequence[str]) -> list[str]:
    """Return a list with duplicates removed while keeping the original order."""
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def get_connection(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Return a SQLite connection to the USAspending prime transactions database."""
    path = Path(db_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"SQLite database not found at {path}")
    return sqlite3.connect(path)


def get_prime_transactions_table_name(conn: sqlite3.Connection) -> str:
    """Detect the prime transactions table name within the filtered database."""
    query = """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name LIKE 'contracts_primetransactions%'
        ORDER BY name
        LIMIT 1
    """
    result = conn.execute(query).fetchone()
    if result is None:
        raise RuntimeError("Prime transactions table not found in the SQLite database.")
    return result[0]


def fetch_prime_transactions(
    columns: Sequence[str],
    *,
    db_path: Path | str = DEFAULT_DB_PATH,
    naics_filter: Optional[Iterable[str]] = DEFAULT_SECURITY_NAICS,
    additional_where: Optional[str] = None,
) -> pd.DataFrame:
    """Load selected columns from the filtered prime transactions table.

    Args:
        columns: Field names to retrieve from the dataset.
        db_path: Location of the SQLite database.
        naics_filter: Optional list of NAICS codes; pass None to avoid filtering.
        additional_where: Optional SQL snippet appended to the WHERE clause.
    """
    if not columns:
        raise ValueError("At least one column must be requested.")

    with get_connection(db_path) as conn:
        table_name = get_prime_transactions_table_name(conn)
        column_list = _dedupe_preserve_order(columns)
        column_sql = ", ".join(column_list)

        where_clauses: list[str] = []
        params: list[str] = []

        if naics_filter:
            placeholders = ",".join("?" for _ in naics_filter)
            where_clauses.append(f"naics_code IN ({placeholders})")
            params.extend([str(code) for code in naics_filter])

        if additional_where:
            where_clauses.append(f"({additional_where})")

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        query = f"SELECT {column_sql} FROM {table_name} {where_sql}"
        df = pd.read_sql_query(query, conn, params=params)

    return df


def _normalize_text(value: object) -> str:
    """Lowercase/strip helper to make string comparisons robust."""
    if isinstance(value, str):
        return value.strip().lower()
    return ""


def derive_quality_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add heuristic quality scoring components and a binary quality flag."""
    df = df.copy()

    df["solicitation_quality_hint"] = df["solicitation_procedures"].map(_normalize_text)
    df["pricing_quality_hint"] = df["type_of_contract_pricing"].map(_normalize_text)
    df["competition_hint"] = df["extent_competed"].map(_normalize_text)
    df["is_performance_based"] = df["performance_based_service_acquisition"].map(
        lambda x: _normalize_text(x) in {"y", "yes", "true", "1"}
    )

    df["quality_points"] = 0.0

    negotiated_mask = df["solicitation_quality_hint"].str.contains(SOLICITATION_PATTERN, na=False)
    price_driven_mask = df["solicitation_quality_hint"].str.contains(PRICE_SOLICITATION_PATTERN, na=False)

    df.loc[negotiated_mask, "quality_points"] += 2.0
    df.loc[price_driven_mask, "quality_points"] -= 1.0

    df.loc[df["is_performance_based"], "quality_points"] += 1.5

    df.loc[
        df["pricing_quality_hint"].str.contains(PRICING_PATTERN, na=False),
        "quality_points",
    ] += 1.0

    df.loc[
        df["competition_hint"].str.contains(COMPETITION_PATTERN, na=False),
        "quality_points",
    ] += 0.5

    df.loc[df["number_of_offers_received"].fillna(0).astype(float) <= 1, "quality_points"] += 0.5

    df["quality_flag"] = df["quality_points"] >= 1.5
    return df


def prepare_quality_dataset(
    *,
    value_fields: Sequence[str] = ("federal_action_obligation", "base_and_all_options_value"),
    db_path: Path | str = DEFAULT_DB_PATH,
) -> pd.DataFrame:
    """Return a DataFrame enriched with quality indicators for analysis."""
    base_columns = [
        "action_date_fiscal_year",
        "solicitation_procedures",
        "type_of_contract_pricing",
        "performance_based_service_acquisition",
        "extent_competed",
        "number_of_offers_received",
    ]
    columns = list({*base_columns, *value_fields})
    df = fetch_prime_transactions(columns, db_path=db_path)

    for field in value_fields:
        df[field] = pd.to_numeric(df[field], errors="coerce")

    df["number_of_offers_received"] = pd.to_numeric(
        df["number_of_offers_received"], errors="coerce"
    )

    df = derive_quality_indicators(df)
    return df


def compute_quality_trends(
    df: pd.DataFrame,
    *,
    value_field: str = "federal_action_obligation",
) -> pd.DataFrame:
    """Calculate yearly counts and dollar shares for quality-flagged awards."""
    if value_field not in df.columns:
        raise KeyError(f"{value_field} is not present in the supplied DataFrame.")

    working = df.copy()
    working["action_date_fiscal_year"] = pd.to_numeric(
        working["action_date_fiscal_year"], errors="coerce"
    )
    working = working.dropna(subset=["action_date_fiscal_year"])
    working["action_date_fiscal_year"] = working["action_date_fiscal_year"].astype(int)

    working[value_field] = pd.to_numeric(working[value_field], errors="coerce")
    working["value_quality_component"] = working[value_field].where(
        working["quality_flag"], other=0.0
    )

    aggregated = (
        working.groupby("action_date_fiscal_year")
        .agg(
            awards_total=("quality_flag", "size"),
            quality_awards=("quality_flag", "sum"),
            total_value=(value_field, "sum"),
            quality_value=("value_quality_component", "sum"),
        )
        .reset_index()
        .sort_values("action_date_fiscal_year")
    )

    aggregated["share_by_count"] = aggregated["quality_awards"] / aggregated["awards_total"]
    aggregated["share_by_value"] = aggregated["quality_value"] / aggregated["total_value"]
    aggregated = aggregated.fillna(0.0)
    return aggregated


__all__ = [
    "compute_quality_trends",
    "derive_quality_indicators",
    "fetch_prime_transactions",
    "get_connection",
    "load_naics_codes",
    "prepare_quality_dataset",
]
