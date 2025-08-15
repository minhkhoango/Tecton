# 🔬 1-Click RAG Context Debugger (Visual Warfare Edition)

An interactive diagnostic tool that provides instant, **visual analysis** of RAG application context quality through compelling, intuitive visualizations.

## 🚀 Quick Start

```bash
# Install dependencies
poetry install

# Test with mock scenarios (no setup required)
poetry run rag-debug --mock --service-name "green_scenario_service" --join-keys '{"user_id": "test"}'

# Launch interactive web app
poetry run streamlit run app.py
```

## Features

- **Visual Relevance Bars**: Color-coded health bars showing chunk strength
- **Context Collapse Heatmapping**: Highlights repetitive, low-value phrases
- **Embedding Space Visualization**: 2D scatter plot showing semantic diversity
- **Live & Mock Modes**: Run against live Tecton or use built-in mock client

## Health Status System

| Status | Relevance Score | Semantic Diversity | Description |
|--------|----------------|-------------------|-------------|
| **🟢 HEALTHY** | ≥ 0.82 | ≥ 0.80 | Relevant, diverse chunks with good coverage |
| **🟡 WARNING** | 0.75-0.82 OR < 0.80 | < 0.80 | Stale data, repetitive content, or mediocre relevance |
| **🔴 CRITICAL** | < 0.75 | Any | Off-topic content, failed retrieval, or critically low relevance |

## Usage

### Streamlit Web App
```bash
poetry run streamlit run app.py
```
Navigate to the local URL. Use "Run in Mock Mode" to simulate API calls without credentials.

### Command-Line Interface (CLI)

**Live Mode:**
```bash
poetry run rag-debug --service-name "your_feature_service" --join-keys '{"user_id": "xyz-123"}'
```

**Mock Mode:**
Use `--mock` flag to test different RAG context quality scenarios:

| Service Name | Status | Description |
|--------------|--------|-------------|
| `green_scenario_service` | HEALTHY | Optimal context quality (0.85-0.92 scores, 0.92 diversity) |
| `yellow_scenario_service` | WARNING | Mediocre relevance with null values |
| `red_scenario_service` | CRITICAL | Poor relevance scores below 0.75 |
| `low_relevance_service` | CRITICAL | Low relevance context (0.61-0.65 scores) |
| `collapse_service` | WARNING | Context collapse - repetitive content (0.79 diversity) |
| `fail_service` | CRITICAL | Failed retrieval - no chunks |

**Example Usage:**
```bash
# Test healthy scenario
poetry run rag-debug --mock --service-name "green_scenario_service" --join-keys '{"user_id": "any"}'

# Test warning scenario (mediocre relevance)
poetry run rag-debug --mock --service-name "yellow_scenario_service" --join-keys '{"user_id": "any"}'

# Test context collapse (repetitive content)
poetry run rag-debug --mock --service-name "collapse_service" --join-keys '{"user_id": "any"}'
```

**Note:** The `--query` parameter is optional. If not provided, a default query will be used.

## Troubleshooting

### Common Issues & Solutions

| Problem | Cause | Solution |
|---------|-------|----------|
| **Low Relevance Scores (< 0.75)** | Context doesn't match query | Review vector search parameters, check embedding freshness, verify chunk settings |
| **Context Collapse (Diversity < 0.80)** | Repetitive chunks | Reduce chunk overlap, implement deduplication, use diverse training data |
| **No Context Retrieved** | Feature service returns empty results | Check join key values, verify service configuration, ensure data exists |

### Interpreting Results

- **High scores + High diversity**: Optimal context quality ✅
- **High scores + Low diversity**: Good relevance but repetitive content ⚠️
- **Low scores + Any diversity**: Poor relevance, review search strategy ❌
- **No chunks**: Retrieval failure, check configuration ❌