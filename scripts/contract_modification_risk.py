"""Reusable helpers for the contract modification risk analysis notebooks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from sklearn.inspection import permutation_importance

from .usaspending_utils import (
    DEFAULT_DB_PATH,
    DEFAULT_SECURITY_NAICS,
    fetch_prime_transactions,
)


VALUE_COLUMNS: tuple[str, ...] = (
    "federal_action_obligation",
    "base_and_exercised_options_value",
    "base_and_all_options_value",
    "current_total_value_of_award",
    "potential_total_value_of_award",
)

DATE_COLUMNS: tuple[str, ...] = (
    "action_date",
    "period_of_performance_start_date",
    "period_of_performance_current_end_date",
)

CATEGORICAL_FEATURES: tuple[str, ...] = (
    "awarding_agency_name",
    "awarding_sub_agency_name",
    "awarding_office_name",
    "type_of_contract_pricing",
    "type_of_set_aside",
    "extent_competed",
    "solicitation_procedures",
    "type_of_idc",
    "multiple_or_single_award_idv",
    "performance_based_service_acquisition",
    "contract_bundling",
    "product_or_service_code",
    "action_type",
)

NUMERIC_FEATURES: tuple[str, ...] = (
    "federal_action_obligation",
    "base_and_exercised_options_value",
    "base_and_all_options_value",
    "current_total_value_of_award",
    "potential_total_value_of_award",
    "number_of_offers_received",
    "options_vs_base_delta",
    "current_vs_base_delta",
    "base_all_options_gap",
    "obligation_to_total_ratio",
    "planned_duration_days",
    "obligation_per_day",
)

TARGET_COLUMN = "has_modification"


def _safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _safe_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    result = numerator / denominator.replace({0: np.nan})
    return result.replace([np.inf, -np.inf], np.nan)


def _parse_dates(df: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def build_contract_modification_dataset(
    *,
    db_path: str | None = None,
    naics_filter: Optional[Iterable[str]] = DEFAULT_SECURITY_NAICS,
) -> pd.DataFrame:
    """Return base-award records enriched with a modification risk target."""

    columns = [
        "contract_transaction_unique_key",
        "contract_award_unique_key",
        "award_id_piid",
        "parent_award_id_piid",
        "modification_number",
        "naics_code",
        "naics_description",
        "awarding_agency_code",
        "awarding_agency_name",
        "awarding_sub_agency_code",
        "awarding_sub_agency_name",
        "awarding_office_code",
        "awarding_office_name",
        "action_type",
        "action_type_code",
        "extent_competed",
        "extent_competed_code",
        "solicitation_procedures",
        "solicitation_procedures_code",
        "type_of_contract_pricing",
        "type_of_contract_pricing_code",
        "type_of_set_aside",
        "type_of_set_aside_code",
        "type_of_idc",
        "type_of_idc_code",
        "multiple_or_single_award_idv",
        "multiple_or_single_award_idv_code",
        "performance_based_service_acquisition",
        "performance_based_service_acquisition_code",
        "contract_bundling",
        "contract_bundling_code",
        "product_or_service_code",
        "product_or_service_code_description",
        "number_of_offers_received",
        *VALUE_COLUMNS,
        *DATE_COLUMNS,
    ]

    df = fetch_prime_transactions(
        columns,
        db_path=db_path or DEFAULT_DB_PATH,
        naics_filter=naics_filter,
    )

    df["modification_number"] = df["modification_number"].fillna("0").astype(str)
    df["is_modification"] = df["modification_number"].str.upper() != "0"

    modification_presence = (
        df.groupby("contract_award_unique_key")["is_modification"].any().rename(TARGET_COLUMN)
    )

    base_awards = df.loc[~df["is_modification"].astype(bool)].copy()
    base_awards = base_awards.merge(
        modification_presence,
        left_on="contract_award_unique_key",
        right_index=True,
        how="left",
    )
    base_awards[TARGET_COLUMN] = base_awards[TARGET_COLUMN].fillna(False)

    for column in VALUE_COLUMNS:
        base_awards[column] = _safe_numeric(base_awards[column])

    base_awards["number_of_offers_received"] = _safe_numeric(
        base_awards["number_of_offers_received"]
    )

    base_awards["options_vs_base_delta"] = (
        base_awards["base_and_all_options_value"] - base_awards["base_and_exercised_options_value"]
    )
    base_awards["current_vs_base_delta"] = (
        base_awards["current_total_value_of_award"]
        - base_awards["base_and_exercised_options_value"]
    )
    base_awards["base_all_options_gap"] = (
        base_awards["potential_total_value_of_award"] - base_awards["base_and_all_options_value"]
    )
    base_awards["obligation_to_total_ratio"] = _safe_ratio(
        base_awards["federal_action_obligation"], base_awards["base_and_all_options_value"]
    )

    base_awards = _parse_dates(base_awards, DATE_COLUMNS)
    base_awards["planned_duration_days"] = (
        base_awards["period_of_performance_current_end_date"]
        - base_awards["period_of_performance_start_date"]
    ).dt.days
    base_awards["obligation_per_day"] = _safe_ratio(
        base_awards["federal_action_obligation"], base_awards["planned_duration_days"]
    )

    base_awards[TARGET_COLUMN] = base_awards[TARGET_COLUMN].astype(bool)

    return base_awards


@dataclass
class ModificationModelArtifacts:
    pipeline: Pipeline
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    y_pred_proba: np.ndarray
    metrics: dict[str, float]
    feature_importances: pd.DataFrame
    classification_report_text: str
    confusion_matrix: np.ndarray
    precision_recall_curve: tuple[np.ndarray, np.ndarray, np.ndarray]


def train_modification_risk_classifier(
    dataset: pd.DataFrame,
    *,
    numeric_features: Sequence[str] = NUMERIC_FEATURES,
    categorical_features: Sequence[str] = CATEGORICAL_FEATURES,
    target_column: str = TARGET_COLUMN,
    test_size: float = 0.2,
    random_state: int = 42,
) -> ModificationModelArtifacts:
    """Train a baseline classifier that predicts contract modification risk."""

    missing_numeric = [col for col in numeric_features if col not in dataset.columns]
    missing_categorical = [col for col in categorical_features if col not in dataset.columns]
    if missing_numeric or missing_categorical:
        raise KeyError(
            "Dataset is missing required columns: "
            f"numeric={missing_numeric}, categorical={missing_categorical}"
        )

    features = list(numeric_features) + list(categorical_features)
    data = dataset.dropna(subset=[target_column])[features + [target_column]].copy()

    X = data[features]
    y = data[target_column].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        stratify=y,
        random_state=random_state,
    )

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=np.nan,
                ),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    model = HistGradientBoostingClassifier(
        learning_rate=0.08,
        max_depth=8,
        min_samples_leaf=60,
        random_state=random_state,
        max_bins=255,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", model),
        ]
    )

    pipeline.fit(X_train, y_train)

    y_scores = pipeline.predict_proba(X_test)[:, 1]
    y_pred = (y_scores >= 0.5).astype(int)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_scores),
        "average_precision": average_precision_score(y_test, y_scores),
    }

    report_text = classification_report(y_test, y_pred, digits=3, zero_division=0)
    cmatrix = confusion_matrix(y_test, y_pred)
    pr_curve = precision_recall_curve(y_test, y_scores)

    feature_names = pipeline.named_steps["preprocess"].get_feature_names_out()
    perm = permutation_importance(
        pipeline,
        X_test,
        y_test,
        n_repeats=5,
        random_state=random_state,
        n_jobs=1,
    )
    feature_importances = (
        pd.DataFrame({"feature": feature_names, "importance": perm.importances_mean})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )

    return ModificationModelArtifacts(
        pipeline=pipeline,
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        y_pred_proba=y_scores,
        metrics=metrics,
        feature_importances=feature_importances,
        classification_report_text=report_text,
        confusion_matrix=cmatrix,
        precision_recall_curve=pr_curve,
    )
