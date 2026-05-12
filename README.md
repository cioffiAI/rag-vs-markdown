# RAG vs Markdown: Local Evidence Benchmark

**Does compiling PDFs into structured Markdown before indexing improve RAG quality?**

This project compares two RAG pipelines on the same 50 gold-standard questions over 10 arXiv papers. All runs on CPU with a local LLM — no cloud API.

## Pipelines

```
Pipeline A (Raw)   PDF → PyMuPDF → raw text → chunks → ChromaDB → retrieve → LLM
Pipeline B (MD)    PDF → PyMuPDF → raw text → Markdown → chunks → ChromaDB → retrieve → LLM
```

| Pipeline | Description | Embeddings | Vector DB | LLM |
|----------|-------------|-----------|-----------|-----|
| **A** | Raw extracted text | all-MiniLM-L6-v2 | ChromaDB (cosine) | Qwen 3.5 0.8B |
| **B** | Compiled Markdown | all-MiniLM-L6-v2 | ChromaDB (cosine) | Qwen 3.5 0.8B |

## Results in 10 Seconds

| Pipeline | Score | Normalized |
|----------|:-----:|:----------:|
| **B — Markdown** | **2.56/5** | **51.2%** |
| A — Raw text | 2.50/5 | 50.0% |

**Markdown wins by +1.2%.** The advantage comes from table-structured questions (+1.6 points). For simple facts and multi-doc comparisons, both pipelines are equivalent — the small LLM (0.8B) dominates the error budget.

See [docs/results.md](docs/results.md) for the full breakdown and [docs/limitations.md](docs/limitations.md) for known constraints.

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
│   ├── build_index.py             Chunk → embed → ChromaDB
│   ├── query.py                   Retrieve + LLM generation
│   ├── evaluate.py                Score answers against ground truth
│   ├── convert_benchmark_to_csv.py
│   └── compare_pipelines.py       A vs B comparison report
├── data/
│   ├── raw/                       Input PDFs (not tracked)
│   ├── extracted/                 Per-page JSON (not tracked)
│   ├── processed/                 Markdown versions (not tracked)
│   ├── benchmark_questions.json  50 gold-standard questions
│   └── gold_questions.csv         CSV export
├── docs/
│   ├── results.md                 Accessible results summary
│   └── limitations.md             Known constraints
├── reports/
│   ├── benchmark_results_a.md     Pipeline A evaluation
│   ├── benchmark_results_b.md     Pipeline B evaluation
│   └── comparative_benchmark.md   Side-by-side comparison
└── requirements.txt
```

## Requirements

- Python 3.10+
- 4GB+ RAM (for sentence-transformers on CPU)
- LM Studio or Ollama running on localhost with Qwen 3.5 0.8B (or any OpenAI-compatible endpoint)
- No GPU required

## License

MIT
