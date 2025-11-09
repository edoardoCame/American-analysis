"""Utilities for the performance-based vs traditional contracting analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.regression.linear_model import RegressionResultsWrapper
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .usaspending_utils import DEFAULT_DB_PATH, prepare_cost_dataset


# Columns required in addition to prepare_cost_dataset defaults
PERFORMANCE_EXTRA_FIELDS: tuple[str, ...] = (
    "contract_award_unique_key",
    "contract_transaction_unique_key",
    "award_id_piid",
    "awarding_agency_code",
    "awarding_agency_name",
    "action_date",
    "performance_based_service_acquisition",
    "performance_based_service_acquisition_code",
    "modification_number",
)


@dataclass(frozen=True)
class MatchingResult:
    """Container for propensity score matching outputs."""

    att: float
    treated_mean: float
    control_mean: float
    coverage_ratio: float
    matches: pd.DataFrame


def prepare_performance_outcomes_dataset(
    *,
    db_path: str | None = None,
    additional_where: str | None = None,
    drop_not_applicable: bool = True,
) -> pd.DataFrame:
    """Return a cleaned, one-row-per-award dataset with derived metrics."""

    dataset = prepare_cost_dataset(
        db_path=db_path or DEFAULT_DB_PATH,
        additional_where=additional_where,
        additional_fields=PERFORMANCE_EXTRA_FIELDS,
    )

    df = dataset.copy()
    df["action_date"] = pd.to_datetime(df["action_date"], errors="coerce")
    df["modification_number"] = pd.to_numeric(df["modification_number"], errors="coerce")

    df["is_performance_based"] = df["performance_based_service_acquisition_code"].map({
        "Y": True,
        "N": False,
    })
    if drop_not_applicable:
        df = df.dropna(subset=["is_performance_based"])
    else:
        df["is_performance_based"] = df["is_performance_based"].fillna(False)

    df = df.dropna(subset=["award_id_piid", "awarding_agency_code"])
    df["award_key"] = (
        df["awarding_agency_code"].astype(str).str.strip() +
        "::" +
        df["award_id_piid"].astype(str).str.strip()
    )

    # Keep the latest available action per award (highest mod number and newest date)
    df = df.sort_values(
        ["award_key", "modification_number", "action_date"],
        ascending=[True, True, True],
    )
    latest_idx = df.groupby("award_key").tail(1).index
    latest = df.loc[latest_idx].copy()

    # Attach total modification count per award to capture contract volatility
    mod_counts = (
        df.groupby("award_key")["modification_number"]
        .max()
        .rename("max_modification_number")
        .reset_index()
    )
    action_counts = (
        df.groupby("award_key")["contract_transaction_unique_key"]
        .nunique()
        .rename("action_records")
        .reset_index()
    )
    latest = latest.merge(mod_counts, on="award_key", how="left")
    latest = latest.merge(action_counts, on="award_key", how="left")

    latest["max_modification_number"] = latest["max_modification_number"].fillna(0)
    latest["action_records"] = latest["action_records"].fillna(1)

    latest["duration_years"] = latest["performance_years"].where(
        latest["performance_years"].notna() & (latest["performance_years"] > 0)
    )
    latest["number_of_offers_received"] = pd.to_numeric(
        latest["number_of_offers_received"], errors="coerce"
    )

    latest["log_current_value"] = np.log1p(
        latest["current_total_value_of_award"].clip(lower=0)
    )
    latest["log_base_all_options_value"] = np.log1p(
        latest["base_and_all_options_value"].clip(lower=0)
    )

    latest["type_of_contract_pricing"] = latest[
        "type_of_contract_pricing"
    ].fillna("UNKNOWN")
    latest["extent_competed"] = latest["extent_competed"].fillna("UNKNOWN")
    latest["awarding_agency_name"] = latest["awarding_agency_name"].fillna(
        "Unknown agency"
    )
    latest["is_performance_based"] = latest["is_performance_based"].astype(bool)

    return latest.reset_index(drop=True)


def summarize_core_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute headline statistics split by the performance-based flag."""

    work = df.copy()

    def q25(series: pd.Series) -> float:
        return series.quantile(0.25)

    def q75(series: pd.Series) -> float:
        return series.quantile(0.75)

    summary = (
        work.groupby("is_performance_based")
        .agg(
            awards=("award_key", "size"),
            median_current_value=("current_total_value_of_award", "median"),
            value_p25=("current_total_value_of_award", q25),
            value_p75=("current_total_value_of_award", q75),
            median_duration_years=("duration_years", "median"),
            duration_p25=("duration_years", q25),
            duration_p75=("duration_years", q75),
            mean_modifications=("max_modification_number", "mean"),
            median_offers=("number_of_offers_received", "median"),
        )
    )
    summary["award_share"] = summary["awards"] / summary["awards"].sum()
    return summary.reset_index()


def compute_agency_performance_share(
    df: pd.DataFrame,
    *,
    min_awards: int = 100,
    top_n: int = 12,
) -> pd.DataFrame:
    """Return agencies with the highest performance-based adoption."""

    aggregated = (
        df.groupby("awarding_agency_name")
        .agg(
            total_awards=("award_key", "size"),
            performance_awards=("is_performance_based", "sum"),
        )
        .reset_index()
    )
    eligible = aggregated[aggregated["total_awards"] >= min_awards].copy()
    eligible["performance_share"] = (
        eligible["performance_awards"] / eligible["total_awards"]
    )
    return (
        eligible.sort_values(["performance_share", "total_awards"], ascending=[False, False])
        .head(top_n)
        .reset_index(drop=True)
    )


