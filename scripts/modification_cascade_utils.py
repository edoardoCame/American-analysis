"""
Utility functions for contract modification cascade analysis.

This module provides plotting, feature engineering, and analysis functions
for predicting sequential contract modifications in federal security contracts.
"""

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def engineer_modification_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create features for each modification that predict the next modification.
    
    Returns a DataFrame where each row represents a modification N,
    with features available at time N and target indicating if N+1 exists.
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw modifications data with temporal and financial fields
        
    Returns
    -------
    pd.DataFrame
        Engineered dataset with temporal, financial, and velocity features
    """
    df = df.copy()
    
    # Sort to ensure proper temporal ordering
    df = df.sort_values(['contract_award_unique_key', 'action_date']).reset_index(drop=True)
    
    # --- TIME-BASED FEATURES ---
    df['days_since_prev_mod'] = (
        df.groupby('contract_award_unique_key')['action_date']
        .diff()
        .dt.days
    )
    
    contract_start = df.groupby('contract_award_unique_key')['action_date'].transform('first')
    df['days_since_contract_start'] = (df['action_date'] - contract_start).dt.days
    
    df['days_until_current_end'] = (
        df['period_of_performance_current_end_date'] - df['action_date']
    ).dt.days
    
    # --- VALUE-BASED FEATURES ---
    df['current_value'] = df['current_total_value_of_award'].fillna(0)
    df['potential_value'] = df['potential_total_value_of_award'].fillna(0)
    
    base_value = df.groupby('contract_award_unique_key')['current_value'].transform('first')
    df['cumulative_value_change'] = df['current_value'] - base_value
    df['cumulative_value_change_pct'] = (
        df['cumulative_value_change'] / base_value.replace(0, np.nan)
    ) * 100
    
    prev_value = df.groupby('contract_award_unique_key')['current_value'].shift(1)
    df['value_change_from_prev'] = df['current_value'] - prev_value
    df['value_change_from_prev_pct'] = (
        df['value_change_from_prev'] / prev_value.replace(0, np.nan)
    ) * 100
    
    df['value_headroom'] = df['potential_value'] - df['current_value']
    df['value_headroom_pct'] = (
        df['value_headroom'] / df['current_value'].replace(0, np.nan)
    ) * 100
    
    # --- VELOCITY FEATURES ---
    df['mod_frequency'] = (
        df['mod_sequence'] / df['days_since_contract_start'].replace(0, np.nan)
    )
    
    df['value_growth_rate'] = (
        df['cumulative_value_change'] / df['days_since_contract_start'].replace(0, np.nan)
    )
    
    # --- CUMULATIVE FEATURES ---
    df['cumulative_obligation'] = (
        df.groupby('contract_award_unique_key')['federal_action_obligation']
        .cumsum()
    )
    
    df['mods_to_date'] = df['mod_sequence']
    
    # --- CATEGORICAL FEATURES ---
    categorical_base_features = [
        'awarding_agency_name',
        'awarding_sub_agency_name',
        'awarding_office_name',
        'type_of_contract_pricing',
        'solicitation_procedures',
        'extent_competed',
        'performance_based_service_acquisition',
        'product_or_service_code',
    ]
    
    for col in categorical_base_features:
        if col in df.columns:
            df[col] = df.groupby('contract_award_unique_key')[col].ffill()
    
    df['current_action_type'] = df['action_type']
    
    # --- TARGET ---
    df['has_next_modification'] = (
        df.groupby('contract_award_unique_key')['mod_sequence']
        .shift(-1)
        .notna()
    )
    
    next_value = df.groupby('contract_award_unique_key')['current_value'].shift(-1)
    df['next_value_change'] = next_value - df['current_value']
    df['next_value_change_pct'] = (
        df['next_value_change'] / df['current_value'].replace(0, np.nan)
    ) * 100
    
    next_date = df.groupby('contract_award_unique_key')['action_date'].shift(-1)
    df['days_until_next_mod'] = (next_date - df['action_date']).dt.days
    
    return df


def plot_modification_distribution(contract_summary: pd.DataFrame) -> go.Figure:
    """Create histogram of modification counts per contract."""
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=contract_summary['total_mods'],
            nbinsx=50,
            marker_color='steelblue',
            name='Contracts',
        )
    )
    fig.update_layout(
        title='Distribution of modification counts per contract',
        xaxis_title='Number of modifications',
        yaxis_title='Number of contracts',
        template='plotly_white',
        height=450,
    )
    return fig


def plot_agency_modification_avg(contract_summary: pd.DataFrame, min_contracts: int = 100, top_n: int = 12) -> go.Figure:
    """Create bar chart of average modifications by agency."""
    agency_mod_avg = (
        contract_summary.groupby('agency')['total_mods']
        .agg(['mean', 'count'])
        .query(f'count >= {min_contracts}')
        .sort_values('mean', ascending=False)
        .head(top_n)
        .reset_index()
    )
    
    fig = go.Figure(
        data=[
            go.Bar(
                y=agency_mod_avg['agency'],
                x=agency_mod_avg['mean'],
                orientation='h',
                marker_color='darkorange',
                text=[f"{val:.1f}" for val in agency_mod_avg['mean']],
                textposition='outside',
            )
        ]
    )
    fig.update_layout(
        title=f'Average modification count by agency (min {min_contracts} contracts)',
        xaxis_title='Average modifications per contract',
        yaxis_title='Agency',
        template='plotly_white',
        height=500,
    )
    fig.update_yaxes(categoryorder='total ascending')
    return fig


def plot_time_between_modifications(df_engineered: pd.DataFrame) -> go.Figure:
    """Create histogram of time intervals between consecutive modifications."""
    mods_with_prev = df_engineered[df_engineered['days_since_prev_mod'].notna()].copy()
    
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=mods_with_prev['days_since_prev_mod'],
            nbinsx=100,
            marker_color='teal',
            name='Time between mods',
        )
    )
    fig.update_layout(
        title='Distribution of time between consecutive modifications',
        xaxis_title='Days since previous modification',
        yaxis_title='Frequency',
        template='plotly_white',
        height=450,
    )
    fig.update_xaxes(range=[0, 365])
    return fig


def plot_value_evolution_trajectories(df_engineered: pd.DataFrame, n_samples: int = 20, min_mods: int = 5) -> go.Figure:
    """Plot value change trajectories for sample of high-modification contracts."""
    high_mod_contracts = (
        df_engineered.groupby('contract_award_unique_key')['mod_sequence']
        .max()
        .pipe(lambda x: x[x >= min_mods])
        .index
    )
    
    sample_contracts = np.random.choice(
        high_mod_contracts,
        size=min(n_samples, len(high_mod_contracts)),
        replace=False
    )
    sample_df = df_engineered[df_engineered['contract_award_unique_key'].isin(sample_contracts)].copy()
    
    fig = go.Figure()
    for contract_id in sample_contracts:
        contract_data = sample_df[sample_df['contract_award_unique_key'] == contract_id]
        fig.add_trace(
            go.Scatter(
                x=contract_data['mod_sequence'],
                y=contract_data['cumulative_value_change_pct'],
                mode='lines+markers',
                name=contract_id[:20],
                showlegend=False,
                line=dict(width=1.5),
                opacity=0.6,
            )
        )
    
    fig.update_layout(
        title=f'Contract value evolution across modification sequence (sample of {n_samples} contracts)',
        xaxis_title='Modification sequence number',
        yaxis_title='Cumulative value change from base (%)',
        template='plotly_white',
        height=500,
    )
    return fig


def plot_avg_cumulative_value_change(df_engineered: pd.DataFrame, min_count: int = 100, max_mods: int = 20) -> go.Figure:
    """Plot average cumulative value change by modification number."""
    avg_change_by_mod = (
        df_engineered.groupby('mod_sequence')['cumulative_value_change_pct']
        .agg(['mean', 'median', 'count'])
        .query(f'count >= {min_count}')
        .head(max_mods)
        .reset_index()
    )
    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=avg_change_by_mod['mod_sequence'],
            y=avg_change_by_mod['mean'],
            mode='lines+markers',
            name='Mean',
            line=dict(color='crimson', width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=avg_change_by_mod['mod_sequence'],
            y=avg_change_by_mod['median'],
            mode='lines+markers',
            name='Median',
            line=dict(color='steelblue', width=3),
        )
    )
    fig.update_layout(
        title='Average cumulative value change by modification number',
        xaxis_title='Modification number',
        yaxis_title='Cumulative value change (%)',
        template='plotly_white',
        height=450,
    )
    return fig


def plot_roc_curve(fpr: np.ndarray, tpr: np.ndarray, auc_score: float) -> go.Figure:
    """Create ROC curve visualization."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=fpr,
            y=tpr,
            mode='lines',
            name=f'ROC (AUC={auc_score:.3f})',
            line=dict(color='darkblue', width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode='lines',
            name='Chance',
            line=dict(color='gray', dash='dash'),
        )
    )
    fig.update_layout(
        title='ROC Curve: Predicting next modification',
        xaxis_title='False Positive Rate',
        yaxis_title='True Positive Rate',
        template='plotly_white',
        height=450,
    )
    return fig


