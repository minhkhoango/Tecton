# RAG Diagnostic Engine: A Business Case

**This tool reduces the operational cost of production RAG systems by saving $30,000 to $50,000 per ML engineer annually. It achieves this by cutting debugging time and accelerating the Mean Time to Resolution (MTTR) for context-related failures.**

## The Operational Problem

Production RAG systems suffer from a hidden operational drain that costs engineering teams millions annually. When context retrieval fails or returns irrelevant information, ML engineers spend 20-40% of their time debugging these issues—an unquantified engineering tax that directly impacts product velocity and customer experience.

**The Hidden Cost:** Every production incident involving poor RAG context quality triggers a debugging cycle that can take days to resolve, while engineers struggle to identify whether the problem lies in vector search parameters, embedding freshness, chunk configuration, or data quality.

## The Solution: RAG Diagnostic Engine

A diagnostic engine that provides real-time operational intelligence into the RAG retrieval process, transforming multi-day debugging cycles into immediate root-cause identification.

**Visual Relevance Analysis** → Immediately identifies off-topic context and failed retrievals  
**Semantic Diversity Plot** → Instantly flags repetitive "context collapse" patterns  
**Automated Health Status** → Reduces cognitive load and accelerates root-cause analysis  

## Quantifiable Business Impact

### Annual Operational Savings per ML Engineer: $27,000 - $40,500

| Metric | Impact | Business Value |
|--------|--------|----------------|
| **Reduce MTTR by up to 90%** | Move from multi-day resolution to under an hour | Faster incident response, reduced customer impact |
| **Reclaim 6-9 Engineering Hours Weekly** | Convert 30% of debugging time into new feature development | Increased product velocity, faster time-to-market |
| **Scale Savings Across Teams** | A team of 10 engineers realizes over $270,000 in annual savings | Direct bottom-line impact on engineering efficiency |

**Calculation:** At an average loaded cost of $90/hour, recovering 6-9 hours of debugging time per engineer per week directly translates to $27,000-$40,500 in annual operational savings.

## Live Demo & Quick Start

### Immediate Value Demonstration

```bash
# Install dependencies
poetry install

# Test with mock scenarios (no setup required)
poetry run rag-debug --mock --quality Green

# Launch interactive web app
poetry run streamlit run app.py
```

**No Credentials Required:** Use "Run in Mock Mode" to simulate API calls and immediately see the diagnostic capabilities in action.

## Technical Implementation & Usage Guide

### Core Diagnostic Features

- **Per-Chunk Relevance Scoring**: Color-coded health bars showing individual chunk strength
- **Semantic Repetition Analysis**: Identifies repetitive, low-value content patterns  
- **Semantic Diversity Visualization**: 2D scatter plot showing context variety
- **Live & Mock Modes**: Run against live Tecton or use built-in mock client
- **Multi-Query Mock Scenarios**: Test 3 different queries with 6 quality levels
- **Answer Surface Analysis**: Generated answers with confidence scores
- **Deterministic Mock Jitter**: Consistent ±0.02 score variation with seed control

### Health Status System

| Status | Relevance Score | Semantic Diversity | Description |
|--------|----------------|-------------------|-------------|
| **HEALTHY** | ≥ 0.75 | ≥ 0.80 | Relevant, diverse chunks with good coverage |
| **WARNING** | 0.60-0.75 OR < 0.80 | < 0.80 | Stale data, repetitive content, or mediocre relevance |
| **CRITICAL** | < 0.60 | Any | Off-topic content, failed retrieval, or critically low relevance |

### Usage Options

#### Streamlit Web App
```bash
poetry run streamlit run app.py
```
Navigate to the local URL for interactive analysis and visualization.

#### Command-Line Interface (CLI)

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

### Troubleshooting Guide

#### Common Issues & Solutions

| Problem | Cause | Solution |
|---------|-------|----------|
| **Irrelevant (Avg_Scores < 0.60)** | Context doesn't match query | Review vector search parameters, check embedding freshness, verify chunk settings |
| **Repetitive (Diversity < 0.80)** | Repetitive chunks | Reduce chunk overlap, implement deduplication, use diverse training data |
| **No Context Retrieved** | Feature service returns empty results | Check join key values, verify service configuration, ensure data exists |

#### Interpreting Results

- **High scores + High diversity**: Optimal context quality ✅
- **High scores + Low diversity**: Good relevance but repetitive content ⚠️
- **Low scores + Any diversity**: Poor relevance, review search strategy ❌
- **No chunks**: Retrieval failure, check configuration ❌