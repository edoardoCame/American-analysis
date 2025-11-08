"""Visualization helpers for USAspending analyses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


@dataclass(frozen=True)
class CompetitionSummary:
    """Summary statistics returned by `plot_competition_value_profile`."""

    data: pd.DataFrame
    metadata: dict[str, object]


def _ensure_numeric(series: pd.Series) -> pd.Series:
    """Return a numeric Series (silently coercing errors to NaN)."""
    return pd.to_numeric(series, errors="coerce")


def plot_competition_value_profile(
    df: pd.DataFrame,
    *,
    value_col: str = "annualized_base_all",
    offers_col: str = "number_of_offers_received",
    procedure_col: str = "solicitation_procedures",
    additional_group_cols: Iterable[str] | None = None,
    competition_bins: Sequence[float] | None = None,
    competition_labels: Sequence[str] | None = None,
    sample_points: int = 500,
    width_per_procedure: float = 7.0,
    height: float = 6.5,
    show_points: bool = True,
) -> tuple[plt.Figure, CompetitionSummary]:
    """Plot annualised contract value against competition intensity.

    Parameters
    ----------
    df:
        Source DataFrame with (at minimum) value, number of offers, and
        solicitation procedure columns.
    value_col:
        Name of the column containing the (positive) dollar amount to display.
    offers_col:
        Name of the column with the number of offers.
    procedure_col:
        Column identifying solicitation procedure labels.
    additional_group_cols:
        Optional collection of column names to include in the returned summary.
    competition_bins:
        Optional explicit bin edges for `pd.cut` on the offers column. If not
        supplied, defaults to [-0.1, 1, 3, 5, 10, np.inf].
    competition_labels:
        Optional labels corresponding to the bins above. Defaults to
        ["1 offer", "2-3", "4-5", "6-10", "11+"].
    sample_points:
        Maximum number of observations drawn *per solicitation procedure* for
        the jittered strip overlay. The full dataset is still used for the
        boxplots and summary table.
    width_per_procedure:
        Horizontal size (in inches) allocated to each solicitation procedure panel.
    height:
        Overall figure height in inches.
    show_points:
        When True, overlay jittered sample points above each boxplot.
    """

    if df.empty:
        raise ValueError("Supplied DataFrame is empty; nothing to plot.")

    working = df.copy()

    mandatory_fields = {value_col, offers_col, procedure_col}
    missing = mandatory_fields.difference(working.columns)
    if missing:
        raise KeyError(f"Required column(s) missing from DataFrame: {sorted(missing)}")

    working[value_col] = _ensure_numeric(working[value_col])
    working[offers_col] = _ensure_numeric(working[offers_col])
    working = working.dropna(subset=[value_col, offers_col, procedure_col])
    working = working[working[value_col] > 0].copy()
    if working.empty:
        raise ValueError(
            "No positive value records remain after filtering for plotting."
        )

    if competition_bins is None:
        competition_bins = (-0.1, 1, 3, 5, 10, np.inf)
    if competition_labels is None:
        competition_labels = ("1 offer", "2-3", "4-5", "6-10", "11+")

    working["competition_bucket"] = pd.cut(
        working[offers_col].fillna(0),
        bins=competition_bins,
        labels=competition_labels,
        include_lowest=True,
        right=True,
    )

    # Keep only buckets with at least one record
    bucket_counts = working["competition_bucket"].value_counts()
    active_buckets = [label for label in competition_labels if bucket_counts.get(label, 0)]
    if not active_buckets:
        raise ValueError("Competition bucketing produced no populated bins.")

    procedure_order = list(
        working[procedure_col].dropna().value_counts().index
    )
    palette = dict(zip(procedure_order, sns.color_palette("Set2", n_colors=len(procedure_order))))

    def _sample(group: pd.DataFrame) -> pd.DataFrame:
        if sample_points <= 0 or len(group) <= sample_points:
            return group
        return group.sample(sample_points, random_state=0)

    sampled = None
    if show_points and sample_points != 0:
        sampled_groups = []
        for _, group in working.groupby(procedure_col):
            sampled_groups.append(_sample(group))
        sampled = pd.concat(sampled_groups, ignore_index=True) if sampled_groups else working.copy()

    def _quantile(series: pd.Series, q: float) -> float:
        return float(np.nanpercentile(series, q))

    group_cols = [procedure_col, "competition_bucket"]
    if additional_group_cols:
        group_cols.extend([col for col in additional_group_cols if col in working.columns])

    summary = (
        working.groupby(group_cols, observed=False)[value_col]
        .agg(
            median="median",
            p25=lambda s: _quantile(s, 25),
            p75=lambda s: _quantile(s, 75),
            awards="size",
        )
        .reset_index()
    )
    summary["median_millions"] = summary["median"] / 1_000_000
    summary["iqr"] = summary["p75"] - summary["p25"]

    # Plot layout: top row for distribution, bottom for counts
    fig = plt.figure(figsize=(width_per_procedure * len(procedure_order), height))
    gs = fig.add_gridspec(2, len(procedure_order), height_ratios=[3, 1], hspace=0.35)

    for idx, procedure in enumerate(procedure_order):
        subset = working[working[procedure_col] == procedure]
        subset_sampled = None
        if show_points and sampled is not None:
            subset_sampled = sampled[sampled[procedure_col] == procedure]
        proc_summary = summary[summary[procedure_col] == procedure]
        proc_summary = (
            proc_summary.set_index("competition_bucket")
            .reindex(active_buckets)
            .dropna(subset=["awards"])
            .reset_index()
        )

        box_ax = fig.add_subplot(gs[0, idx])
        sns.boxplot(
            data=subset,
            x="competition_bucket",
            y=value_col,
            order=active_buckets,
            color=palette[procedure],
            fliersize=2,
            linewidth=1.2,
            ax=box_ax,
        )
        if show_points and subset_sampled is not None and not subset_sampled.empty:
            sns.stripplot(
                data=subset_sampled,
                x="competition_bucket",
                y=value_col,
                order=active_buckets,
                color="black",
                alpha=0.35,
                jitter=0.22,
                size=2.5,
                ax=box_ax,
            )

        box_ax.set_yscale("log")
        box_ax.set_xlabel("Offers received")
        if idx == 0:
            box_ax.set_ylabel("Annualised base + options (USD, log scale)")
        else:
            box_ax.set_ylabel("")
        box_ax.set_title(procedure.title() if procedure.islower() else procedure)

        for x_pos, row in enumerate(proc_summary.itertuples()):
            median_value = float(row.median)
            box_ax.text(
                x_pos,
                median_value,
                f"median: ${median_value:,.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
                color="#333333",
            )

        count_ax = fig.add_subplot(gs[1, idx], sharex=box_ax)
        bar = sns.barplot(
            data=proc_summary,
            x="competition_bucket",
            y="awards",
            order=active_buckets,
            color=palette[procedure],
            ax=count_ax,
        )
        for patch, row in zip(bar.patches, proc_summary.itertuples()):
            count_ax.text(
                patch.get_x() + patch.get_width() / 2,
                patch.get_height(),
                f"{int(row.awards):,}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

        count_ax.set_ylabel("Award count")
        count_ax.set_xlabel("")

    fig.suptitle("Competition intensity vs annualised value", fontsize=16, y=0.97)

    metadata = {
        "value_column": value_col,
        "offers_column": offers_col,
        "procedure_column": procedure_col,
        "competition_bins": list(competition_bins),
        "competition_labels": list(competition_labels),
        "active_competition_labels": active_buckets,
        "sample_points": sample_points,
        "show_points": show_points,
    }

    return fig, CompetitionSummary(summary, metadata)


def plot_high_value_characteristics(
    model_df: pd.DataFrame,
    high_value_df: pd.DataFrame,
    features_to_plot: list[str],
    figsize: tuple[float, float] = (16, 10)
) -> plt.Figure:
    """Plot comparison of feature distributions between all contracts and high-value contracts.
    
    Parameters
    ----------
    model_df:
        Full dataset of contracts
    high_value_df:
        Subset of high-value contracts (e.g., 90th percentile)
    features_to_plot:
        List of feature names to visualize
    figsize:
        Figure size (width, height)
    
    Returns
    -------
    Figure with comparison bar charts
    """
    n_features = len(features_to_plot)
    n_cols = 3
    n_rows = (n_features + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    axes = axes.flatten() if n_rows > 1 else [axes] if n_cols == 1 else axes
    
    for idx, feature in enumerate(features_to_plot):
        if idx >= len(axes) or feature not in model_df.columns:
            continue
        
        ax = axes[idx]
        
        # Calculate distributions
        all_counts = model_df[feature].value_counts(normalize=True).head(6) * 100
        high_counts = high_value_df[feature].value_counts(normalize=True).head(6) * 100
        
        # Align indices
        all_idx = all_counts.index
        comparison_df = pd.DataFrame({
            'All Contracts': all_counts,
            'High-Value (>p90)': high_counts.reindex(all_idx, fill_value=0)
        })
        
        comparison_df.plot(kind='barh', ax=ax, color=['#1f77b4', '#ff7f0e'])
        ax.set_xlabel('Percentage of contracts (%)')
        ax.set_title(f'{feature.replace("_", " ").title()}')
        ax.legend(loc='lower right', fontsize=8)
        
        # Truncate long labels
        labels = [str(label)[:30] + '...' if len(str(label)) > 30 else str(label) 
                  for label in ax.get_yticklabels()]
        ax.set_yticklabels(labels, fontsize=8)
    
    # Hide unused subplots
    for idx in range(len(features_to_plot), len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    return fig


def plot_value_estimation_heatmap(
    model_df: pd.DataFrame,
    row_feature: str,
    col_feature: str,
    filter_dict: dict | None = None,
    figsize: tuple[float, float] = (10, 6),
    value_col: str = 'annualized_base_all',
    min_samples: int = 10
) -> plt.Figure:
    """Create a heatmap showing median contract values for feature combinations.
    
    Parameters
    ----------
    model_df:
        Dataset with contracts
    row_feature:
        Feature name for heatmap rows
    col_feature:
        Feature name for heatmap columns
    filter_dict:
        Optional dict of {feature: value} to filter the dataset
    figsize:
        Figure size
    value_col:
        Column name with contract values
    min_samples:
        Minimum number of samples required for a cell to be shown
        
    Returns
    -------
    Figure with heatmap
    """
    working = model_df.copy()
    
    # Apply filters if provided
    if filter_dict:
        for feat, val in filter_dict.items():
            if feat in working.columns:
                working = working[working[feat] == val]
    
    # Build pivot data
    pivot_data = []
    row_values = working[row_feature].value_counts().head(6).index
    col_values = working[col_feature].value_counts().head(4).index
    
    for row_val in row_values:
        for col_val in col_values:
            mask = (working[row_feature] == row_val) & (working[col_feature] == col_val)
            subset = working[mask]
            if len(subset) >= min_samples:
                pivot_data.append({
                    row_feature: row_val,
                    col_feature: col_val,
                    'Median Value': subset[value_col].median()
                })
    
    if not pivot_data:
        raise ValueError("No valid combinations found with minimum sample size")
    
    pivot_df = pd.DataFrame(pivot_data).pivot(
        index=row_feature,
        columns=col_feature,
        values='Median Value'
    )
    
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        pivot_df / 1e6,  # Convert to millions
        annot=True,
        fmt='.2f',
        cmap='YlOrRd',
        cbar_kws={'label': 'Median Annualized Value (USD millions)'},
        ax=ax
    )
    
    title = f'Expected Contract Value'
    if filter_dict:
        filter_str = ', '.join([f'{k}={v}' for k, v in filter_dict.items()])
        title += f'\n({filter_str})'
    ax.set_title(title)
    ax.set_xlabel(col_feature.replace('_', ' ').title())
    ax.set_ylabel(row_feature.replace('_', ' ').title())
    
    plt.tight_layout()
    return fig
