"""Utility helpers for the competition intensity analysis notebook."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, List, Sequence

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder


# Columns needed for the competition intensity workflow.
DEFAULT_USECOLS: List[str] = [
    "action_date",
    "awarding_agency_name",
    "awarding_sub_agency_name",
    "awarding_office_name",
    "extent_competed",
    "type_of_set_aside",
    "solicitation_procedures",
    "type_of_contract_pricing",
    "product_or_service_code",
    "product_or_service_code_description",
    "primary_place_of_performance_state_code",
    "number_of_offers_received",
    "base_and_all_options_value",
    "total_dollars_obligated",
    "naics_code",
    "naics_description",
]

RESTRICTED_SOLICITATION_LABELS = {
    "ONLY ONE SOURCE",
    "ALTERNATIVE SOURCES",
    "SUBJECT TO MULTIPLE AWARD FAIR OPPORTUNITY",
}

NON_OPEN_EXTENT_LABELS = {
    "NOT COMPETED",
    "NOT COMPETED UNDER SAP",
    "NOT AVAILABLE FOR COMPETITION",
    "FOLLOW ON TO COMPETED ACTION",
    "NON-COMPETITIVE DELIVERY ORDER",
}

EXCLUSIONARY_EXTENT_LABELS = {
    "FULL AND OPEN COMPETITION AFTER EXCLUSION OF SOURCES",
}


def load_security_transactions(
    csv_path: Path | str,
    *,
    naics_code: str = "561612",
    usecols: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Load contracts filtered to the security-services NAICS code."""

    path = Path(csv_path)
    cols = list(usecols) if usecols else DEFAULT_USECOLS
    df = pd.read_csv(
        path,
        usecols=cols,
        parse_dates=["action_date"],
        dtype={"naics_code": "string"},
        low_memory=False,
    )
    mask = df["naics_code"].astype("string").str.startswith(str(naics_code))
    df = df.loc[mask].copy()
    return df


def load_security_transactions_from_sqlite(
    db_path: Path | str,
    table_name: str,
    *,
    naics_code: str = "561612",
    usecols: Sequence[str] | None = None,
    limit: int | None = None,
) -> pd.DataFrame:
    """Load contracts filtered to the NAICS code directly from SQLite."""

    columns = list(usecols) if usecols else DEFAULT_USECOLS
    quoted_cols = ", ".join(f'"{col}"' for col in columns)
    filter_param = f"{naics_code}%"

    query = [
        f"SELECT {quoted_cols}",
        f"FROM \"{table_name}\"",
        "WHERE \"naics_code\" LIKE ?",
    ]
    if limit is not None and limit > 0:
        query.append(f"LIMIT {int(limit)}")

    sql = "\n".join(query)

    with sqlite3.connect(str(db_path)) as conn:
        df = pd.read_sql_query(sql, conn, params=(filter_param,))

    if "action_date" in df.columns:
        df["action_date"] = pd.to_datetime(df["action_date"], errors="coerce")

    return df


