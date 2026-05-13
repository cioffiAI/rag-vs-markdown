# Corpus Expansion Report — Fase 6

*Generated: 2026-05-13*
*Model: Gemma 3 4B (Ollama) | Embedder: all-MiniLM-L6-v2 | Threshold: 200 (Pipeline C)*

---

## Summary

The corpus was expanded from 10 to 20 documents and from 50 to 75 questions. This report compares results before and after expansion to test robustness.

## Corpus Growth

| Metric | Before (Fase 2-3) | After (Fase 6) | Change |
|--------|:-:|:-:|:-:|
| Documents | 10 | 20 | +10 |
| Real papers | 10 | 15 | +5 |
| Synthetic papers | 0 | 5 | +5 |
| Benchmark questions | 50 | 75 | +25 |
| Chunks (Pipeline A) | ~553 | 633 | +80 |
| Chunks (Pipeline B) | ~553 | 664 | +111 |
| Chunks (Pipeline C) | ~544 | 647 | +103 |

## New Documents

### Real Papers (arXiv, <50 citations)

| ID | Paper | Source |
|:--:|-------|--------|
| 11 | REPLUG: Retrieval-Augmented Black-Box Language Models (Shi et al., 2023) | arXiv:2301.12652 |
| 12 | HyDE: Precise Zero-Shot Dense Retrieval without Relevance Labels (Gao et al., 2022) | arXiv:2212.10496 |
| 13 | RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval (Sarthi et al., 2024) | arXiv:2401.18059 |
| 14 | In-Context RALM (Ram et al., 2023) | arXiv:2304.03442 |
| 15 | LLM-Augmenter (Peng et al., 2023) | arXiv:2302.00093 |

### Synthetic Papers (invented facts)

| ID | Title | Topic |
|:--:|-------|-------|
| 16 | Zorvian Retrieval Protocol | Cross-dimensional embedding alignment |
| 17 | Neuro-Symbolic Index Fusion | Differentiable rule injection for RAG |
| 18 | Quantum Embedding Projection | Hilbert space orthogonal embeddings |
| 19 | Temporal RAG | Time-aware retrieval augmentation |
| 20 | Adversarial Chunk Filtering | Learned shallow chunk suppression |

## New Questions (Q051-Q075)

| Range | Count | Types | Documents |
|-------|:-----:|-------|-----------|
| Q051-Q063 | 13 | 5 simple, 3 local, 3 multi, 1 table, 1 negative | Real papers (11-15) |
| Q064-Q075 | 12 | 3 simple, 2 local, 2 multi, 1 table, 4 negative | Synthetic papers (16-20) |

## Overall Scores: 75 Questions

| Pipeline | Mean Score | vs Baseline (50q) |
|----------|:----------:|:-----------------:|
| **A (Raw)** | **2.31** | — |
| **B (Markdown)** | **2.18** | — |
| **C (MD-filtered)** | **2.13** | — |

## Bootstrap Results (75 questions, 5000 resamples, 95% CI)

| Comparison | n | Delta | CI 95% | p-value |
|------------|:-:|:-----:|:------:|:-------:|
| Raw (A) vs Markdown (B) | 75 | +0.127 | [-0.147, +0.400] | 0.389 |
| Raw (A) vs MD-filtered (C) | 75 | +0.180 | [-0.093, +0.453] | 0.214 |
| Markdown (B) vs MD-filtered (C) | 75 | +0.053 | [-0.127, +0.240] | 0.645 |

## Comparison: Before vs After Expansion

| Metric | Before (50q) | After (75q) | Delta |
|--------|:-----------:|:-----------:|:-----:|
| A (Raw) mean | 2.35 | 2.31 | -0.04 |
| B (Markdown) mean | 2.05 | 2.18 | +0.13 |
| C (MD-filtered) mean | 2.19 | 2.13 | -0.06 |
| Δ A-B | +0.30 | +0.13 | -0.17 |
| Δ A-C | +0.16 | +0.18 | +0.02 |
| Δ B-C | -0.14 | +0.05 | +0.19 |
| Shallow chunks filtered | 9/553 (1.6%) | 17/664 (2.6%) | +1.0pp |

## Analysis

1. **Raw advantage persists but narrows**: The Raw (A) > Markdown (B) advantage drops from Δ=+0.30 to Δ=+0.13 on the expanded corpus. Neither result is statistically significant (p=0.061 before, p=0.389 after).

2. **Pipeline C (shallow filter) shows no benefit on expanded corpus**: Unlike the original corpus where C slightly improved over B, on the expanded corpus C is slightly worse (Δ B-C = +0.05, p=0.645). This may be because the new synthetic documents (created directly as Markdown) have fewer shallow structural artifacts.

3. **Negative question performance varies**: The synthetic negative questions (Q072-Q075) test whether the model correctly declines to answer questions about information not present in the documents. Performance on these questions was mixed — some were correctly declined while others produced false answers by drawing from parametric knowledge.

4. **Synthetic paper questions are harder**: Questions about invented papers (16-20) often received lower scores because the LLM's parametric knowledge conflicts with the document content. This is expected and validates the synthetic paper approach for testing retrieval reliance.

## Limitations

- Only 1 model tested on expanded corpus (Gemma 3 4B). Other models may show different patterns.
- Synthetic papers are short (1-4 pages) and may not produce enough chunks in the pipeline.
- The 25 new questions have not been manually validated as thoroughly as the original 50.
- Pipeline C shallow threshold (200 chars) was not re-tuned for the expanded corpus.
