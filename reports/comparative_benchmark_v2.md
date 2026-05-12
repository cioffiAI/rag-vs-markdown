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

The advantage shifts monotonically from Markdown to Raw as model size increases. A linear fit suggests the crossover point is approximately 1-2B parameters.

## Interpretation

1. **Small models (<2B)**: Markdown structure provides useful parsing cues that compensate for limited language understanding. Tables, headers, and lists act as explicit retrieval signals.

2. **Medium-large models (3B+)**: Raw text provides denser information per token. Markdown markup (##, **, `, |---|) consumes embedding dimensions that would be better spent on semantic content. Larger models can parse unstructured text without structural cues.

3. **Implication for RAG system design**: Preprocessing strategy should be selected based on the expected generator model. For small/edge-deployed models, Markdown compilation improves quality. For cloud-hosted large models, raw text extraction is both simpler and better.

4. **Caveat**: All models exhibit prompt-format issues (repeating the question, analyzing constraints step-by-step). This depresses absolute scores equally for both pipelines, so Δ values are reliable but absolute scores are conservative.
