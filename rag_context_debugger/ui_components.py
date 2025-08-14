# Library imports
import streamlit as st
import pandas as pd
import click
from typing import List

# Local application imports
from .analysis import AnalysisResult

# --- Streamlit Components ---

def display_summary_metrics(analysis: AnalysisResult) -> None:
    """Renders the high-level summary metrics in Streamlit."""
    st.subheader("Diagnostic Summary")
    
    slo = analysis.get('slo_report')
    temporal = analysis.get('temporal_report')
    
    col1, col2, col3 = st.columns(3)
    
    # Latency Metric
    latency = slo.get('server_time_seconds', 0.0) if slo else 0.0
    col1.metric("Server Latency", f"{latency:.4f}s", help="Time taken by Tecton to compute and retrieve the feature vector.")
    
    # Temporal Spread Metric
    spread = temporal.get('time_spread_seconds', 0.0) if temporal else 0.0
    col2.metric("Temporal Spread", f"{spread:.2f}s", help="The time difference between the newest and oldest features in the context vector.")
    
    # Cohesion Risk Metric
    risk = temporal.get('risk_level', 'N/A') if temporal else 'N/A'
    col3.metric("Cohesion Risk", risk, help="An assessment of risk based on the temporal spread. HIGH risk may lead to logically inconsistent context.")

def display_analysis_tabs(analysis: AnalysisResult) -> None:
    """Renders the detailed analysis in a set of tabs in Streamlit."""
    tab1, tab2, tab3 = st.tabs(["Feature Values", "Temporal Analysis", "Raw Metadata"])

    with tab1:
        st.markdown("#### Retrieved Feature Values")
        features = analysis.get('features', {})
        if features:
            features_df = pd.DataFrame(features.items(), columns=['Feature Name', 'Value'])
            st.dataframe(features_df, use_container_width=True)  # type: ignore
        else:
            st.info("No features were retrieved.")

    with tab2:
        st.markdown("#### Point-in-Time Correctness")
        temporal = analysis.get('temporal_report')
        if temporal and temporal.get('feature_timestamps'):
            ts_df = pd.DataFrame(temporal['feature_timestamps'].items(), columns=['Feature Name', 'Effective Timestamp'])
            st.dataframe(ts_df, use_container_width=True)  # type: ignore
        else:
            st.info("No temporal data available for analysis (requires at least two features with timestamps).")
    
    with tab3:
        st.markdown("#### Raw Tecton Metadata")
        st.json(analysis.get('raw_metadata', {}))

# --- CLI Formatting Component ---

def format_cli_report(analysis: AnalysisResult) -> str:
    """Formats the full analysis result into a string for CLI output."""
    report_parts: List[str] = []

    # --- Feature Values Section ---
    report_parts.append(click.style("\n--- Feature Values ---", fg="cyan"))
    features = analysis.get('features', {})
    if features:
        for k, v in features.items():
            # Add a visual indicator for None values
            indicator = click.style(" (NULL)", fg="yellow") if v is None else ""
            report_parts.append(f"{k}: {v}{indicator}")
    else:
        report_parts.append("No features were retrieved.")

    # --- SLO Report Section ---
    report_parts.append(click.style("\n--- SLO Report ---", fg="cyan"))
    slo = analysis.get('slo_report')
    if slo:
        latency = slo.get('server_time_seconds')
        latency_str = f"{latency:.4f}s" if isinstance(latency, float) else "N/A"
        report_parts.append(f"Server Latency: {latency_str}")
    else:
        report_parts.append("SLO info not available.")

    # --- Temporal Cohesion Section ---
    report_parts.append(click.style("\n--- Temporal Cohesion Report ---", fg="cyan"))
    temporal = analysis.get('temporal_report')
    if temporal:
        risk = temporal['risk_level']
        color = "green" if risk == "LOW" else ("yellow" if risk == "MEDIUM" else "red")
        report_parts.append(f"Risk Level: {click.style(risk, fg=color, bold=True)}")
        report_parts.append(f"Time Spread: {temporal['time_spread_seconds']:.2f} seconds")
        report_parts.append(f"Oldest Feature Time: {temporal['min_effective_time']}")
        report_parts.append(f"Newest Feature Time: {temporal['max_effective_time']}")
    else:
        report_parts.append("Temporal analysis not applicable (fewer than 2 features with timestamps).")
    
    report_parts.append("\n")
    return "\n".join(report_parts)