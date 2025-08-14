# 🔬 1-Click RAG Context Debugger

A lightweight diagnostic tool for developers building Retrieval-Augmented Generation (RAG) applications on Tecton. It provides an instant, clear analysis of the context vector retrieved from a Tecton Feature Service, helping to rapidly diagnose issues related to data freshness, latency, and temporal cohesion.

## Features

- **Dual Interface**: Use it as a scriptable **CLI** or an interactive **Streamlit Web App**.
- **Live & Mock Modes**: Run against a live Tecton environment or use the built-in mock client to simulate different scenarios without needing API keys.
- **SLO Analysis**: Instantly see if a feature retrieval request met its latency SLO.
- **Temporal Cohesion Analysis**: Automatically detects and flags risks when features in the context vector are from wildly different points in time.

## Setup

(Setup instructions remain the same)

## Usage

### Streamlit Web App

For a rich, visual, and interactive analysis.

```bash
streamlit run app.py
```

Navigate to the local URL. Use the "Run in Mock Mode" checkbox to simulate API calls without needing live credentials.

### Command-Line Interface (CLI)

For quick, scriptable diagnosis.

**Live Mode:**

```bash
# Ensure TECTON environment variables are set
rag-debug --service-name "your_feature_service" --join-keys '{"user_id": "xyz-123"}'
```

**Mock Mode:**

Use the `--mock` flag to run without API keys. You can use specific service names to trigger different scenarios:
- `green_scenario_service`: Simulates a healthy response.
- `yellow_scenario_service`: Simulates a response with stale data and a null value.
- `red_scenario_service`: Simulates a response with high temporal risk.

```bash
rag-debug --mock --service-name "yellow_scenario_service" --join-keys '{"user_id": "any"}'
```