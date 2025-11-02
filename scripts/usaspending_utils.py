"""Utility helpers for analyzing USAspending prime transactions without heuristics.

The functions below retrieve data directly from the filtered SQLite database and
provide reusable aggregations centred on solicitation procedure labels.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Optional, Sequence

import pandas as pd

# Project-level paths
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = REPO_ROOT / "db" / "prime_transactions_filtered.sqlite"
NAICS_FILE = REPO_ROOT / "NAICs.md"


def load_naics_codes(source: Path | str = NAICS_FILE) -> tuple[str, ...]:
    """Read six-digit NAICS codes from the project documentation."""
    path = Path(source).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"NAICS definition file not found at {path}")

    text = path.read_text(encoding="utf-8")
    codes = [fragment for fragment in text.split() if fragment.isdigit() and len(fragment) == 6]
    if not codes:
        preview = text[:120].replace("\n", " ")
        raise ValueError(
            f"No six-digit NAICS codes detected in {path}. Content preview: {preview!r}"
        )
    # Preserve original order, remove duplicates
    seen: set[str] = set()
    ordered_codes: list[str] = []
    for code in codes:
        if code not in seen:
            seen.add(code)
            ordered_codes.append(code)
    return tuple(ordered_codes)


DEFAULT_SECURITY_NAICS = load_naics_codes()


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
    """Load selected columns from the filtered prime transactions table."""
    if not columns:
        raise ValueError("At least one column must be requested.")

    with get_connection(db_path) as conn:
        table_name = get_prime_transactions_table_name(conn)
        column_sql = ", ".join(dict.fromkeys(columns))

        where_clauses: list[str] = []
        params: list[str] = []

        if naics_filter:
            naics_codes = [str(code) for code in naics_filter]
            placeholders = ",".join("?" for _ in naics_codes)
            where_clauses.append(f"naics_code IN ({placeholders})")
            params.extend(naics_codes)

        if additional_where:
            where_clauses.append(f"({additional_where})")

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        query = f"SELECT {column_sql} FROM {table_name} {where_sql}"
        df = pd.read_sql_query(query, conn, params=params)

    return df


def prepare_solicitation_dataset(
    *,
    value_fields: Sequence[str] = (
        "federal_action_obligation",
        "base_and_exercised_options_value",
        "base_and_all_options_value",
        "current_total_value_of_award",
        "potential_total_value_of_award",
        "total_outlayed_amount_for_overall_award",
    ),
    extra_fields: Sequence[str] = ("extent_competed", "number_of_offers_received"),
    db_path: Path | str = DEFAULT_DB_PATH,
) -> pd.DataFrame:
    """Return a DataFrame with the fields needed for solicitation analyses."""
    base_columns = ["action_date_fiscal_year", "solicitation_procedures"]
    columns = list(dict.fromkeys([*base_columns, *value_fields, *extra_fields]))
    df = fetch_prime_transactions(columns, db_path=db_path)

    numeric_fields = set(value_fields) | {"number_of_offers_received"}
    for field in numeric_fields:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors="coerce")

    df["action_date_fiscal_year"] = pd.to_numeric(
        df["action_date_fiscal_year"], errors="coerce"
    ).astype("Int64")

    return df


def compute_solicitation_timeseries(
    df: pd.DataFrame,
    *,
    value_field: str = "federal_action_obligation",
) -> pd.DataFrame:
    """Aggregate counts and dollar sums by fiscal year and solicitation procedure."""
    if value_field not in df.columns:
        raise KeyError(f"{value_field} is not present in the supplied DataFrame.")

    working = df.dropna(subset=["action_date_fiscal_year", "solicitation_procedures"]).copy()
    working[value_field] = pd.to_numeric(working[value_field], errors="coerce")

    aggregated = (
        working.groupby(["action_date_fiscal_year", "solicitation_procedures"])
        .agg(
            awards_total=("solicitation_procedures", "size"),
            obligation_total=(value_field, "sum"),
            median_offers=("number_of_offers_received", "median"),
        )
        .reset_index()
        .sort_values(["action_date_fiscal_year", "awards_total"], ascending=[True, False])
    )

    return aggregated


def pivot_solicitation_share(
    timeseries: pd.DataFrame,
) -> pd.DataFrame:
    """Return a wide-format table with share of awards and obligations per label."""
    totals = (
        timeseries.groupby("action_date_fiscal_year")
        .agg(
            total_awards=("awards_total", "sum"),
            total_obligation=("obligation_total", "sum"),
        )
        .reset_index()
    )

    merged = timeseries.merge(totals, on="action_date_fiscal_year", how="left")
    merged["share_awards"] = merged["awards_total"] / merged["total_awards"]
    merged["share_obligation"] = merged["obligation_total"] / merged["total_obligation"]

    share_table = merged.pivot_table(
        index="action_date_fiscal_year",
        columns="solicitation_procedures",
        values="share_awards",
        fill_value=0.0,
    ).sort_index()

    share_table.columns.name = "Share of awards"
    return share_table


def prepare_cost_dataset(
    *,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> pd.DataFrame:
    """Return fields required for value and duration analysis."""
    columns = [
        "solicitation_procedures",
        "federal_action_obligation",
        "base_and_exercised_options_value",
        "base_and_all_options_value",
        "current_total_value_of_award",
        "potential_total_value_of_award",
        "total_outlayed_amount_for_overall_award",
        "period_of_performance_start_date",
        "period_of_performance_current_end_date",
        "period_of_performance_potential_end_date",
    ]
    df = fetch_prime_transactions(columns, db_path=db_path)

    numeric_cols = [
        "federal_action_obligation",
        "base_and_exercised_options_value",
        "base_and_all_options_value",
        "current_total_value_of_award",
        "potential_total_value_of_award",
        "total_outlayed_amount_for_overall_award",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["period_of_performance_start_date"] = pd.to_datetime(
        df["period_of_performance_start_date"], errors="coerce"
    )
    current_end = pd.to_datetime(
        df["period_of_performance_current_end_date"], errors="coerce"
    )
    potential_end = pd.to_datetime(
        df["period_of_performance_potential_end_date"], errors="coerce"
    )
    df["period_of_performance_end_date"] = current_end.combine_first(potential_end)

    df["performance_years"] = (
        (
            df["period_of_performance_end_date"] - df["period_of_performance_start_date"]
        ).dt.days
        / 365.25
    )
    df.loc[df["performance_years"] <= 0, "performance_years"] = pd.NA

    for value_col, annualized_col in [
        ("base_and_exercised_options_value", "annualized_base_exercised"),
        ("base_and_all_options_value", "annualized_base_all"),
        ("current_total_value_of_award", "annualized_current_total"),
        ("potential_total_value_of_award", "annualized_potential_total"),
    ]:
        df[annualized_col] = df[value_col] / df["performance_years"]

    return df


def summarize_cost_by_procedure(
    df: pd.DataFrame,
    *,
    value_fields: Sequence[str] = (
        "federal_action_obligation",
        "base_and_exercised_options_value",
        "base_and_all_options_value",
        "current_total_value_of_award",
        "potential_total_value_of_award",
        "total_outlayed_amount_for_overall_award",
    ),
    annualized_fields: Sequence[str] = (
        "annualized_base_exercised",
        "annualized_base_all",
        "annualized_current_total",
        "annualized_potential_total",
    ),
) -> pd.DataFrame:
    """Compute descriptive statistics by solicitation procedure."""
    aggregations: dict[str, tuple[str, str]] = {
        "awards_total": ("solicitation_procedures", "size"),
    }

    def q25(series: pd.Series) -> float:
        return series.quantile(0.25)

    def q75(series: pd.Series) -> float:
        return series.quantile(0.75)

    for field in value_fields:
        aggregations[f"{field}_median"] = (field, "median")
        aggregations[f"{field}_iqr_low"] = (field, q25)
        aggregations[f"{field}_iqr_high"] = (field, q75)

    for field in annualized_fields:
        aggregations[f"{field}_median"] = (field, "median")
        aggregations[f"{field}_iqr_low"] = (field, q25)
        aggregations[f"{field}_iqr_high"] = (field, q75)

    grouped = (
        df.groupby("solicitation_procedures")
        .agg(**aggregations)
        .sort_values("awards_total", ascending=False)
    )

    return grouped


__all__ = [
    "compute_solicitation_timeseries",
    "fetch_prime_transactions",
    "load_naics_codes",
    "prepare_cost_dataset",
    "pivot_solicitation_share",
    "prepare_solicitation_dataset",
    "summarize_cost_by_procedure",
]
