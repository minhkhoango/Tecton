# 🔬 1-Click RAG Context Debugger (Visual Warfare Edition)

An interactive diagnostic tool that provides instant, **visual analysis** of RAG application context quality through compelling, intuitive visualizations.

## 🚀 Quick Start

```bash
# Install dependencies
poetry install

# Test with mock scenarios (no setup required)
poetry run rag-debug --mock --quality Green

# Launch interactive web app
poetry run streamlit run app.py
```

## Features

- **Visual Relevance Bars**: Color-coded health bars showing chunk strength
- **Context Collapse Heatmapping**: Highlights repetitive, low-value phrases
- **Embedding Space Visualization**: 2D scatter plot showing semantic diversity
- **Live & Mock Modes**: Run against live Tecton or use built-in mock client
- **Multi-Query Mock Scenarios**: Test 3 different queries with 6 quality levels
- **Answer Surface Analysis**: Generated answers with confidence scores
- **Deterministic Mock Jitter**: Consistent ±0.02 score variation with seed control

## Health Status System

| Status | Relevance Score | Semantic Diversity | Description |
|--------|----------------|-------------------|-------------|
| **🟢 HEALTHY** | ≥ 0.75 | ≥ 0.80 | Relevant, diverse chunks with good coverage |
| **🟡 WARNING** | 0.60-0.75 OR < 0.80 | < 0.80 | Stale data, repetitive content, or mediocre relevance |
| **🔴 CRITICAL** | < 0.60 | Any | Off-topic content, failed retrieval, or critically low relevance |

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
Use `--mock` flag with `--quality` to test different RAG context quality scenarios:

| Quality | Status | Description |
|---------|--------|-------------|
| `Green` | HEALTHY | Optimal context quality (avg ≈ 0.83-0.85, high diversity) |
| `Yellow` | WARNING | Mediocre relevance (avg ≈ 0.70-0.72) |
| `Red` | CRITICAL | Poor relevance scores (avg ≈ 0.54-0.58) |
| `Irrelevant` | CRITICAL | Very low relevance context (avg ≈ 0.41-0.43) |
| `Repetitive` | WARNING | Context collapse - repetitive content (diversity < 0.80) |
| `Fail` | CRITICAL | Failed retrieval - no chunks |

**Supported Queries:**
- "How do I reset my password?"
- "How do I set up SSO with Okta?"
- "How do I rotate my API key?"

**Example Usage:**
```bash
# Test healthy scenario with specific query
poetry run rag-debug --mock --quality Green --query "How do I set up SSO with Okta?"

# Test warning scenario with seed for deterministic output
poetry run rag-debug --mock --quality Yellow --query "How do I reset my password?" --seed 42

# Test context collapse (repetitive content)
poetry run rag-debug --mock --quality Repetitive --query "How do I rotate my API key?"
```

**Note:** Use `--quality` (preferred) or `--status` for mock mode. The `--seed` parameter ensures consistent output for testing.

## Troubleshooting

### Common Issues & Solutions

| Problem | Cause | Solution |
|---------|-------|----------|
| **Irrelevant (Avg_Scores < 0.60)** | Context doesn't match query | Review vector search parameters, check embedding freshness, verify chunk settings |
| **Repetitive (Diversity < 0.80)** | Repetitive chunks | Reduce chunk overlap, implement deduplication, use diverse training data |
| **No Context Retrieved** | Feature service returns empty results | Check join key values, verify service configuration, ensure data exists |

### Interpreting Results

- **High scores + High diversity**: Optimal context quality ✅
- **High scores + Low diversity**: Good relevance but repetitive content ⚠️
- **Low scores + Any diversity**: Poor relevance, review search strategy ❌
- **No chunks**: Retrieval failure, check configuration ❌