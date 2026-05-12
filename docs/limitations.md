# Limitations

This document describes the known limitations of the benchmark and experimental framework. These do not weaken the project — they define its scope and make its claims falsifiable.

## 1. Model Size

All evaluations use **Qwen 3.5 0.8B** (800M parameters) running locally via LM Studio / Ollama.

- A larger model (4B+, 7B+) would likely produce more accurate paraphrasing and better handle multi-document synthesis.
- The reported scores (2.5–2.56/5.0) are primarily constrained by the LLM, not the retrieval pipeline.
- **This means**: the small gap between pipelines may widen or disappear with a stronger model. We cannot yet predict which.

## 2. Scoring Methodology

Evaluation uses **fuzzy word-overlap matching** (threshold 0.4) against manually written key points.

- This is a proxy metric that may not capture semantic equivalence.
- An LLM-as-judge approach (e.g., GPT-4 as evaluator) would be more robust but introduces its own biases.
- The composite score (0–5) conflates answer correctness, evidence citation, and hallucination detection into a single number. Two questions with the same total score may fail for entirely different reasons.
- **This means**: the mean score is useful for coarse comparison but hides important variation. The [error taxonomy](error_taxonomy.md) is designed to address this.

## 3. The Benchmark Conflates Retrieval and Generation

The current evaluation pipeline does not separate these two failure modes:

- A low score could mean the retriever failed to find the right document.
- A low score could mean the retriever found the right document but the LLM failed to use it.
- A medium score could mean the LLM answered correctly using parametric knowledge despite poor retrieval.

**This is the most important methodological limitation.** Oracle-context testing (giving the LLM the correct passage directly) would be needed to attribute errors correctly.

## 4. Corpus Is Composed of Famous Papers

All 10 documents are well-known arXiv papers (RAG, Transformer, HELM, Self-RAG, YOLOv7, etc.).

- A model with strong parametric knowledge (e.g., GPT-4, Llama 3 70B) may answer questions about these papers correctly **without using the retrieved context**.
- This makes it harder to distinguish genuine RAG success from parametric knowledge leakage.
- **Mitigation**: negative questions partially control for this, and future benchmarks should include synthetic documents or less-cited papers.

## 5. Knowledge Compilation Is an Interpretive Act

Converting PDF to Markdown (`compile_markdown.py`) is not a neutral technical transformation. It involves decisions that affect retrieval and generation:

| Decision | Impact |
|----------|--------|
| Which lines become `## headers` | Changes chunk boundaries and embedding alignment |
| Which table markers are preserved | Determines whether table data is retrievable |
| How sections are identified | Can merge or split conceptually related content |
| What artifacts are removed | May lose metadata or marginalia |

**This means**: the Markdown pipeline implicitly encodes a theory of what information matters. A different compilation strategy would produce different results.

## 6. Benchmark Size and Scope

- 10 documents, 50 questions, single language (Italian queries, English LLM).
- No out-of-distribution testing (e.g., tables from different domains, noisy scans, handwritten notes).
- Single embedding model (all-MiniLM-L6-v2). A different embedding model may interact differently with chunk formatting.
- Single chunking strategy (paragraph-based, 1500 chars). Results may change with semantic chunking or smaller/larger windows.

Statistical significance is limited. A replication with more questions and documents would be needed to confirm the observed patterns.

## 7. CPU-Only Embeddings

Sentence embeddings are computed on CPU (~2 minutes for 550 chunks). This is acceptable for development but would not scale to production corpora (10k+ documents). GPU acceleration would change the cost/benefit tradeoff of chunk size and overlap tuning.

## 8. No Ground-Truth for Table Parsing

Table extraction questions are evaluated through the same chunking pipeline as text passages. No dedicated table parser (Camelot, Tabula, pdfplumber) is used. Table QA performance could likely be improved by row-level or cell-level retrieval, independent of the Markdown-vs-raw choice.

## 9. Pipeline C Not Implemented

The research plan included a third pipeline (Markdown + conceptual knowledge cards). This pipeline could improve performance on reasoning and synthesis questions but also introduces risks (interpreter bias in card generation, increased complexity).

## 10. Single LLM Provider

All experiments use Qwen 3.5 via LM Studio with an OpenAI-compatible API. Prompt formatting, system prompt style, and tokenizer behavior may vary across providers (LM Studio vs. Ollama vs. cloud). The system prompt ("use ONLY the provided context") is enforced by instruction, not architecture — a different model may follow it differently.

## Summary of Threats to Validity

| Threat | Severity | Mitigation |
|--------|----------|------------|
| Conflated retrieval/generation | High | Oracle test (planned, Fase 3) |
| Famous papers bias | Medium | Synthetic docs (planned, Fase 4) |
| Scoring proxy | Medium | Error taxonomy (added) |
| Small benchmark | Medium | Future expansion |
| Single model | High | Multi-model benchmark (planned, Fase 2) |
| Knowledge compilation bias | Medium | Explicitly documented here |
