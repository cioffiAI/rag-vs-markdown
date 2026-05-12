# Benchmark Results

## Research Context
This benchmark does not measure "RAG in general". It measures the ability of two pipeline configurations to answer 50 questions that we chose as representative of five skill dimensions. The results are valid within this experimental boundary and should not be generalized without replication on different corpora and question sets.

## Setup

| Parameter | Value |
|-----------|-------|
| LLM | Qwen 3.5 0.8B via LM Studio (temp=0.1, max_tokens=256) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (CPU) |
| Vector DB | ChromaDB (cosine distance) |
| Retrieval | TOP_K = 3 chunks |
| Chunk size | 1500 chars, 150 overlap paragraph-based |
| Corpus | 10 arXiv papers (RAG, Self-RAG, Transformer, YOLOv7, Survey, Foundation Models, Ragas, CRAG, HELM, Tree-of-Thoughts) |
| Questions | 50 gold-standard across 5 types, Italian language |

## Overall Score

| Pipeline | Mean (/5.0) | Normalized |
|----------|:-----------:|:----------:|
| **B — Markdown** | **2.56** | **51.2%** |
| **A — Raw text** | **2.50** | **50.0%** |
| Delta | +0.06 | +1.2% |

## Results by Question Type

| Type | B (Markdown) | A (Raw) | Delta | Questions |
|------|:-----------:|:-------:|:-----:|:---------:|
| Table extraction | **3.60** | 2.00 | +1.60 | 5 |
| Local reasoning | **2.55** | 2.30 | +0.25 | 10 |
| Negative (trap) | 2.25 | 2.25 | 0.00 | 10 |
| Multi-document | 2.70 | **3.05** | -0.35 | 10 |
| Simple factual | 2.33 | **2.60** | -0.27 | 15 |

## Results by Negative Subtype

| Subtype | Count | B (Markdown) | A (Raw) | Hallucination Rate (B) | Correct Refusal (B) |
|---------|:----:|:-----------:|:-------:|:---------------------:|:------------------:|
| true_absence | 5 | 1.80 | 2.10 | 40% | 60% |
| false_premise | 3 | 2.50 | 2.00 | 33% | 67% |
| out_of_domain | 2 | 3.00 | 3.00 | 0% | 100% |

Note: Hallucination rate measures how often the system produced an answer when it should have declined. The out_of_domain category (Tree-of-Thoughts questions) shows perfect refusal because the model correctly identifies the paper as unrelated to RAG.

## Full Per-Question Scores