def compute_pricing_mix(df: pd.DataFrame) -> pd.DataFrame:
    """Return award counts by pricing type and performance flag."""

    grouped = (
        df.groupby(["type_of_contract_pricing", "is_performance_based"])
        .size()
        .reset_index(name="award_count")
    )
    totals = grouped.groupby("type_of_contract_pricing")["award_count"].transform("sum")
    grouped["share_within_pricing"] = grouped["award_count"] / totals
    return grouped.sort_values("award_count", ascending=False).reset_index(drop=True)


def compute_cohens_d(df: pd.DataFrame, column: str) -> float:
    """Return Cohen's d between performance groups for the selected column."""

    treated = df.loc[df["is_performance_based"], column].dropna()
    control = df.loc[~df["is_performance_based"], column].dropna()
    if len(treated) < 2 or len(control) < 2:
        return float("nan")

    mean_diff = treated.mean() - control.mean()
    pooled_var = (
        ((len(treated) - 1) * treated.var(ddof=1)) +
        ((len(control) - 1) * control.var(ddof=1))
    ) / (len(treated) + len(control) - 2)
    pooled_std = np.sqrt(pooled_var)
    if pooled_std == 0:
        return float("nan")
    return mean_diff / pooled_std


def run_value_regression(
    df: pd.DataFrame,
    *,
    response: str = "log_current_value",
) -> RegressionResultsWrapper:
    """Run an OLS model with interaction terms requested in the analysis brief."""

    required_cols = [
        response,
        "is_performance_based",
        "log_base_all_options_value",
        "duration_years",
        "number_of_offers_received",
        "type_of_contract_pricing",
        "extent_competed",
        "awarding_agency_code",
    ]
    working = df.dropna(subset=required_cols).copy()

    formula = (
        f"{response} ~ is_performance_based"
        " + log_base_all_options_value"
        " + duration_years"
        " + number_of_offers_received"
        " + C(type_of_contract_pricing)"
        " + C(extent_competed)"
        " + C(awarding_agency_code)"
        " + is_performance_based:C(type_of_contract_pricing)"
        " + is_performance_based:C(extent_competed)"
    )

    model = smf.ols(formula=formula, data=working).fit(cov_type="HC3")
    return model


def propensity_score_match(
    df: pd.DataFrame,
    *,
    outcome_col: str = "current_total_value_of_award",
    n_neighbors: int = 5,
    max_iter: int = 500,
) -> MatchingResult:
    """Perform one-to-one nearest propensity score matching."""

    features: Sequence[str] = (
        "awarding_agency_code",
        "type_of_contract_pricing",
        "log_base_all_options_value",
    )

    feature_list = list(features)
    required = ["is_performance_based", outcome_col, *feature_list]
    working = df.dropna(subset=required).copy()

    categorical = ["awarding_agency_code", "type_of_contract_pricing"]
    numeric = ["log_base_all_options_value"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
            ("num", Pipeline([("scaler", StandardScaler())]), numeric),
        ]
    )

    log_reg = LogisticRegression(
        max_iter=max_iter,
        class_weight="balanced",
        solver="lbfgs",
    )

    pipeline = Pipeline(
        steps=[
            ("prep", preprocessor),
            ("clf", log_reg),
        ]
    )

    pipeline.fit(working[feature_list], working["is_performance_based"])
    working["propensity_score"] = pipeline.predict_proba(working[feature_list])[:, 1]

    treated = working[working["is_performance_based"]].copy()
    control = working[~working["is_performance_based"]].copy()

    if treated.empty or control.empty:
        return MatchingResult(float("nan"), float("nan"), float("nan"), 0.0, pd.DataFrame())

    treated_scores = treated["propensity_score"].to_numpy().reshape(-1, 1)
    control_scores = control["propensity_score"].to_numpy().reshape(-1, 1)

    k = min(n_neighbors, len(control))
    neighbor_model = NearestNeighbors(n_neighbors=k)
    neighbor_model.fit(control_scores)
    distances, indices = neighbor_model.kneighbors(treated_scores)

    control_available = np.ones(len(control), dtype=bool)
    pairs: list[tuple[int, int]] = []

    for treated_idx, neighbor_idxs in enumerate(indices):
        match_idx = None
        for candidate in neighbor_idxs:
            if control_available[candidate]:
                match_idx = candidate
                break
        if match_idx is None:
            continue
        control_available[match_idx] = False
        pairs.append((treated_idx, match_idx))

    if not pairs:
        return MatchingResult(float("nan"), float("nan"), float("nan"), 0.0, pd.DataFrame())

    treated_indices = [treated.index[i] for i, _ in pairs]
    control_indices = [control.index[j] for _, j in pairs]

    matched_df = pd.DataFrame(
        {
            "treated_index": treated_indices,
            "control_index": control_indices,
            "treated_outcome": working.loc[treated_indices, outcome_col].to_numpy(),
            "control_outcome": working.loc[control_indices, outcome_col].to_numpy(),
            "treated_propensity": working.loc[treated_indices, "propensity_score"].to_numpy(),
            "control_propensity": working.loc[control_indices, "propensity_score"].to_numpy(),
        }
    )
    matched_df["difference"] = matched_df["treated_outcome"] - matched_df["control_outcome"]
    matched_df["propensity_gap"] = matched_df["treated_propensity"] - matched_df["control_propensity"]

    att = matched_df["difference"].mean()
    treated_mean = matched_df["treated_outcome"].mean()
    control_mean = matched_df["control_outcome"].mean()
    coverage = len(matched_df) / len(treated)

    return MatchingResult(att, treated_mean, control_mean, coverage, matched_df)


__all__ = [
    "MatchingResult",
    "compute_agency_performance_share",
    "compute_cohens_d",
    "compute_pricing_mix",
    "prepare_performance_outcomes_dataset",
    "propensity_score_match",
    "run_value_regression",
    "summarize_core_metrics",
]