def plot_precision_recall_curve(precision: np.ndarray, recall: np.ndarray, ap_score: float) -> go.Figure:
    """Create Precision-Recall curve visualization."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=recall,
            y=precision,
            mode='lines',
            name=f'PR (AP={ap_score:.3f})',
            line=dict(color='darkred', width=3),
        )
    )
    fig.update_layout(
        title='Precision-Recall Curve',
        xaxis_title='Recall',
        yaxis_title='Precision',
        template='plotly_white',
        height=450,
    )
    return fig


def plot_confusion_matrix(cm: np.ndarray) -> go.Figure:
    """
    Create styled confusion matrix heatmap.
    
    Parameters
    ----------
    cm : np.ndarray
        2x2 confusion matrix from sklearn
        
    Returns
    -------
    go.Figure
        Plotly figure with annotated heatmap
    """
    # Create text annotations with counts and percentages
    cm_text = []
    total = cm.sum()
    
    for i in range(2):
        row_text = []
        for j in range(2):
            count = cm[i, j]
            pct = (count / total) * 100
            row_text.append(f"{count:,}<br>({pct:.1f}%)")
        cm_text.append(row_text)
    
    fig = go.Figure(
        data=go.Heatmap(
            z=cm,
            x=['Predicted<br>No cascade', 'Predicted<br>Cascades'],
            y=['Actual<br>No cascade', 'Actual<br>Cascades'],
            colorscale='Blues',
            showscale=True,
            text=cm_text,
            texttemplate='%{text}',
            textfont=dict(size=16, color='white'),
            hovertemplate='True: %{y}<br>Predicted: %{x}<br>Count: %{z}<extra></extra>',
        )
    )
    
    fig.update_layout(
        title='Confusion Matrix: Cascade Prediction Performance',
        xaxis_title='Predicted Class',
        yaxis_title='Actual Class',
        template='plotly_white',
        height=500,
        width=600,
        xaxis=dict(side='bottom'),
        yaxis=dict(autorange='reversed'),
    )
    
    return fig


def plot_feature_importance(importance_df: pd.DataFrame, top_n: int = 20) -> go.Figure:
    """Create horizontal bar chart of feature importances."""
    top_features = importance_df.head(top_n)
    
    fig = go.Figure(
        data=[
            go.Bar(
                y=top_features['feature'][::-1],
                x=top_features['importance'][::-1],
                orientation='h',
                marker_color='purple',
                error_x=dict(type='data', array=top_features['std'][::-1]),
            )
        ]
    )
    fig.update_layout(
        title=f'Top {top_n} Feature Importances (Permutation)',
        xaxis_title='Importance',
        yaxis_title='Feature',
        template='plotly_white',
        height=600,
    )
    return fig


def plot_probability_distribution(y_pred_proba: np.ndarray, y_test: np.ndarray) -> go.Figure:
    """Plot distribution of predicted probabilities by actual class."""
    prob_df = pd.DataFrame({
        'predicted_prob': y_pred_proba,
        'actual_class': y_test,
        'actual_label': pd.Series(y_test).map({0: 'No cascade', 1: 'Cascades'})
    })
    
    fig = go.Figure()
    for label in ['No cascade', 'Cascades']:
        data = prob_df[prob_df['actual_label'] == label]['predicted_prob']
        fig.add_trace(
            go.Histogram(
                x=data,
                nbinsx=50,
                name=label,
                opacity=0.7,
            )
        )
    
    fig.update_layout(
        title='Distribution of predicted cascade probabilities by actual outcome',
        xaxis_title='Predicted probability of cascade',
        yaxis_title='Frequency',
        template='plotly_white',
        height=450,
        barmode='overlay',
    )
    return fig


def plot_calibration(y_pred_proba: np.ndarray, y_test: np.ndarray, n_bins: int = 10) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Create calibration plot comparing predicted vs actual rates.
    
    Returns
    -------
    Tuple[go.Figure, pd.DataFrame]
        Plotly figure and calibration statistics DataFrame
    """
    prob_df = pd.DataFrame({
        'predicted_prob': y_pred_proba,
        'actual_class': y_test,
    })
    
    prob_df['prob_decile'] = pd.qcut(prob_df['predicted_prob'], n_bins, labels=False, duplicates='drop')
    calibration = (
        prob_df.groupby('prob_decile')
        .agg(
            mean_pred_prob=('predicted_prob', 'mean'),
            actual_rate=('actual_class', 'mean'),
            count=('actual_class', 'size'),
        )
        .reset_index()
    )
    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=calibration['mean_pred_prob'],
            y=calibration['actual_rate'],
            mode='markers+lines',
            name='Model calibration',
            marker=dict(size=10, color='darkorange'),
            text=[f"Decile {i}<br>N={n:,}" for i, n in enumerate(calibration['count'], 1)],
            hovertemplate='Predicted: %{x:.2f}<br>Actual: %{y:.2f}<br>%{text}<extra></extra>',
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode='lines',
            name='Perfect calibration',
            line=dict(dash='dash', color='gray'),
        )
    )
    fig.update_layout(
        title='Calibration plot: Predicted vs actual cascade rate by probability decile',
        xaxis_title='Mean predicted probability',
        yaxis_title='Actual cascade rate',
        template='plotly_white',
        height=450,
    )
    
    return fig, calibration


