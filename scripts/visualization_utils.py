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
