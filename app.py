# Strict typing imports
from typing import Dict, Any
import json

# Library imports
import streamlit as st

# Local application imports
from rag_context_debugger.config import config, ConfigError
from rag_context_debugger.tecton_client import TectonDebuggerClient
from rag_context_debugger.mock_client import MockTectonDebuggerClient
from rag_context_debugger.analysis import analyze_retrieved_context, AnalysisResult
from rag_context_debugger.ui_components import display_visual_summary, display_context_details

def main() -> None:
    st.set_page_config(layout="wide", page_title="RAG Context Debugger")
    st.title("🔬 1-Click RAG Context Debugger")
    st.markdown("Instantly diagnose the quality of context retrieved for your RAG application.")

    use_mock = st.checkbox("Run in Mock Mode", value=True, help="Simulate API calls without a live Tecton connection.")

    if not use_mock and config is None:
        st.error("Please set Tecton environment variables or use Mock Mode.")
        st.stop()

    st.subheader("Diagnostic Request")
    
    if use_mock:
        query = st.selectbox(
            "User Query", 
            [
                "How do I reset my password?",
                "How do I set up SSO with Okta?",
                "How do I rotate my API key?"
            ],
            index=0
        )
    else:
        query = st.text_input(
            "User Query", 
            value="How do I reset my password?"
        )

    col1, col2 = st.columns(2)
    with col1:
        if use_mock:
            service_name = st.selectbox(
                "Quality", 
                options=['Green', 'Yellow', 'Red', 'Irrelevant', 'Repetitive', 'Fail'],
                index=0
            )
        else:
            service_name = st.selectbox("Feature Service Name", "product_rag_service")
    with col2:
        join_keys_str = st.text_input("Join Keys (JSON)", '{"user_id": "user_465"}', disabled=use_mock)
        


    if st.button("Diagnose Context", type="primary", use_container_width=True):
        try:
            join_keys: Dict[str, Any] = json.loads(join_keys_str)
            
            with st.spinner("Retrieving and analyzing RAG context..."):
                client: Any = MockTectonDebuggerClient() if use_mock else TectonDebuggerClient()
                feature_vector = client.fetch_context_vector(service_name, join_keys, {"query": query})
                analysis: AnalysisResult = analyze_retrieved_context(feature_vector)

            st.success("Analysis Complete!")

            # Call the new, visually-driven UI components
            display_visual_summary(analysis)
            display_context_details(analysis)

        except (ConfigError, ConnectionError, ValueError, RuntimeError) as e:
            st.error(f"An error occurred: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()