def prepare_competition_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Clean fields and derive helper flags for modeling and segmentation."""

    prepared = df.copy()
    prepared["number_of_offers_received"] = pd.to_numeric(
        prepared["number_of_offers_received"], errors="coerce"
    )
    prepared = prepared.dropna(subset=["number_of_offers_received"])

    for value_col in ("base_and_all_options_value", "total_dollars_obligated"):
        prepared[value_col] = (
            pd.to_numeric(prepared[value_col], errors="coerce").fillna(0.0)
        )

    prepared["log_base_and_all_options_value"] = np.log10(
        prepared["base_and_all_options_value"].clip(lower=0) + 1
    )

    cat_cols = [
        "awarding_agency_name",
        "awarding_sub_agency_name",
        "awarding_office_name",
        "extent_competed",
        "type_of_set_aside",
        "solicitation_procedures",
        "type_of_contract_pricing",
        "product_or_service_code",
        "primary_place_of_performance_state_code",
    ]

    for col in cat_cols:
        prepared[col] = prepared[col].fillna("missing").astype("string")

    return prepared


def _normalize_competition_label(value: str) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def classify_solicitation_scope(value: str) -> str:
    """Label solicitation procedures as open or restricted."""

    normalized = _normalize_competition_label(value)
    if not normalized:
        return "Unknown"
    if normalized in RESTRICTED_SOLICITATION_LABELS:
        return "Restricted/limited"
    return "Open/general"


def classify_extent_scope(value: str) -> str:
    """Label extent competed outcomes to flag non-open pathways."""

    normalized = _normalize_competition_label(value)
    if not normalized:
        return "Unknown"
    if normalized in NON_OPEN_EXTENT_LABELS:
        return "Non-competed"
    if normalized in EXCLUSIONARY_EXTENT_LABELS:
        return "Open w/ exclusions"
    return "Open/general"


def filter_open_competitions(
    df: pd.DataFrame,
    *,
    solicitation_col: str = "solicitation_procedures",
    extent_col: str = "extent_competed",
) -> pd.DataFrame:
    """Keep only contracts that are open both by solicitation and extent competed."""

    solicitation_scope = df[solicitation_col].map(classify_solicitation_scope)
    extent_scope = df[extent_col].map(classify_extent_scope)
    mask = solicitation_scope.eq("Open/general") & extent_scope.eq("Open/general")
    return df.loc[mask].copy()


def build_regression_pipeline(
    categorical_cols: Sequence[str], numeric_cols: Sequence[str]
) -> Pipeline:
    """Create the regressor pipeline for offer-count prediction."""

    categorical = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            (
                "encoder",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                    dtype=np.float32,
                ),
            ),
        ]
    )

    numeric = Pipeline(steps=[("imputer", SimpleImputer(strategy="median"))])

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", categorical, list(categorical_cols)),
            ("numeric", numeric, list(numeric_cols)),
        ]
    )

    model = HistGradientBoostingRegressor(
        max_depth=8,
        learning_rate=0.08,
        min_samples_leaf=35,
        l2_regularization=0.2,
        random_state=42,
    )

    return Pipeline(steps=[("preprocess", preprocessor), ("model", model)])


def build_low_competition_classifier(
    categorical_cols: Sequence[str], numeric_cols: Sequence[str]
) -> Pipeline:
    """Classifier for identifying low-competition opportunities."""

    categorical = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            (
                "encoder",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                    dtype=np.float32,
                ),
            ),
        ]
    )

    numeric = Pipeline(steps=[("imputer", SimpleImputer(strategy="median"))])

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", categorical, list(categorical_cols)),
            ("numeric", numeric, list(numeric_cols)),
        ]
    )

    model = HistGradientBoostingClassifier(
        max_depth=6,
        learning_rate=0.1,
        min_samples_leaf=30,
        l2_regularization=0.1,
        class_weight="balanced",
        random_state=42,
    )

    return Pipeline(steps=[("preprocess", preprocessor), ("model", model)])


def summarize_low_competition_niches(
    df: pd.DataFrame,
    *,
    group_cols: Iterable[str],
    low_threshold: int = 3,
    high_value_quantile: float = 0.8,
    min_awards: int = 10,
) -> pd.DataFrame:
    """Aggregate contracts to highlight valuable, low-competition niches."""

    working = df.copy()
    working["is_low_competition"] = (
        working["number_of_offers_received"] <= low_threshold
    )

    value_cut = working["base_and_all_options_value"].quantile(high_value_quantile)
    working["is_high_value"] = working["base_and_all_options_value"] >= value_cut
    working["is_low_comp_high_value"] = (
        working["is_low_competition"] & working["is_high_value"]
    )

    grouped = (
        working.groupby(list(group_cols))
        .agg(
            awards=("number_of_offers_received", "size"),
            avg_offers=("number_of_offers_received", "mean"),
            low_comp_share=("is_low_competition", "mean"),
            high_value_share=("is_high_value", "mean"),
            hv_low_comp_count=("is_low_comp_high_value", "sum"),
            hv_low_comp_share=("is_low_comp_high_value", "mean"),
            median_value=("base_and_all_options_value", "median"),
            p90_value=("base_and_all_options_value", lambda s: s.quantile(0.9)),
        )
        .reset_index()
    )

    grouped = grouped[grouped["awards"] >= min_awards]
    grouped = grouped[grouped["hv_low_comp_count"] > 0]

    grouped["niche_score"] = (
        grouped["hv_low_comp_share"] * grouped["median_value"]
    )

    grouped = grouped.sort_values(
        by=["niche_score", "hv_low_comp_share"], ascending=False
    ).reset_index(drop=True)

    grouped.attrs["high_value_cutoff"] = value_cut
    grouped.attrs["low_threshold"] = low_threshold
    return grouped