def plot_predicted_vs_actual_cost(y_test_reg: pd.Series, y_pred_reg: np.ndarray) -> go.Figure:
    """Create scatter plot of predicted vs actual cost changes."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=y_test_reg,
            y=y_pred_reg,
            mode='markers',
            marker=dict(color='green', size=4, opacity=0.3),
            name='Predictions',
        )
    )
    
    perfect_line = np.linspace(y_test_reg.min(), y_test_reg.max(), 100)
    fig.add_trace(
        go.Scatter(
            x=perfect_line,
            y=perfect_line,
            mode='lines',
            line=dict(color='red', dash='dash'),
            name='Perfect prediction',
        )
    )
    fig.update_layout(
        title='Predicted vs Actual Cost Change to Next Modification',
        xaxis_title='Actual cost change ($)',
        yaxis_title='Predicted cost change ($)',
        template='plotly_white',
        height=500,
    )
    return fig


def plot_residuals_distribution(y_test_reg: pd.Series, y_pred_reg: np.ndarray) -> go.Figure:
    """Create histogram of prediction residuals."""
    residuals = y_test_reg - y_pred_reg
    
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=residuals,
            nbinsx=50,
            marker_color='coral',
            name='Residuals',
        )
    )
    fig.update_layout(
        title='Distribution of Prediction Residuals',
        xaxis_title='Residual (Actual - Predicted)',
        yaxis_title='Frequency',
        template='plotly_white',
        height=450,
    )
    return fig


def export_all_visualizations(
    figures_dict: Dict[str, go.Figure],
    output_dir,
    width: int = 1200,
    height: int = 700,
    scale: int = 2
) -> None:
    """
    Export all figures to PNG files.
    
    Parameters
    ----------
    figures_dict : Dict[str, go.Figure]
        Dictionary mapping filenames to Plotly figures
    output_dir : Path
        Directory to save images
    width : int
        Image width in pixels
    height : int
        Image height in pixels
    scale : int
        Image scale factor for resolution
    """
    import plotly.io as pio
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for filename, fig in figures_dict.items():
        output_path = output_dir / filename
        pio.write_image(fig, str(output_path), width=width, height=height, scale=scale)
        print(f"✓ Saved: {filename}")
