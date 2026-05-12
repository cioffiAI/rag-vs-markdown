# RAG vs Markdown: Local Evidence Benchmark

**Does compiling PDFs into structured Markdown before indexing improve RAG quality?**

This project is not a RAG demo. It is a **diagnostic framework** to separate the effects of document preprocessing, retrieval, generation, and epistemic behavior (knowing when not to answer) in local RAG pipelines.

## Research Questions

| ID | Question | Status |
|----|----------|--------|
| RQ1 | Does Markdown compilation improve overall quality vs. raw PDF text? | Baseline measured (Δ = +1.2%) |
| RQ2 | Does the Markdown advantage persist with stronger generative models? | Planned (Fase 2) |
| RQ3 | Are errors primarily caused by retrieval failures or generation failures? | Planned (Fase 3) |

## Pipelines

```
Pipeline A (Raw)   PDF → PyMuPDF → raw text → chunks → ChromaDB → retrieve → LLM
Pipeline B (MD)    PDF → PyMuPDF → raw text → Markdown → chunks → ChromaDB → retrieve → LLM
```

| Pipeline | Description | Embeddings | Vector DB | LLM |
|----------|-------------|-----------|-----------|-----|
| **A** | Raw extracted text | all-MiniLM-L6-v2 | ChromaDB (cosine) | Configurable |
| **B** | Compiled Markdown | all-MiniLM-L6-v2 | ChromaDB (cosine) | Configurable |

## Results at a Glance (Qwen 0.8B)

| Pipeline | Mean (/5.0) | Normalized |
|----------|:-----------:|:----------:|
| **B — Markdown** | **2.56** | **51.2%** |
| A — Raw text | 2.50 | 50.0% |
| Delta | +0.06 | +1.2% |

Markdown wins by 1.2%, driven entirely by table-extraction questions (+1.6). On all other types, pipelines are equivalent within noise (0.8B model).

See [docs/results.md](docs/results.md) and the [comparative report](reports/comparative_benchmark.md).

## Interpreting These Results

This benchmark does not measure "RAG in general". It measures the ability of two pipeline configurations to answer 50 questions we designed. The scores are valid within this boundary. Key constraints:

- **Small LLM**: Qwen 0.8B is the dominant bottleneck. A larger model could change the gap.
- **Conflated metrics**: The composite score mixes retrieval quality, generation quality, and citation accuracy. See the [error taxonomy](docs/error_taxonomy.md) for separation.
- **Famous papers**: All documents are well-known arXiv papers. A model with strong parametric knowledge may answer without using context.

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
│   ├── query.py                   Retrieve + LLM generation (--pipeline a|b)
│   ├── evaluate.py                Score answers against ground truth
│   ├── convert_benchmark_to_csv.py
│   └── compare_pipelines.py       A vs B comparison report
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
│   ├── benchmark_results_a.md     Pipeline A evaluation
│   ├── benchmark_results_b.md     Pipeline B evaluation
│   └── comparative_benchmark.md   Side-by-side comparison
└── requirements.txt
```

## Requirements

- Python 3.10+
- 4GB+ RAM (for sentence-transformers on CPU)
- LM Studio or Ollama on localhost with an OpenAI-compatible endpoint
- No GPU required

## License

MIT
