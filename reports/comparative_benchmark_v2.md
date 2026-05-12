# Comparative Benchmark — 4-Model Results (Fase 4)

## Model × Pipeline Interaction Gradient

| Model | Size | Pipeline A (Raw) | Pipeline B (MD) | Δ (B−A) | Prefers |
|-------|------|:---:|:---:|:---:|---------|
| Qwen 0.8B | 800M | 2.50 | **2.56** | **+0.06** (+1.2%) | Markdown |
| Nemotron 3 Super Free | ~3B | **2.46** | 2.28 | −0.18 (−3.6%) | Raw |
| DeepSeek V4 Flash | — | **2.98** | 2.76 | −0.22 (−4.4%) | Raw |
| Gemma 4 26B A4B | 26B | **3.12** | 2.86 | −0.26 (−5.2%) | Raw |

## Individual Per-Model Results

### Qwen 0.8B
- Provider: LM Studio (local)
- A = 2.50/5.0, B = 2.56/5.0
- Markdown advantage driven by table extraction (+1.60)
- First model tested (Fase 1)

### Nemotron 3 Super Free
- Provider: OpenCode API (opencode.ai/zen/v1)
- A = 2.46/5.0, B = 2.28/5.0
- Δ = −0.18 (−3.6%) — Raw advantage
- Verbose "We need to answer..." preamble depresses scores
- High refusal rate, including for answerable questions

### DeepSeek V4 Flash
- Provider: OpenCode API (opencode.ai/zen/go/v1)
- A = 2.98/5.0, B = 2.76/5.0
- Δ = −0.22 (−4.4%) — Raw advantage
- Best performing model on Pipeline A after Gemma 4
- Reasoning model — generates "Thinking..." preamble before answering
- Required max_tokens=1024 to produce complete answers (reasoning + response)

### Gemma 4 26B A4B
- Provider: Google Gemini API (free tier)
- A = 3.12/5.0, B = 2.86/5.0
- Δ = −0.26 (−5.2%) — Largest Raw advantage
- Source of E06 (false_refusal) — 42-46% of questions even with correct chunk retrieved
- Best overall scores but most expensive in token usage

## Gradient Visualization

```
Markdown advantage
    ∆ +0.06  █ Qwen 0.8B (800M)
    ------------ zero line ------------
    ∆ -0.18  █ Nemotron 3 (~3B)
    ∆ -0.22  █ DeepSeek V4 Flash
    ∆ -0.26  █ Gemma 4 26B (26B)
Raw advantage
```

The advantage shifts monotonically from Markdown to Raw as model size increases, but **model identity, provider, API format, and prompt formatting co-vary**. A linear fit on size alone suggests a crossover near 1–2B parameters, but this is a confounded estimate — replication on a single provider with controlled size variation (e.g., Llama 3 1B vs 8B vs 70B via the same API) would be needed to confirm.

## Chunk Size Note

The nominal CHUNK_SIZE=1500 is a paragraph-preserving closing threshold, not a hard limit. Single paragraphs exceeding 1500 chars are stored as standalone chunks of arbitrary length; accumulations of small paragraphs can also exceed 1500 before the next paragraph triggers closure. Average chunk lengths for Pipeline A are ~3100 chars, for Pipeline B ~3500 chars. This is by design: paragraph boundaries are semantic units, and splitting them would fragment section headers, table rows, and list items that Markdown preprocessing depends on.

## Proposed Mechanism: Shallow Chunks

A **shallow chunk** is defined as a retrieved chunk whose informative text content (stripped of Markdown syntax tokens: `#`, `*`, `` ` ``, `|`, `---`, `[`, `]`, `>`) is ≤200 characters. In our corpus, **26% of Pipeline B retrieved chunks (39/150)** are shallow vs. **0% for Pipeline A**. Examples:

- Shallow chunk from B: `# 03_attention_transformer_vaswani_2017.pdf` — a heading-only chunk matched via lexical overlap on "Transformer" in the query, with zero factual content.
- Corresponding A chunk at same position: `The attention mechanism computes weighted sums of values...` — a content-dense paragraph.

The embedding model normalizes vectors to unit length, so these shallow chunks compete on equal footing with substantive chunks. The structural words that make Markdown headings informative for human readers become **embedding false positives** in cosine retrieval, diluting the quality of the top-3 context window.

## Interpretation

1. **Small models (<2B)**: Markdown structure may provide useful parsing cues that compensate for limited language understanding. Tables, headers, and lists act as explicit retrieval signals, and the model's inability to exploit dense raw text makes the shallow-chunk penalty less severe.

2. **Medium-large models (3B+)**: Raw text provides denser information per token. The shallow-chunk problem (26% of retrieved MD chunks are near-empty) outweighs any structural benefit. Larger models can parse unstructured text without structural cues, so Markdown's cost (wasted embedding budget on headers) dominates.

3. **Implication for RAG system design**: Preprocessing strategy should be selected based on the expected generator model. For small/edge-deployed models, Markdown compilation may improve quality. For larger models, raw text extraction is both simpler and better — unless shallow chunks are filtered out of the Markdown pipeline (e.g., minimum-content threshold).

4. **Major caveat**: All models differ in provider, API, and prompt formatting. The gradient correlates with size but is confounded. For practical RAG design, this means: test your preprocessing with your target model before committing.

5. **Minor caveat**: All models exhibit prompt-format issues (repeating the question, analyzing constraints step-by-step). This depresses absolute scores equally for both pipelines, so Δ values are reliable but absolute scores are conservative.
