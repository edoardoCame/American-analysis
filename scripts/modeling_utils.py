"""Model training utilities for USAspending analyses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .usaspending_utils import DEFAULT_DB_PATH, list_prime_transaction_columns

# ---------------------------------------------------------------------------
# Feature selection helpers


DEFAULT_EXPLICIT_KEEP = {
    "solicitation_procedures",
    "solicitation_procedures_code",
    "extent_competed",
    "extent_competed_code",
    "type_of_contract_pricing",
    "type_of_contract_pricing_code",
    "type_of_set_aside",
    "type_of_set_aside_code",
    "evaluated_preference",
    "evaluated_preference_code",
    "contract_bundling",
    "contract_bundling_code",
    "fair_opportunity_limited_sources",
    "fair_opportunity_limited_sources_code",
    "commercial_item_acquisition_procedures",
    "commercial_item_acquisition_procedures_code",
    "commercial_item_test_program",
    "commercial_item_test_program_code",
    "simplified_procedures_for_certain_commercial_items",
    "simplified_procedures_for_certain_commercial_items_code",
    "undefinitized_action",
    "undefinitized_action_code",
    "performance_based_service_acquisition",
    "performance_based_service_acquisition_code",
    "type_of_idc",
    "type_of_idc_code",
    "multiple_or_single_award_idv",
    "multiple_or_single_award_idv_code",
    "award_or_idv_flag",
    "action_type",
    "action_type_code",
    "number_of_offers_received",
    "product_or_service_code",
    "product_or_service_code_description",
    "naics_code",
    "naics_description",
    "domestic_or_foreign_entity",
    "domestic_or_foreign_entity_code",
    "country_of_product_or_service_origin",
    "country_of_product_or_service_origin_code",
    "place_of_manufacture",
    "place_of_manufacture_code",
    "subcontracting_plan",
    "subcontracting_plan_code",
    "interagency_contracting_authority",
    "interagency_contracting_authority_code",
    "commercial_item_acquisition",
    "commercial_item_acquisition_code",
    "research",
    "research_code",
    "contract_financing",
    "contract_financing_code",
    "cost_or_pricing_data",
    "cost_or_pricing_data_code",
    "clinger_cohen_act_planning",
    "clinger_cohen_act_planning_code",
    "clinger_cohen_act_compliance",
    "clinger_cohen_act_compliance_code",
    "sea_transportation",
    "sea_transportation_code",
    "materials_supplies",
    "materials_supplies_code",
    "labor_standards",
    "labor_standards_code",
    "construction_wage_rate_requirements",
    "construction_wage_rate_requirements_code",
    "service_contract_act",
    "service_contract_act_code",
    "davis_bacon_act",
    "davis_bacon_act_code",
    "purchase_card_as_payment_method",
    "purchase_card_as_payment_method_code",
    "a_76_fair_act_action",
    "a_76_fair_act_action_code",
    "local_area_set_aside",
    "local_area_set_aside_code",
    "statutory_exception_to_fair_opportunity",
    "statutory_exception_to_fair_opportunity_code",
    "manufacturer_of_goods",
    "contracting_officers_determination_of_business_size",
    "contracting_officers_determination_of_business_size_code",
    "program_acronym",
    "national_interest_action",
    "national_interest_action_code",
    "small_business_competitive",
    "small_business_competitiveness_demonstration_program",
    "small_disadvantaged_business",
    "woman_owned_business",
    "economically_disadvantaged_women_owned_small_business",
    "joint_venture_women_owned_small_business",
    "joint_venture_economic_disadvantaged_women_owned_small_bus",
    "veteran_owned_business",
    "service_disabled_veteran_owned_business",
    "minority_owned_business",
    "contract_bundling",
    "consolidated_contract",
    "consolidated_contract_code",
    "labor_surplus_area_firm",
    "total_dollars_obligated",
    "total_outlayed_amount_for_overall_award",
    "government_furnished_property",
    "government_furnished_property_code",
}

DEFAULT_EXCLUDE_KEYWORDS = (
    "unique_key",
    "award_id",
    "piid",
    "uei",
    "duns",
    "permalink",
    "description",
    "text",
    "address",
    "name",
    "city",
    "county",
    "zip",
    "phone",
    "fax",
    "treasury_accounts",
    "federal_accounts",
    "object_classes",
    "program_activities",
    "transaction",
    "cage_code",
    "recipient",
    "prime_award",
    "last_modified",
    "initial_report",
    "usaspending_permalink",
    "award_description",
)


def candidate_feature_columns(
    *,
    db_path: Path | str = DEFAULT_DB_PATH,
    explicit_keep: Optional[Iterable[str]] = None,
    exclude_keywords: Optional[Iterable[str]] = None,
) -> list[str]:
    """Derive a feature column list from the prime transactions table."""
    explicit = set(explicit_keep or DEFAULT_EXPLICIT_KEEP)
    excluded = tuple(exclude_keywords or DEFAULT_EXCLUDE_KEYWORDS)
    columns = list_prime_transaction_columns(db_path=db_path)
    selected: list[str] = []

    for col in columns:
        if col in explicit:
            selected.append(col)
            continue
        if any(keyword in col for keyword in excluded):
            continue
        if col.endswith("_code") or col.endswith("_flag"):
            selected.append(col)
            continue
        if col.startswith(("small_", "minority_", "women_", "woman_", "veteran_", "service_disabled_veteran", "economically_disadvantaged", "joint_venture")):
            selected.append(col)
            continue
        if col.startswith(("corporate_", "partnership", "sole_proprietorship", "nonprofit_", "for_profit_", "organizational_", "us_", "foreign_", "community_", "labor_", "airport_", "housing_", "tribal_", "educational_", "hospital_", "manufactur", "receives_", "subchapter_", "limited_liability")):
            selected.append(col)
            continue
        if col.endswith("_indicator") or col.endswith("_program") or "business" in col or "government" in col:
            selected.append(col)
            continue
        if col in {"action_date_fiscal_year", "ordering_period_end_date", "solicitation_date", "period_of_performance_start_date", "period_of_performance_current_end_date", "period_of_performance_potential_end_date"}:
            selected.append(col)
            continue

    # Preserve original order, remove duplicates
    ordered_unique: list[str] = []
    seen: set[str] = set()
    for col in selected:
        if col not in seen:
            ordered_unique.append(col)
            seen.add(col)
    return ordered_unique


# ---------------------------------------------------------------------------
# Modelling utilities


def _build_one_hot_encoder(max_categories: Optional[int] = None) -> OneHotEncoder:
    encoder_kwargs = {"handle_unknown": "ignore"}
    if max_categories is not None:
        encoder_kwargs["max_categories"] = max_categories
    try:
        return OneHotEncoder(sparse_output=False, **encoder_kwargs)
    except TypeError:
        encoder_kwargs.pop("max_categories", None)
        encoder_kwargs["sparse"] = False
        if max_categories is not None:
            encoder_kwargs["max_categories"] = max_categories
        return OneHotEncoder(**encoder_kwargs)


@dataclass
class LinearModelArtifacts:
    model: Pipeline
    feature_columns: dict[str, list[str]]
    train_metrics: dict[str, float]
    test_metrics: dict[str, float]
    predictions: pd.DataFrame


def train_log_linear_model_with_split(
    source_df: pd.DataFrame,
    *,
    target_col: str = "annualized_base_all",
    test_size: float = 0.2,
    random_state: int = 42,
    max_categories: int = 50,
    min_nonnull_ratio: float = 0.01,
    max_unique_ratio: float = 0.8,
    max_unique_categories: int = 300,
    drop_columns: Optional[Sequence[str]] = None,
) -> LinearModelArtifacts:
    """Train a multivariate log-linear model with an explicit train/test split."""
    if target_col not in source_df.columns:
        raise KeyError(f"{target_col} is missing from the provided DataFrame.")

    working = source_df.copy()
    working = working.replace({np.inf: np.nan, -np.inf: np.nan})

    mask = working[target_col].notna() & (working[target_col] > 0)
    working = working.loc[mask].copy()
    working["log_target"] = np.log10(working[target_col])

    if "number_of_offers_received" in working.columns:
        working["log_offers"] = np.log1p(
            working["number_of_offers_received"].clip(lower=0).astype(float)
        )

    if "performance_years" in working.columns:
        valid_years = working["performance_years"].where(
            working["performance_years"] > 0
        )
        working["log_duration"] = np.log10(valid_years)

    drop_cols = set(drop_columns or [])
    drop_cols.update(
        col for col in working.columns if col.startswith("annualized_")
    )
    drop_cols.discard(target_col)

    feature_df = working.drop(columns=list(drop_cols))
    y = working["log_target"]
    feature_df = feature_df.drop(columns=[target_col, "log_target"])

    nonnull_ratio = feature_df.notna().mean()
    low_support_cols = nonnull_ratio[nonnull_ratio < min_nonnull_ratio].index.tolist()
    if low_support_cols:
        feature_df = feature_df.drop(columns=low_support_cols)

    constant_cols = feature_df.columns[feature_df.nunique(dropna=True) <= 1].tolist()
    if constant_cols:
        feature_df = feature_df.drop(columns=constant_cols)

    numeric_cols = feature_df.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_cols = [
        col for col in feature_df.columns if col not in numeric_cols
    ]

    high_card_cols: list[str] = []
    for col in categorical_cols:
        nunique = feature_df[col].nunique(dropna=True)
        if nunique == 0:
            high_card_cols.append(col)
            continue
        ratio = nunique / len(feature_df)
        if (ratio > max_unique_ratio) or (max_unique_categories and nunique > max_unique_categories):
            high_card_cols.append(col)
    if high_card_cols:
        feature_df = feature_df.drop(columns=high_card_cols)
        categorical_cols = [col for col in categorical_cols if col not in high_card_cols]

    X = feature_df
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler(with_mean=False)),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", _build_one_hot_encoder(max_categories=max_categories)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols),
        ],
        remainder="drop",
    )

    pipeline = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("regressor", LinearRegression()),
        ]
    )

    pipeline.fit(X_train, y_train)

    train_pred = pipeline.predict(X_train)
    test_pred = pipeline.predict(X_test)

    train_mse = mean_squared_error(y_train, train_pred)
    test_mse = mean_squared_error(y_test, test_pred)

    train_metrics = {
        "rmse": float(np.sqrt(train_mse)),
        "mae": float(mean_absolute_error(y_train, train_pred)),
        "r2": float(r2_score(y_train, train_pred)),
    }
    test_metrics = {
        "rmse": float(np.sqrt(test_mse)),
        "mae": float(mean_absolute_error(y_test, test_pred)),
        "r2": float(r2_score(y_test, test_pred)),
    }

    predictions = pd.DataFrame(
        {
            "actual_log10": y_test,
            "predicted_log10": test_pred,
        },
        index=y_test.index,
    )
    predictions["actual_value"] = np.power(10.0, predictions["actual_log10"])
    predictions["predicted_value"] = np.power(10.0, predictions["predicted_log10"])
    predictions["residual_log10"] = (
        predictions["actual_log10"] - predictions["predicted_log10"]
    )

    return LinearModelArtifacts(
        model=pipeline,
        feature_columns={
            "numeric": numeric_cols,
            "categorical": categorical_cols,
            "dropped_low_support": low_support_cols,
            "dropped_high_cardinality": high_card_cols,
            "dropped_constant": constant_cols,
        },
        train_metrics=train_metrics,
        test_metrics=test_metrics,
        predictions=predictions.sort_index(),
    )


def extract_linear_feature_importance(
    artifacts: LinearModelArtifacts,
    *,
    min_absolute_pct: float = 0.0,
) -> pd.DataFrame:
    """Return coefficients and percentage impacts from a fitted linear pipeline."""
    pipeline = artifacts.model
    preprocessor: ColumnTransformer = pipeline.named_steps["preprocess"]
    regressor: LinearRegression = pipeline.named_steps["regressor"]

    numeric_cols = artifacts.feature_columns.get("numeric", [])
    categorical_cols = artifacts.feature_columns.get("categorical", [])

    feature_names: list[str] = []
    transformer_names: list[str] = []

    if numeric_cols:
        feature_names.extend(numeric_cols)
        transformer_names.extend(["numeric"] * len(numeric_cols))

    if categorical_cols:
        cat_transformer = preprocessor.named_transformers_.get("cat")
        if cat_transformer is not None:
            encoder: OneHotEncoder = cat_transformer.named_steps["encoder"]
            try:
                encoded_names = encoder.get_feature_names_out(categorical_cols)
            except TypeError:
                encoded_names = encoder.get_feature_names(categorical_cols)
            feature_names.extend(encoded_names.tolist())
            transformer_names.extend(["categorical"] * len(encoded_names))

    coefficients = regressor.coef_.ravel()
    if len(coefficients) != len(feature_names):
        raise ValueError(
            "Coefficient vector length does not match derived feature names."
        )

    df = pd.DataFrame(
        {
            "feature": feature_names,
            "source": transformer_names,
            "coefficient": coefficients,
        }
    )
    df["abs_coefficient"] = df["coefficient"].abs()
    df["pct_impact"] = (np.power(10.0, df["coefficient"]) - 1.0) * 100.0
    df["abs_pct_impact"] = df["pct_impact"].abs()

    if min_absolute_pct > 0:
        df = df[df["abs_pct_impact"] >= min_absolute_pct]

    df = df.sort_values("abs_coefficient", ascending=False)
    return df.reset_index(drop=True)


__all__ = [
    "candidate_feature_columns",
    "LinearModelArtifacts",
    "train_log_linear_model_with_split",
    "extract_linear_feature_importance",
]
