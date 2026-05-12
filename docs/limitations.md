# Limitations

This document describes the known limitations of the benchmark and experimental framework. These do not weaken the project — they define its scope and make its claims falsifiable.

## 1. Model Size

The benchmark was run on **two models** with very different sizes:

| Model | Params | Source |
|-------|--------|--------|
| Qwen 3.5 0.8B | 800M | Local (LM Studio) |
| Gemma 4 26B A4B | ~4B active / 26B total | Google Gemini API (free tier) |

Key observations:
- Gemma 4 26B consistently outperforms Qwen across both pipelines (+25% on Pipeline A, +12% on Pipeline B).
- The pipeline advantage **reverses** between models: Qwen benefits from Markdown (+1.2%), Gemma 4 benefits from Raw (−5.2%).
- The retrieval bottleneck is common to both: the [oracle test](reports/fase3_retrieval_vs_generation.md) shows +67–85% improvement when giving full document context, regardless of model size.
- **This means**: model size alone doesn't predict which preprocessing strategy works. The interaction between model capability and chunk format is non-trivial.

## 2. Scoring Methodology

Evaluation uses **fuzzy word-overlap matching** (threshold 0.4) against manually written key points.

- This is a proxy metric that may not capture semantic equivalence.
- An LLM-as-judge approach (e.g., GPT-4 as evaluator) would be more robust but introduces its own biases.
- The composite score (0–5) conflates answer correctness, evidence citation, and hallucination detection into a single number. Two questions with the same total score may fail for entirely different reasons.
- **This means**: the mean score is useful for coarse comparison but hides important variation. The [error taxonomy](error_taxonomy.md) is designed to address this.

## 3. The Benchmark Conflates Retrieval and Generation

~~This limitation has been addressed by Fase 3.~~ See below.

The evaluation pipeline originally did not separate retrieval and generation failure modes. Fase 3 addressed this with:

1. **Oracle-context testing**: giving the LLM the full document text directly, bypassing the retriever, showed +67–85% score improvement. This quantifies the retrieval gap.
2. **Error taxonomy (E01–E07)**: each failed answer is classified by origin (retrieval → E01/E02, generation → E03/E04/E05/E06, scoring → E07).

Result: **~60% of errors are retrieval-related, ~25% generation-related, ~15% scoring/citation artifacts.** The oracle test is documented in [reports/fase3_retrieval_vs_generation.md](reports/fase3_retrieval_vs_generation.md) and the [error taxonomy](error_taxonomy.md).

**Remaining limitation**: the oracle test uses raw extracted text (not Markdown), so it may slightly under/overestimate the retrieval gap for Pipeline B. A per-pipeline oracle would be more precise but was not run due to API rate limits.

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

## 10. LLM Provider Diversity

Experiments use two providers:
- **Qwen 3.5 0.8B** via LM Studio (local, OpenAI-compatible API) — for the Fase 1 baseline.
- **Gemma 4 26B A4B** via Google Gemini API (free tier, direct HTTP) — for Fase 2 multi-model comparison and Fase 3 oracle test.

Prompt formatting, system prompt style, and tokenizer behavior differ across providers. Notably, Gemma 4 shows a **prompt-format issue**: it systematically repeats the question and analyzes constraints step-by-step before answering, which depresses word-overlap-based scores. This affects both retrieval and oracle results equally, so the retrieval-vs-generation comparison remains valid.

The system prompt ("use ONLY the provided context") is enforced by instruction, not architecture. A model with different instruction-following characteristics may behave differently.

## Summary of Threats to Validity

| Threat | Severity | Mitigation |
|--------|----------|------------|
| Conflated retrieval/generation | ~~High~~ **Resolved** | Oracle test + error taxonomy (Fase 3) |
| Famous papers bias | Medium | Synthetic docs (planned, Fase 4) |
| Scoring proxy | Medium | Error taxonomy (added) |
| Small benchmark | Medium | Future expansion |
| Single model | ~~High~~ **Resolved** | Multi-model benchmark (Fase 2) |
| Knowledge compilation bias | Medium | Explicitly documented here |
