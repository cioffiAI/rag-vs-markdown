# Benchmark Results

## Research Context
This benchmark does not measure "RAG in general". It measures the ability of two pipeline configurations to answer 50 questions that we chose as representative of five skill dimensions. The results are valid within this experimental boundary and should not be generalized without replication on different corpora and question sets.

## Setup

| Parameter | Value |
|-----------|-------|
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (CPU) |
| Vector DB | ChromaDB (cosine distance) |
| Retrieval | TOP_K = 3 chunks |
| Chunk size (nominal) | 1500 chars, 150 overlap, paragraph-preserving |
| Avg chunk length (A) | ~3100 chars (paragraphs kept intact; see note below) |
| Avg chunk length (B) | ~3500 chars |
| Corpus | 10 arXiv papers (RAG, Self-RAG, Transformer, YOLOv7, Survey, Foundation Models, Ragas, CRAG, HELM, Tree-of-Thoughts) |
| Questions | 50 gold-standard across 5 types, Italian language |
| Models tested | Gemma 3 4B (Ollama Cloud), Nemotron 3 Super Free (OpenCode API), DeepSeek V4 Flash (OpenCode API), Gemma 4 26B A4B (Google Gemini API) |

> **Note on chunk size vs. actual length**: CHUNK_SIZE=1500 is a **closing threshold**, not a hard limit. The chunker (`smart_chunk_text` in `build_index.py`) accumulates whole paragraphs into a buffer and closes it when the *next* paragraph would exceed 1500 chars. Single paragraphs longer than 1500 chars are emitted as standalone chunks of arbitrary length. Consequently, average chunk lengths (~3100–3500) exceed the nominal 1500. This is by design: paragraph boundaries are semantic units, and splitting them mid-paragraph would corrupt section headers, table rows, or list items that Markdown preprocessing relies on. The overlap (150 chars) ensures continuity across chunk boundaries.

## Overall Scores by Model

| Model | Size | Pipeline A (Raw) | Pipeline B (Markdown) | Pipeline C (MD-filtered) | Δ B−A | Δ C−B |
|-------|------|:---:|:---:|:---:|:---:|:---:|
| Gemma 3 4B | 4B | **2.29** | 1.99 | 2.16 | −0.30 (−6.0%) | +0.17 (+3.4%) |
| Nemotron 3 Super Free | ~3B | **2.46** | 2.28 | 2.37 | −0.18 (−3.6%) | +0.09 (+1.8%) |
| DeepSeek V4 Flash | — | **2.98** | 2.76 | 2.83 | −0.22 (−4.4%) | +0.07 (+1.4%) |
| Gemma 4 26B A4B | 26B | **3.12** | 2.86 | —* | −0.26 (−5.2%) | — |

\*Gemma 4 26B Pipeline C result unreliable due to Gemini API errors (18/50 HTTP 500).

**Key finding**: All models prefer Raw over Markdown. Pipeline C (shallow chunk filter) partially recovers the Markdown loss for all models tested.

## Results by Question Type — Gemma 3 4B (A/B/C)

| Type | A (Raw) | B (Markdown) | C (MD-filtered) | Count |
|------|:---:|:---:|:---:|:----:|
| Simple factual | 2.73 | 2.00 | 2.33 | 15 |
| Local reasoning | 2.40 | 2.00 | 1.90 | 10 |
| Multi-document | 2.45 | 2.40 | 2.35 | 10 |
| Table extraction | 2.00 | 1.80 | 1.90 | 5 |
| Negative (trap) | 1.50 | 1.65 | 2.10 | 10 |

## Interpretation

### 1. Markdown Consistently Hurts
Across all 4 models (4B to 26B), Pipeline B (Markdown) underperforms Pipeline A (Raw) by −3.6% to −6.0%. The shallow chunk mechanism — structural headers that produce embedding false positives — outweighs any structural benefit. Unlike our earlier results with Qwen 0.8B (which showed a small Markdown advantage), the replacement model Gemma 3 4B confirms the universal pattern.

### 2. Pipeline C Filtering Partially Recovers
Removing shallow chunks (chunks with ≤200 informative characters) improves scores over unfiltered Markdown for all models:
- Gemma 3 4B: +0.17 (+3.4%)
- Nemotron 3: +0.09 (+1.8%)
- DeepSeek V4 Flash: +0.07 (+1.4%)

