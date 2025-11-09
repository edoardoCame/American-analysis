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
    "total_dollars_obligated",
)

DATE_COLUMNS: tuple[str, ...] = (
    "action_date",
    "period_of_performance_start_date",
    "period_of_performance_current_end_date",
    "period_of_performance_potential_end_date",
    "ordering_period_end_date",
    "solicitation_date",
)

CATEGORICAL_FEATURES: tuple[str, ...] = (
    # Agency info
    "awarding_agency_name",
    "awarding_sub_agency_name",
    "awarding_office_name",
    "funding_agency_name",
    "funding_sub_agency_name",
    "funding_office_name",
    "parent_award_agency_name",
    # Contract structure
    "award_or_idv_flag",
    "award_type",
    "idv_type",
    "parent_award_type",
    "parent_award_single_or_multiple",
    "type_of_contract_pricing",
    "type_of_set_aside",
    "type_of_idc",
    "multiple_or_single_award_idv",
    "action_type",
    # Competition and selection
    "extent_competed",
    "solicitation_procedures",
    "fair_opportunity_limited_sources",
    "other_than_full_and_open_competition",
    "evaluated_preference",
    "commercial_item_acquisition_procedures",
    "simplified_procedures_for_certain_commercial_items",
    # Product/Service
    "product_or_service_code",
    "contract_bundling",
    "place_of_manufacture",
    "country_of_product_or_service_origin",
    "domestic_or_foreign_entity",
    "information_technology_commercial_item_category",
    # Compliance and requirements
    "performance_based_service_acquisition",
    "inherently_governmental_functions",
    "cost_or_pricing_data",
    "cost_accounting_standards_clause",
    "labor_standards",
    "construction_wage_rate_requirements",
    "clinger_cohen_act_planning",
    "government_furnished_property",
    "materials_supplies_articles_equipment",
    "subcontracting_plan",
    "recovered_materials_sustainability",
    "epa_designated_product",
    # Special characteristics
    "multi_year_contract",
    "consolidated_contract",
    "undefinitized_action",
    "purchase_card_as_payment_method",
    "contingency_humanitarian_or_peacekeeping_operation",
    "national_interest_action",
    "a76_fair_act_action",
    "fed_biz_opps",
    "interagency_contracting_authority",
    "contract_financing",
    "sea_transportation",
    "foreign_funding",
    # Vendor business size determination
    "contracting_officers_determination_of_business_size",
    # Vendor identity
    "recipient_name",
    "recipient_parent_name",
    "cage_code",
    # DoD specific
    "dod_claimant_program_description",
    "dod_acquisition_program_description",
    # Text descriptions (for potential NLP)
    "transaction_description",
    "prime_award_base_transaction_description",
    "other_statutory_authority",
    "program_acronym",
    "major_program",
    "sam_exception_description",
    "inherently_governmental_functions_description",
    "foreign_funding_description",
)

NUMERIC_FEATURES: tuple[str, ...] = (
    # Value fields
    "federal_action_obligation",
    "base_and_exercised_options_value",
    "base_and_all_options_value",
    "total_dollars_obligated",
    # Competition
    "number_of_offers_received",
    "price_evaluation_adjustment_preference_percent_difference",
    # Computed ratios and deltas
    "options_vs_base_delta",
    "obligation_to_total_ratio",
    "planned_duration_days",
    "potential_duration_days",
    "ordering_period_duration_days",
    "solicitation_to_award_days",
    "obligation_per_day",
    "number_of_actions",
)

