# Benchmark Results

## Setup
- **LLM**: Qwen 3.5 0.8B via LM Studio (temp=0.1, max_tokens=256)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector DB**: ChromaDB (cosine distance)
- **Retrieval**: TOP_K = 3 chunks
- **Chunk size**: 1500 chars, 150 overlap
- **Questions**: 50 gold-standard (15 simple, 10 local reasoning, 10 multi-doc, 5 table extraction, 10 negative)

## Overall Score

| Pipeline | Mean (/5.0) | Normalized |
|----------|:-----------:|:----------:|
| **B — Markdown** | **2.56** | **51.2%** |
| **A — Raw text** | **2.50** | **50.0%** |
| Delta | +0.06 | +1.2% |

## By Question Type

| Type | B (Markdown) | A (Raw) | Delta |
|------|:-----------:|:-------:|:-----:|
| Table extraction | **3.60** | 2.00 | **+1.60** |
| Local reasoning | **2.55** | 2.30 | +0.25 |
| Negative | 2.25 | 2.25 | 0.00 |
| Multi-document | 2.70 | **3.05** | -0.35 |
| Simple factual | 2.33 | **2.60** | -0.27 |

## Key Findings

### Markdown wins on tables
Questions requiring table data (BLEU scores, COCO AP, ablation studies) scored significantly higher with Markdown (+1.6 points). The structured table format preserves numeric relationships that raw PDF text flattens.

### Raw text is competitive on facts
For simple factual questions and multi-document comparisons, raw PDF text sometimes performs slightly better. The Markdown compilation can occasionally introduce noise through heuristic header detection.

### Negative questions are identical
Both pipelines correctly declined ~70% of trap questions. The LLM's ability to detect "not in documents" is independent of chunk formatting.

### LLM quality is the bottleneck
With a 0.8B model, chunk formatting differences are dwarfed by the model's limited reasoning and paraphrasing ability. Both pipelines suffer from:
- Inaccurate paraphrasing of retrieved content
- Incomplete answers (missing key points)
- Occasional hallucinations on ambiguous queries

## Best Performing Questions (B, 4/5)

| ID | Topic |
|:--:|-------|
| Q001 | RAG-Sequence vs RAG-Token formulation |
| Q006 | Transformer encoder sub-layers |
| Q012 | Ragas metrics (faithfulness, relevance) |
| Q017 | Self-RAG retrieval/critique tokens |
| Q019 | Scaled dot-product attention |
| Q029 | Self-RAG vs CRAG factuality approaches |
| Q031 | Evaluation metrics overlap (Chang vs Liang) |
| Q035 | Retrieval differences across RAG/CRAG |

## Worst Performing Questions (B, < 2/5)

| ID | Topic | Score | Issue |
|:--:|-------|:-----:|-------|
| Q008 | YOLOv7 backbone architecture | 1.0 | Hallucinated answer |
| Q014 | CRAG difficulty distribution | 1.0 | No context retrieved |
| Q023 | Ragas faithfulness calculation | 1.0 | Wrong document retrieved |
| Q044 | GPU used for HELM (trap) | 0.0 | Hallucinated GPU specs |

## Detailed Report
For per-question breakdown and raw scores, see `reports/comparative_benchmark.md`.
