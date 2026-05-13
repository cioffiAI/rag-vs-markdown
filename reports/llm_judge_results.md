# LLM Judge vs Fuzzy Overlap — Confronto

*Generated: 2026-05-13T17:28:23.184936*

## Metodologia

- **Fuzzy overlap**: word-overlap (threshold 0.4) su key_points + document citation check + hallucination detection (scala 0-5).
- **LLM judge**: nemotron-3-super:cloud via Ollama, rubrica 0-5, temperature=0.
- **Correlazione**: Pearson e Spearman tra fuzzy_total e judge_score.

---

## Gemma 3 4B (4B)

### Pipeline Raw (A)

| Metrica | Valore |
|---------|-------:|
| N | 50 |
| Fuzzy mean | 2.29 / 5.0 |
| LLM judge mean | 2.08 / 5.0 |
| Delta (Judge − Fuzzy) | -0.21 |
| Pearson r | 0.2528 |
| Spearman rho | 0.2485 |

#### Per-type breakdown

| Type | N | Fuzzy mean | Judge mean | Delta |
|------|:-:|:----------:|:----------:|:-:|
| simple | 15 | 2.73 | 2.40 | -0.33 |
| local_reasoning | 10 | 2.40 | 2.60 | +0.20 |
| multi_document | 10 | 2.45 | 1.80 | -0.65 |
| table_extraction | 5 | 2.00 | 1.40 | -0.60 |
| negative | 10 | 1.50 | 1.70 | +0.20 |

### Pipeline Markdown (B)

| Metrica | Valore |
|---------|-------:|
| N | 50 |
| Fuzzy mean | 1.99 / 5.0 |
| LLM judge mean | 1.54 / 5.0 |
| Delta (Judge − Fuzzy) | -0.45 |
| Pearson r | 0.3156 |
| Spearman rho | 0.3153 |

#### Per-type breakdown

| Type | N | Fuzzy mean | Judge mean | Delta |
|------|:-:|:----------:|:----------:|:-:|
| simple | 15 | 2.00 | 1.47 | -0.53 |
| local_reasoning | 10 | 2.00 | 1.70 | -0.30 |
| multi_document | 10 | 2.40 | 1.50 | -0.90 |
| table_extraction | 5 | 1.80 | 2.40 | +0.60 |
| negative | 10 | 1.65 | 1.10 | -0.55 |

### Pipeline MD-filtered (C)

| Metrica | Valore |
|---------|-------:|
| N | 50 |
| Fuzzy mean | 2.16 / 5.0 |
| LLM judge mean | 1.46 / 5.0 |
| Delta (Judge − Fuzzy) | -0.70 |
| Pearson r | 0.4786 |
| Spearman rho | 0.4495 |

#### Per-type breakdown

| Type | N | Fuzzy mean | Judge mean | Delta |
|------|:-:|:----------:|:----------:|:-:|
| simple | 15 | 2.33 | 1.33 | -1.00 |
| local_reasoning | 10 | 1.90 | 1.50 | -0.40 |
| multi_document | 10 | 2.35 | 1.40 | -0.95 |
| table_extraction | 5 | 1.90 | 1.80 | -0.10 |
| negative | 10 | 2.10 | 1.50 | -0.60 |

## Nemotron 3 (~3B)

### Pipeline Raw (A)

| Metrica | Valore |
|---------|-------:|
| N | 50 |
| Fuzzy mean | 2.46 / 5.0 |
| LLM judge mean | 2.00 / 5.0 |
| Delta (Judge − Fuzzy) | -0.46 |
| Pearson r | -0.0142 |
| Spearman rho | -0.0161 |

#### Per-type breakdown

| Type | N | Fuzzy mean | Judge mean | Delta |
|------|:-:|:----------:|:----------:|:-:|
| simple | 15 | 2.80 | 2.73 | -0.07 |
| local_reasoning | 10 | 1.90 | 1.20 | -0.70 |
| multi_document | 10 | 2.55 | 1.90 | -0.65 |
| table_extraction | 5 | 3.10 | 2.00 | -1.10 |
| negative | 10 | 2.10 | 1.80 | -0.30 |

### Pipeline Markdown (B)

| Metrica | Valore |
|---------|-------:|
| N | 50 |
| Fuzzy mean | 2.28 / 5.0 |
| LLM judge mean | 1.14 / 5.0 |
| Delta (Judge − Fuzzy) | -1.14 |
| Pearson r | -0.0332 |
| Spearman rho | -0.0751 |

#### Per-type breakdown

