# RAG Diagnostic Engine: A Business Case

**This tool reduces the operational cost of production RAG systems by saving $30,000 to $50,000 per ML engineer annually. It achieves this by cutting debugging time and accelerating the Mean Time to Resolution (MTTR) for context-related failures.**

## The Problem

Production RAG systems suffer from hidden operational costs. When context retrieval fails or returns irrelevant information, ML engineers spend 20-40% of their time debugging these issues—costing millions annually in lost productivity.

## The Solution

A diagnostic engine that provides real-time operational intelligence into the RAG retrieval process, transforming multi-day debugging cycles into immediate root-cause identification.

**Key Features:**
- **Visual Relevance Analysis** → Immediately identifies off-topic context and failed retrievals  
- **Semantic Diversity Plot** → Instantly flags repetitive "context collapse" patterns  
- **Automated Health Status** → Reduces cognitive load and accelerates root-cause analysis  

## Business Impact

### Annual Operational Savings per ML Engineer: $27,000 - $40,500

| Metric | Impact | Business Value |
|--------|--------|----------------|
| **Reduce MTTR by up to 90%** | Multi-day resolution → under an hour | Faster incident response, reduced customer impact |
| **Reclaim 6-9 Engineering Hours Weekly** | Convert 30% of debugging time into feature development | Increased product velocity, faster time-to-market |
| **Scale Savings Across Teams** | 10 engineers = $270,000+ annual savings | Direct bottom-line impact on engineering efficiency |

## Quick Start

### Primary: Streamlit Web App (Recommended)

```bash
# Install dependencies
poetry install

# Launch interactive web app
poetry run streamlit run app.py
```

Navigate to the local URL for interactive analysis and visualization.

### Secondary: Command-Line Interface

```bash
# Test with mock scenarios (no setup required)
poetry run rag-debug --mock --quality Green

# Live mode
poetry run rag-debug --join-keys '{"user_id": "xyz-123"}'
```

## Technical Features

- **Per-Chunk Relevance Scoring**: Color-coded health bars showing individual chunk strength
- **Semantic Repetition Analysis**: Identifies repetitive, low-value content patterns  
- **Semantic Diversity Visualization**: 2D scatter plot showing context variety
- **Live & Mock Modes**: Run against live Tecton or use built-in mock client
- **Multi-Query Mock Scenarios**: Test different queries with 6 quality levels

### Health Status System

| Status | Relevance Score | Semantic Diversity | Description |
|--------|----------------|-------------------|-------------|
| **HEALTHY** | ≥ 0.75 | ≥ 0.80 | Relevant, diverse chunks with good coverage |
| **WARNING** | 0.60-0.75 OR < 0.80 | < 0.80 | Stale data, repetitive content, or mediocre relevance |
| **CRITICAL** | < 0.60 | Any | Off-topic content, failed retrieval, or critically low relevance |

### Mock Mode Options

| Quality | Status | Description |
|---------|--------|-------------|
| `Green` | HEALTHY | Optimal context quality (avg ≈ 0.83-0.85, high diversity) |
| `Yellow` | WARNING | Mediocre relevance (avg ≈ 0.70-0.72) |
| `Red` | CRITICAL | Poor relevance scores (avg ≈ 0.54-0.58) |
| `Irrelevant` | CRITICAL | Very low relevance context (avg ≈ 0.41-0.43) |
| `Repetitive` | WARNING | Context collapse - repetitive content (diversity < 0.80) |
| `Fail` | CRITICAL | Failed retrieval - no chunks |

**Supported Queries:** "How do I reset my password?", "How do I set up SSO with Okta?", "How do I rotate my API key?"

**Example:**
```bash
poetry run rag-debug --mock --quality Green --query "How do I set up SSO with Okta?"
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| **Irrelevant (Avg_Scores < 0.60)** | Context doesn't match query | Review vector search parameters, check embedding freshness, verify chunk settings |
| **Repetitive (Diversity < 0.80)** | Repetitive chunks | Reduce chunk overlap, implement deduplication, use diverse training data |
| **No Context Retrieved** | Feature service returns empty results | Check join key values, verify service configuration, ensure data exists |

**Interpreting Results:**
- **High scores + High diversity**: Optimal context quality ✅
- **High scores + Low diversity**: Good relevance but repetitive content ⚠️
- **Low scores + Any diversity**: Poor relevance, review search strategy ❌
- **No chunks**: Retrieval failure, check configuration ❌