# Limitations

## Model Size
All evaluations use **Qwen 3.5 0.8B** (800M parameters) running locally via LM Studio / Ollama. A larger model (7B+) would likely produce more accurate paraphrasing and better handle multi-document synthesis. The reported scores (2.5–2.56/5.0) are primarily constrained by the LLM, not the retrieval pipeline.

## Chunking Strategy
The project uses a simple **paragraph-based chunking** (1500 chars, 150 overlap). No semantic chunking, recursive splitting, or document-aware boundaries are applied. Tables embedded in paragraphs may be partially lost. A more sophisticated chunking strategy (e.g., recursive character splitter, section-aware) could improve retrieval quality.

## Retrieval: TOP_K = 3
Only the top 3 chunks are retrieved per query. Increasing this value (e.g., TOP_K = 5) could provide more context for complex questions, but would also require a larger LLM context window.

## Scoring Methodology
Evaluation uses **fuzzy word-overlap matching** (threshold 0.4) against manually written key points. This is a proxy metric and may not capture semantic equivalence. An LLM-as-judge approach (e.g., GPT-4 as evaluator) would be more robust.

- Answer correctness: scored 0–2 based on key-point overlap
- Evidence correctness: scored 0–2 based on document name citation
- Hallucination: scored 0–1 based on negation pattern detection

## Benchmark Size
- 10 arXiv papers
- 50 gold-standard questions (15 simple, 10 local reasoning, 10 multi-doc, 5 table extraction, 10 negative)
- Single language (Italian questions, English LLM)

A larger and more diverse benchmark would increase statistical significance.

## Pipeline C Not Implemented
The original research plan included a third pipeline (Markdown + conceptual knowledge cards). This pipeline could potentially improve performance on synthesis and reasoning questions.

## Embedding on CPU
Sentence embeddings are computed on CPU using `all-MiniLM-L6-v2`. While acceptable for 500+ chunks (~2 minutes), GPU acceleration would be needed for production-scale corpora.

## No Ground Truth for Tables
Table extraction questions rely on the same chunking as text passages. A dedicated table parser (e.g., Camelot, Tabula) with row-level retrieval could significantly improve table QA performance.