| Type | N | Fuzzy mean | Judge mean | Delta |
|------|:-:|:----------:|:----------:|:-:|
| simple | 15 | 2.07 | 1.27 | -0.80 |
| local_reasoning | 10 | 1.95 | 1.10 | -0.85 |
| multi_document | 10 | 2.70 | 1.20 | -1.50 |
| table_extraction | 5 | 3.10 | 0.80 | -2.30 |
| negative | 10 | 2.10 | 1.10 | -1.00 |

### Pipeline MD-filtered (C)

| Metrica | Valore |
|---------|-------:|
| N | 50 |
| Fuzzy mean | 2.37 / 5.0 |
| LLM judge mean | 1.76 / 5.0 |
| Delta (Judge − Fuzzy) | -0.61 |
| Pearson r | -0.0008 |
| Spearman rho | -0.0613 |

#### Per-type breakdown

| Type | N | Fuzzy mean | Judge mean | Delta |
|------|:-:|:----------:|:----------:|:-:|
| simple | 15 | 2.40 | 2.20 | -0.20 |
| local_reasoning | 10 | 2.05 | 1.80 | -0.25 |
| multi_document | 10 | 2.80 | 1.20 | -1.60 |
| table_extraction | 5 | 2.90 | 1.40 | -1.50 |
| negative | 10 | 1.95 | 1.80 | -0.15 |

## DeepSeek V4 Flash (—)

### Pipeline Raw (A)

| Metrica | Valore |
|---------|-------:|
| N | 50 |
| Fuzzy mean | 2.98 / 5.0 |
| LLM judge mean | 1.88 / 5.0 |
| Delta (Judge − Fuzzy) | -1.10 |
| Pearson r | 0.2224 |
| Spearman rho | 0.1954 |

#### Per-type breakdown

| Type | N | Fuzzy mean | Judge mean | Delta |
|------|:-:|:----------:|:----------:|:-:|
| simple | 15 | 3.13 | 1.87 | -1.27 |
| local_reasoning | 10 | 2.30 | 1.50 | -0.80 |
| multi_document | 10 | 3.10 | 2.00 | -1.10 |
| table_extraction | 5 | 3.60 | 1.60 | -2.00 |
| negative | 10 | 3.00 | 2.30 | -0.70 |

### Pipeline Markdown (B)

| Metrica | Valore |
|---------|-------:|
| N | 50 |
| Fuzzy mean | 2.76 / 5.0 |
| LLM judge mean | 1.56 / 5.0 |
| Delta (Judge − Fuzzy) | -1.20 |
| Pearson r | 0.3443 |
| Spearman rho | 0.3057 |

#### Per-type breakdown

| Type | N | Fuzzy mean | Judge mean | Delta |
|------|:-:|:----------:|:----------:|:-:|
| simple | 15 | 2.73 | 1.47 | -1.27 |
| local_reasoning | 10 | 2.30 | 1.30 | -1.00 |
| multi_document | 10 | 3.05 | 1.70 | -1.35 |
| table_extraction | 5 | 3.60 | 2.00 | -1.60 |
| negative | 10 | 2.55 | 1.60 | -0.95 |

### Pipeline MD-filtered (C)

| Metrica | Valore |
|---------|-------:|
| N | 50 |
| Fuzzy mean | 2.83 / 5.0 |
| LLM judge mean | 1.84 / 5.0 |
| Delta (Judge − Fuzzy) | -0.99 |
| Pearson r | 0.3253 |
| Spearman rho | 0.3223 |

#### Per-type breakdown

| Type | N | Fuzzy mean | Judge mean | Delta |
|------|:-:|:----------:|:----------:|:-:|
| simple | 15 | 2.93 | 1.53 | -1.40 |
| local_reasoning | 10 | 2.40 | 1.80 | -0.60 |
| multi_document | 10 | 2.95 | 2.10 | -0.85 |
| table_extraction | 5 | 3.40 | 2.20 | -1.20 |
| negative | 10 | 2.70 | 1.90 | -0.80 |

---

## Discrepanze annotate

- **Negative questions**: fuzzy overlap tends to score negative questions highly (correct decline = 3.0), but LLM judge may penalize answers that do not explicitly state 'not in the document'.
- **Table extraction**: fuzzy overlap may miss numerical precision while LLM judge evaluates correctness more holistically.
- **Multi-document**: LLM judge can verify cross-document synthesis better than word overlap, which only checks per-document key points.

## Limitazioni

- LLM judge uses nemotron-3-super:cloud, not a dedicated evaluator model.
- Judge prompt and rubric may introduce bias toward certain answer styles.
- Small sample size per type (3-15 questions).