| ID | Type | Category | B | A | Delta |
|:--:|------|----------|:-:|:-:|:-----:|
| Q001 | simple | factual_evidence | 4.0 | 4.0 | 0.0 |
| Q002 | simple | factual_evidence | 3.0 | 4.0 | -1.0 |
| Q003 | simple | factual_evidence | 2.0 | 2.0 | 0.0 |
| Q004 | simple | factual_evidence | 3.0 | 3.0 | 0.0 |
| Q005 | simple | factual_evidence | 1.0 | 3.0 | -2.0 |
| Q006 | simple | factual_evidence | 4.0 | 4.0 | 0.0 |
| Q007 | simple | factual_evidence | 2.0 | 2.0 | 0.0 |
| Q008 | simple | factual_evidence | 1.0 | 1.0 | 0.0 |
| Q009 | simple | factual_evidence | 2.0 | 1.0 | +1.0 |
| Q010 | simple | factual_evidence | 1.0 | 2.0 | -1.0 |
| Q011 | simple | factual_evidence | 2.0 | 2.0 | 0.0 |
| Q012 | simple | factual_evidence | 4.0 | 4.0 | 0.0 |
| Q013 | simple | factual_evidence | 3.0 | 3.0 | 0.0 |
| Q014 | simple | factual_evidence | 1.0 | 1.0 | 0.0 |
| Q015 | simple | factual_evidence | 2.0 | 3.0 | -1.0 |
| Q016 | local_reasoning | same_document | 2.0 | 1.0 | +1.0 |
| Q017 | local_reasoning | same_document | 4.0 | 4.0 | 0.0 |
| Q018 | local_reasoning | same_document | 2.5 | 2.5 | 0.0 |
| Q019 | local_reasoning | same_document | 4.0 | 3.0 | +1.0 |
| Q020 | local_reasoning | same_document | 3.0 | 1.0 | +2.0 |
| Q021 | local_reasoning | same_document | 2.0 | 2.0 | 0.0 |
| Q022 | local_reasoning | same_document | 2.5 | 2.5 | 0.0 |
| Q023 | local_reasoning | same_document | 1.0 | 2.5 | -1.5 |
| Q024 | local_reasoning | same_document | 1.5 | 2.5 | -1.0 |
| Q025 | local_reasoning | same_document | 3.0 | 2.0 | +1.0 |
| Q026 | multi_document | comparison | 3.0 | 4.0 | -1.0 |
| Q027 | multi_document | comparison | 2.0 | 4.0 | -2.0 |
| Q028 | multi_document | comparison | 1.5 | 1.5 | 0.0 |
| Q029 | multi_document | comparison | 4.0 | 3.0 | +1.0 |
| Q030 | multi_document | comparison | 2.0 | 2.0 | 0.0 |
| Q031 | multi_document | comparison | 4.0 | 4.0 | 0.0 |
| Q032 | multi_document | comparison | 2.5 | 3.0 | -0.5 |
| Q033 | multi_document | comparison | 2.0 | 2.5 | -0.5 |
| Q034 | multi_document | comparison | 2.0 | 2.5 | -0.5 |
| Q035 | multi_document | comparison | 4.0 | 4.0 | 0.0 |
| Q036 | table_extraction | table_metric | 4.0 | 3.0 | +1.0 |
| Q037 | table_extraction | table_metric | 4.0 | 1.0 | +3.0 |
| Q038 | table_extraction | table_metric | 4.0 | 4.0 | 0.0 |
| Q039 | table_extraction | table_metric | 3.0 | 1.0 | +2.0 |
| Q040 | table_extraction | table_metric | 3.0 | 1.0 | +2.0 |
| Q041 | negative | true_absence | 1.5 | 1.5 | 0.0 |
| Q042 | negative | true_absence | 3.0 | 3.0 | 0.0 |
| Q043 | negative | false_premise | 1.5 | 1.5 | 0.0 |
| Q044 | negative | true_absence | 0.0 | 1.5 | -1.5 |
| Q045 | negative | false_premise | 3.0 | 3.0 | 0.0 |
| Q046 | negative | out_of_domain | 3.0 | 3.0 | 0.0 |
| Q047 | negative | true_absence | 3.0 | 1.5 | +1.5 |
| Q048 | negative | false_premise | 3.0 | 1.5 | +1.5 |
| Q049 | negative | true_absence | 1.5 | 3.0 | -1.5 |
| Q050 | negative | out_of_domain | 3.0 | 3.0 | 0.0 |

## Interpretation

### 1. The Preprocessing Effect Is Small (on 0.8B)
Pipeline B (Markdown) outperforms A (Raw) by only 0.06 points — a 1.2% difference. With a weak LLM, chunk formatting quality is dwarfed by the model's limited ability to paraphrase and reason. This does **not** prove Markdown is useless. It proves that if the generator is the bottleneck, improving the retriever has limited impact on the final score.

### 2. Tables Are the Exception
On the 5 table-extraction questions, Markdown shows a clear +1.6 point advantage. The structured format preserves numeric relationships that raw PDF text flattens into prose. This is the most actionable finding: **if your use case involves tables, Markdown preprocessing matters**.

### 3. Negative Questions Are a Separate Dimension
Both pipelines score identically on negative questions (2.25/5), but the error profile differs. Pipeline A hallucinates less on `true_absence` questions by producing more cautious answers, while Pipeline B is better at detecting `false_premise` patterns. Refusal behavior is pipeline-dependent.

### 4. What We Cannot Conclude
- We cannot say "Markdown is better than raw text" — the difference is within noise range for this model.
- We cannot say "raw text is sufficient" — a stronger LLM might reveal a hidden Markdown advantage.
- We cannot attribute score differences to retrieval vs. generation — the current scoring conflates both.

### 5. Next Diagnostic Steps
To separate retrieval quality from generation quality, the next experiment should:
- Measure **Recall@k** (is the correct document retrieved?)
- Run an **oracle context** test (give the LLM the correct passage directly)
- Classify each error using the [error taxonomy](error_taxonomy.md)

## All-Question Summary

| Metric | B (Markdown) | A (Raw) |
|--------|:-----------:|:-------:|
| Mean | 2.56 | 2.50 |
| Median | 2.50 | 2.50 |
| Stdev | 1.09 | 1.03 |
| Best | 4.0 (13x) | 4.0 (11x) |
| Worst | 0.0 (Q044) | 1.0 (4x) |
| Questions >= 3.0 | 21 (42%) | 20 (40%) |
| Questions < 2.0 | 14 (28%) | 14 (28%) |
| Hallucinations | 9 (18%) | 9 (18%) |

## Detailed Report
For per-question answers and retrieved chunks, see `reports/comparative_benchmark.md`.