The filter removed only 9 chunks (1.6% of the collection) but measurably improved retrieval quality, confirming the mechanism.

### 3. Negative Questions Are Pipeline-Dependent
Pipeline C shows the strongest negative-question performance (2.10) for Gemma 3 4B, suggesting that removing shallow chunks reduces false positives in retrieval for unanswerable questions. Raw text (1.50) is weakest on negative questions, while Markdown (1.65) sits in between.

### 4. Tables Are Not an Exception Anymore
Unlike Qwen 0.8B (which showed +1.60 on tables with Markdown), Gemma 3 4B shows Raw (2.00) slightly outperforming Markdown (1.80) on table extraction. This suggests the table advantage was model-specific rather than universal.

### 5. Shallow Chunks

The Markdown pipeline introduces a class of retrieval candidates we call **shallow chunks**: chunks whose informative text length (after stripping structural markup: `##`, `**`, `|--|`, list markers) is ≤200 characters. These chunks typically consist of:

- Section headers alone (e.g., `# 03_attention_transformer_vaswani_2017.pdf`)
- Short list items
- Table formatting artifacts (header separators like `|---|---|`)

In our corpus, **26% of retrieved Markdown chunks (39/150)** are shallow vs. **0% for Raw text**. The embedding model (all-MiniLM-L6-v2) matches these chunks to queries via **lexical overlap in structural words** (e.g., "Transformer", "Model", "Attention" in headers matching query keywords) — producing high cosine similarity scores despite near-zero factual content. This is the primary mechanism behind the Markdown disadvantage: Pipeline B retrieves more irrelevant chunks that pass the embedding filter.

**Formal definition**: A chunk is *shallow* if, after removing Markdown syntax tokens (`#`, `*`, `` ` ``, `|`, `---`, `[`, `]`, `>`) and trimming whitespace, the remaining text has ≤200 characters. This threshold captures chunks that contain only structural headings without substantive prose.

### 6. Oracle Test — Retrieval vs. Generation (Fase 3, Diagnostic)

The oracle test (giving the LLM the full document text instead of top-3 chunks) estimates an upper bound on the retrieval contribution:

| Test | Pipeline B Mean | Oracle Mean | Delta |
|------|:---:|:---:|:---:|
| Gemma 4 26B | 1.58 | **2.93** | **+1.35 (+85%)** |

**Interpretation**: The data are consistent with retrieval being the dominant performance constraint on this benchmark. However, the oracle test has three diagnostic limitations:

1. **Upper-bound only**: replacing retrieved chunks with the full document text eliminates retrieval error entirely, which is unrealistic for any production RAG system. The +67–85% improvement is a ceiling, not a typical gain.
2. **Single-context oracle**: both pipelines use the same raw-text oracle — a per-pipeline oracle (Markdown for B) would give a more precise comparison but was not run due to API rate limits.
3. **E06 ambiguity**: the primary failure mode is **E06 (false_refusal, 42–46%)**: the model says "cannot find information" even when the correct document was retrieved. The oracle test attributes this to retrieval *insufficiency* (correct passage ranked 4th+), but it may also reflect a generation-side over-cautiousness policy — the model refuses unless the answer is obvious. E06 sits at the retrieval–generation boundary.

**Bottom line**: ~60% of errors are plausibly retrieval-related, ~25% are generation-related, ~15% are scoring/citation artifacts. These proportions are diagnostic hints, not causal attributions.

The [error taxonomy](error_taxonomy.md) provides the full E01–E07 breakdown, and the [Fase 3 report](../reports/fase3_retrieval_vs_generation.md) has the complete analysis.

## Detailed Reports
- Gemma 3 4B A/B/C comparison: `reports/comparative_gemma4b.md`
- Gemma 4 26B comparison: `reports/comparative_benchmark.md`
- Pipeline C sensitivity sweep: `reports/pipeline_c_sensitivity.md`
- Comparative A/B/C (4 models): `reports/comparative_abc.md`
- Error profiles (E01–E07): `reports/error_profile_*.md`
- Oracle test comparison: `reports/oracle_comparison_*.md`
- Fase 3 synthesis: `reports/fase3_retrieval_vs_generation.md`
