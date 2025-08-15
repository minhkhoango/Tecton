# 🔬 1-Click RAG Context Debugger (Visual Warfare Edition)

An interactive diagnostic tool that provides instant, **visual analysis** of RAG application context quality through compelling, intuitive visualizations.

## 🚀 Quick Start

```bash
# Install dependencies
poetry install

# Test with mock scenarios (no setup required)
poetry run rag-debug --mock --status "Green"

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
poetry run rag-debug --join-keys '{"user_id": "xyz-123"}'
```

**Mock Mode:**
Use `--mock` flag to test different RAG context quality scenarios:

| Service Name | Status | Description |
|--------------|--------|-------------|
| `Green` | HEALTHY | Optimal context quality (0.85-0.92 scores, 0.92 diversity) |
| `Yellow` | WARNING | Mediocre relevance with null values |
| `Red` | CRITICAL | Poor relevance scores below 0.75 |
| `Irrelevant` | CRITICAL | Low relevance context (0.61-0.65 scores) |
| `Repetitive` | WARNING | Context collapse - repetitive content (0.79 diversity) |
| `Fail` | CRITICAL | Failed retrieval - no chunks |

**Example Usage:**
```bash
# Test healthy scenario
poetry run rag-debug --mock --status "Green"

# Test warning scenario (mediocre relevance)
poetry run rag-debug --mock --status "Yellow"

# Test context collapse (repetitive content)
poetry run rag-debug --mock --status "Repetitive"
```

**Note:** The `--query` parameter is not needed for a mock run, where a default query will be used.

## Troubleshooting

### Common Issues & Solutions

| Problem | Cause | Solution |
|---------|-------|----------|
| **Irrelevant (Avg_Scores < 0.75)** | Context doesn't match query | Review vector search parameters, check embedding freshness, verify chunk settings |
| **Repetitive (Diversity < 0.80)** | Repetitive chunks | Reduce chunk overlap, implement deduplication, use diverse training data |
| **No Context Retrieved** | Feature service returns empty results | Check join key values, verify service configuration, ensure data exists |

### Interpreting Results

- **High scores + High diversity**: Optimal context quality ✅
- **High scores + Low diversity**: Good relevance but repetitive content ⚠️
- **Low scores + Any diversity**: Poor relevance, review search strategy ❌
- **No chunks**: Retrieval failure, check configuration ❌