# RAG vs Markdown: Local Evidence Benchmark

**Does compiling PDFs into structured Markdown before indexing improve RAG quality?**

This project is not a RAG demo. It is a **diagnostic framework** to separate the effects of document preprocessing, retrieval, generation, and epistemic behavior (knowing when not to answer) in local RAG pipelines.

## Research Questions

| ID | Question | Status |
|----|----------|--------|
| RQ1 | Does Markdown compilation improve overall quality vs. raw PDF text? | **Completed** (Qwen Δ = +1.2%, Gemma Δ = −8.3%) |
| RQ2 | Does the Markdown advantage persist with stronger generative models? | **Completed** (No — Gemma 4 26B prefers Raw, Δ = −8.3%) |
| RQ3 | Are errors primarily caused by retrieval failures or generation failures? | **Completed** (~60% retrieval, ~25% generation, ~15% scoring/citation) |

## Pipelines

```
Pipeline A (Raw)   PDF → PyMuPDF → raw text → chunks → ChromaDB → retrieve → LLM
Pipeline B (MD)    PDF → PyMuPDF → raw text → Markdown → chunks → ChromaDB → retrieve → LLM
```

| Pipeline | Description | Embeddings | Vector DB | LLM |
|----------|-------------|-----------|-----------|-----|
| **A** | Raw extracted text | all-MiniLM-L6-v2 | ChromaDB (cosine) | Configurable |
| **B** | Compiled Markdown | all-MiniLM-L6-v2 | ChromaDB (cosine) | Configurable |

## Results at a Glance

### Qwen 0.8B (Local, LM Studio)

| Pipeline | Mean (/5.0) | Normalized |
|----------|:-----------:|:----------:|
| **B — Markdown** | **2.56** | **51.2%** |
| A — Raw text | 2.50 | 50.0% |
| Delta | +0.06 | +1.2% |

Markdown wins by 1.2%, driven entirely by table-extraction questions (+1.6).

### Gemma 4 26B (Google Gemini API)

| Pipeline | Mean (/5.0) | Normalized |
|----------|:-----------:|:----------:|
| A — Raw text | **3.12** | **62.4%** |
| B — Markdown | 2.86 | 57.2% |
| Delta (B − A) | −0.26 | −5.2% |

With a stronger model, the pattern **reverses**: Raw text outperforms Markdown by 5.2%. The Markdown advantage does not persist.

See [docs/results.md](docs/results.md), the [comparative report](reports/comparative_benchmark.md), and the [Fase 3 oracle report](reports/fase3_retrieval_vs_generation.md).

## Interpreting These Results

This benchmark does not measure "RAG in general". It measures the ability of two pipeline configurations to answer 50 questions we designed. Key findings across all three phases:

- **Retrieval is the primary bottleneck**: the [oracle test](reports/fase3_retrieval_vs_generation.md) shows that giving the LLM the full document text improves scores by +67–85%. Only ~25% of errors are true generation failures.
- **Model × pipeline interaction flips**: Markdown helps small models (Qwen, +1.2%) but hurts larger ones (Gemma 4, −5.2%). Preprocessing strategy should depend on model capability.
- **Famous papers**: All documents are well-known arXiv papers. The [error taxonomy](docs/error_taxonomy.md) helps separate RAG quality from parametric knowledge.

## Experimental Philosophy

This project follows three principles:

1. **Separate concerns**. Each pipeline, model, and metric is a variable that can be changed independently.
2. **Document failure modes**. Errors are classified by origin (retrieval, generation, hallucination) not by final score.
3. **Declare boundaries**. Results are reported within their experimental context, not as general claims.

## Setup

```bash
# Clone
git clone https://github.com/cioffiAI/rag-vs-markdown.git
cd rag-vs-markdown

# Virtual environment
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate # Linux/Mac

# Install
pip install -r requirements.txt
```

Place PDFs in `data/raw/`, then:

```bash
# 1. Extract text from PDFs
python scripts/extract.py

# 2. (Optional) Compile to Markdown for Pipeline B
python scripts/compile_markdown.py

# 3. Build index
python scripts/build_index.py --pipeline a   # raw text index
python scripts/build_index.py --pipeline b   # markdown index

# 4. Run queries
python scripts/query.py --pipeline b "your question?"

# 5. Batch run benchmark
python scripts/query.py --pipeline b --file data/benchmark_questions.json

# 6. Evaluate
python scripts/evaluate.py batch_b_*.json benchmark_results.md

# 7. Compare pipelines
python scripts/compare_pipelines.py

# 8. Classify errors (Fase 3)
python scripts/error_analysis.py batch_*.json --pipeline-label "B" --model-label "Gemma4"

# 9. Run oracle test (Fase 3)
python scripts/oracle_test.py --model gemma-4-26b-a4b-it

# 10. Compare retrieval vs oracle
python scripts/oracle_compare.py batch_results.json oracle_results.json
```

## Benchmark

50 gold-standard questions (Italian questions, English LLM):

| Type | Count | Description |
|------|-------|-------------|
| Simple factual | 15 | Single-document, direct extraction |
| Local reasoning | 10 | Multi-paragraph within one document |
| Multi-document | 10 | Compare/contrast across 2+ papers |
| Table extraction | 5 | Numeric values from tables |
| Negative (trap) | 10 | Questions not answerable from corpus |

Questions file: [data/benchmark_questions.json](data/benchmark_questions.json)

## Project Structure

```
├── scripts/
│   ├── extract.py                 PDF → JSON (PyMuPDF)
│   ├── compile_markdown.py        JSON → Markdown with sections
│   ├── build_index.py             Chunk → embed → ChromaDB (--pipeline a|b)
│   ├── query.py                   Retrieve + LLM generation (multi-provider)
│   ├── evaluate.py                Score answers against ground truth
│   ├── compare_pipelines.py       A vs B comparison report
│   ├── error_analysis.py          E01–E07 error classification
│   ├── oracle_test.py             Oracle context (full document text)
│   ├── oracle_compare.py          Retrieval vs oracle score comparison
│   └── convert_benchmark_to_csv.py
├── data/
│   ├── raw/                       Input PDFs (not tracked)
│   ├── extracted/                 Per-page JSON (not tracked)
│   ├── processed/                 Markdown versions (not tracked)
│   ├── benchmark_questions.json   50 gold-standard questions
│   └── gold_questions.csv         CSV export
├── docs/
│   ├── results.md                 Results with interpretation
│   ├── limitations.md             Known constraints and threats to validity
│   └── error_taxonomy.md          Error classification system
├── reports/
│   ├── comparative_benchmark.md          Gemma 4 26B A vs B comparison
│   ├── fase3_retrieval_vs_generation.md  Oracle test + error classification
│   ├── error_profile_*.md                E01–E07 per-pipeline profiles
│   ├── oracle_comparison_*.md            Retrieval vs oracle comparisons
│   └── benchmark_results_*.md            Per-pipeline score tables
└── requirements.txt
```

## Requirements

- Python 3.10+
- 4GB+ RAM (for sentence-transformers on CPU)
- For local inference: LM Studio or Ollama on localhost with an OpenAI-compatible endpoint
- For cloud inference: Google Gemini API key (free tier: Gemma 4 26B, 15 RPM, 1500 RPD)
- No GPU required

## License

MIT