BOOLEAN_FEATURES: tuple[str, ...] = (
    # Small business and socioeconomic categories
    "small_disadvantaged_business",
    "veteran_owned_business",
    "service_disabled_veteran_owned_business",
    "woman_owned_business",
    "women_owned_small_business",
    "economically_disadvantaged_women_owned_small_business",
    "joint_venture_women_owned_small_business",
    "joint_venture_economic_disadvantaged_women_owned_small_bus",
    "historically_underutilized_business_zone_hubzone_firm",
    "c8a_program_participant",
    "sba_certified_8a_joint_venture",
    "self_certified_small_disadvantaged_business",
    "emerging_small_business",
    "the_ability_one_program",
    # Minority owned
    "minority_owned_business",
    "alaskan_native_corporation_owned_firm",
    "american_indian_owned_business",
    "indian_tribe_federally_recognized",
    "native_hawaiian_organization_owned_firm",
    "tribally_owned_firm",
    "subcontinent_asian_asian_indian_american_owned_business",
    "asian_pacific_american_owned_business",
    "black_american_owned_business",
    "hispanic_american_owned_business",
    "native_american_owned_business",
    "other_minority_owned_business",
    # Other business characteristics
    "labor_surplus_area_firm",
    "community_developed_corporation_owned_firm",
    "dot_certified_disadvantage",
    # Government entities
    "us_federal_government",
    "federally_funded_research_and_development_corp",
    "federal_agency",
    "us_state_government",
    "us_local_government",
    "city_local_government",
    "county_local_government",
    "inter_municipal_local_government",
    "local_government_owned",
    "municipality_local_government",
    "school_district_local_government",
    "township_local_government",
    "us_tribal_government",
    "foreign_government",
    "airport_authority",
    "council_of_governments",
    "housing_authorities_public_tribal",
    "interstate_entity",
    "planning_commission",
    "port_authority",
    "transit_authority",
    # Organizational types
    "corporate_entity_not_tax_exempt",
    "corporate_entity_tax_exempt",
    "partnership_or_limited_liability_partnership",
    "sole_proprietorship",
    "small_agricultural_cooperative",
    "international_organization",
    "us_government_entity",
    "community_development_corporation",
    "domestic_shelter",
    "educational_institution",
    "foundation",
    "hospital_flag",
    "manufacturer_of_goods",
    "veterinary_hospital",
    "subchapter_scorporation",
    "limited_liability_corporation",
    "foreign_owned",
    "for_profit_organization",
    "nonprofit_organization",
    "other_not_for_profit_organization",
    # Educational institutions
    "private_university_or_college",
    "state_controlled_institution_of_higher_learning",
    "1862_land_grant_college",
    "1890_land_grant_college",
    "1994_land_grant_college",
    "minority_institution",
    "historically_black_college",
    "tribal_college",
    "alaskan_native_servicing_institution",
    "native_hawaiian_servicing_institution",
    "hispanic_servicing_institution",
    "school_of_forestry",
    "veterinary_college",
    # Recipient operational flags
    "receives_contracts",
    "receives_financial_assistance",
    "receives_contracts_and_financial_assistance",
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
        # Identifiers (for filtering only, not features)
        "contract_transaction_unique_key",
        "contract_award_unique_key",
        "award_id_piid",
        "modification_number",
        "naics_code",
        "naics_description",
        # Agency codes (for reference)
        "awarding_agency_code",
        "awarding_sub_agency_code",
        "awarding_office_code",
        "funding_agency_code",
        "funding_sub_agency_code",
        "funding_office_code",
        "parent_award_agency_id",
        # Codes (not used as features, descriptive versions used instead)
        "action_type_code",
        "extent_competed_code",
        "solicitation_procedures_code",
        "type_of_contract_pricing_code",
        "type_of_set_aside_code",
        "type_of_idc_code",
        "multiple_or_single_award_idv_code",
        "performance_based_service_acquisition_code",
        "contract_bundling_code",
        "award_type_code",
        "idv_type_code",
        "parent_award_type_code",
        "parent_award_single_or_multiple_code",
        "dod_claimant_program_code",
        "dod_acquisition_program_code",
        # All categorical features
        *CATEGORICAL_FEATURES,
        # All numeric value columns (base)
        "number_of_offers_received",
        "price_evaluation_adjustment_preference_percent_difference",
        "number_of_actions",
        *VALUE_COLUMNS,
        # All date columns
        *DATE_COLUMNS,
        # All boolean features
        *BOOLEAN_FEATURES,
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

    # Convert numeric VALUE_COLUMNS
    for column in VALUE_COLUMNS:
        base_awards[column] = _safe_numeric(base_awards[column])

    # Convert other numeric fields
    base_awards["total_dollars_obligated"] = _safe_numeric(base_awards["total_dollars_obligated"])
    base_awards["number_of_offers_received"] = _safe_numeric(base_awards["number_of_offers_received"])
    base_awards["price_evaluation_adjustment_preference_percent_difference"] = _safe_numeric(
        base_awards["price_evaluation_adjustment_preference_percent_difference"]
    )
    base_awards["number_of_actions"] = _safe_numeric(base_awards["number_of_actions"])

    # Compute financial ratios and deltas
    base_awards["options_vs_base_delta"] = (
        base_awards["base_and_all_options_value"] - base_awards["base_and_exercised_options_value"]
    )
    base_awards["obligation_to_total_ratio"] = _safe_ratio(
        base_awards["federal_action_obligation"], base_awards["base_and_all_options_value"]
    )

    # Parse dates
    base_awards = _parse_dates(base_awards, DATE_COLUMNS)
    
    # Compute date-based features
    base_awards["planned_duration_days"] = (
        base_awards["period_of_performance_current_end_date"]
        - base_awards["period_of_performance_start_date"]
    ).dt.days
    
    base_awards["potential_duration_days"] = (
        base_awards["period_of_performance_potential_end_date"]
        - base_awards["period_of_performance_start_date"]
    ).dt.days
    
    base_awards["ordering_period_duration_days"] = (
        base_awards["ordering_period_end_date"]
        - base_awards["period_of_performance_start_date"]
    ).dt.days
    
    base_awards["solicitation_to_award_days"] = (
        base_awards["action_date"]
        - base_awards["solicitation_date"]
    ).dt.days
    
    base_awards["obligation_per_day"] = _safe_ratio(
        base_awards["federal_action_obligation"], base_awards["planned_duration_days"]
    )

    # Convert boolean fields to actual boolean type, then to int for sklearn compatibility
    for bool_col in BOOLEAN_FEATURES:
        if bool_col in base_awards.columns:
            # Handle various boolean representations
            base_awards[bool_col] = base_awards[bool_col].map(
                lambda x: str(x).strip().upper() in ['TRUE', 'T', 'YES', 'Y', '1'] if pd.notna(x) else False
            ).astype(int)

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
    boolean_features: Sequence[str] = BOOLEAN_FEATURES,
    target_column: str = TARGET_COLUMN,
    test_size: float = 0.2,
    random_state: int = 42,
) -> ModificationModelArtifacts:
    """Train a baseline classifier that predicts contract modification risk."""

    missing_numeric = [col for col in numeric_features if col not in dataset.columns]
    missing_categorical = [col for col in categorical_features if col not in dataset.columns]
    missing_boolean = [col for col in boolean_features if col not in dataset.columns]
    if missing_numeric or missing_categorical or missing_boolean:
        raise KeyError(
            "Dataset is missing required columns: "
            f"numeric={missing_numeric}, categorical={missing_categorical}, boolean={missing_boolean}"
        )

    features = list(numeric_features) + list(categorical_features) + list(boolean_features)
    data = dataset.dropna(subset=[target_column])[features + [target_column]].copy()

    # Convert boolean features to int (0/1) for sklearn compatibility
    for bool_col in boolean_features:
        if bool_col in data.columns:
            data[bool_col] = data[bool_col].astype(int)

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
    
    # Boolean features: treat as numeric (0/1) with median imputation
    boolean_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
            ("bool", boolean_transformer, boolean_features),
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
