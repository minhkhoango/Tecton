# Strict typing imports
from typing import Dict, Any
import json

# Library imports
import streamlit as st

# Local application imports
from rag_context_debugger.config import config, ConfigError
from rag_context_debugger.tecton_client import TectonDebuggerClient
from rag_context_debugger.mock_client import MockTectonDebuggerClient
from rag_context_debugger.analysis import analyze_feature_vector, AnalysisResult
from rag_context_debugger.ui_components import display_summary_metrics, display_analysis_tabs

def main() -> None:
    """
    Main function to run the Streamlit application.
    """
    st.set_page_config(layout="wide", page_title="RAG Context Debugger")
    st.title("🔬 1-Click RAG Context Debugger for Tecton")

    # --- Mode Selection ---
    use_mock = st.checkbox(
        "Run in Mock Mode (no API key needed)",
        value=True,
        help="Simulate API calls to demonstrate different scenarios without connecting to Tecton."
    )

    if not use_mock and config is None:
        st.error(
            "**Configuration Error:** To run in Live Mode, Tecton environment variables must be set. "
            "Please set `TECTON_URL`, `TECTON_API_KEY`, and `TECTON_WORKSPACE` or use Mock Mode."
        )
        st.stop()

    # --- User Inputs ---
    st.subheader("Diagnostic Request")
    col1, col2 = st.columns(2)
    with col1:
        # Provide helpful defaults for mock mode
        default_service = "yellow_scenario_service" if use_mock else "fraud_detection_feature_service"
        service_name = st.text_input(
            "Feature Service Name", default_service,
            help="In Mock Mode, use: green_scenario_service, yellow_scenario_service, or red_scenario_service."
        )
    with col2:
        join_keys_str = st.text_input(
            "Join Keys (JSON)", '{"user_id": "user_465"}',
            help='The primary keys to look up features, as a JSON string.'
        )

    request_data_str = st.text_area(
        "Request Context Map (JSON, Optional)", '{}',
        help="Request-time data for on-demand features, as a JSON string."
    )

    if st.button("Run Diagnosis", type="primary", use_container_width=True):
        try:
            join_keys: Dict[str, Any] = json.loads(join_keys_str)
            request_data: Dict[str, Any] = json.loads(request_data_str)

            with st.spinner("Fetching and analyzing context..."):
                # --- CONDITIONAL CLIENT INITIALIZATION ---
                # Based on the checkbox, we instantiate either the real or mock client.
                # This is a clean way to implement a strategy pattern.
                if use_mock:
                    client: Any = MockTectonDebuggerClient()
                else:
                    client = TectonDebuggerClient()

                feature_vector = client.fetch_context_vector(service_name, join_keys, request_data)
                analysis: AnalysisResult = analyze_feature_vector(feature_vector)

            st.success("Analysis Complete!")

            display_summary_metrics(analysis)
            display_analysis_tabs(analysis)

        except json.JSONDecodeError:
            st.error("Invalid JSON provided. Please check the format of your Join Keys or Request Context.")
        except (ConfigError, ConnectionError, ValueError, RuntimeError) as e:
            st.error(f"An error occurred: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()