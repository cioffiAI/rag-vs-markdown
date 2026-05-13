# Bootstrap & Permutation Test Results

*Generated: 2026-05-13T15:47:23.558807*
*Resamples: 10000 | Seed: 42 | CI: 95%*

## Raw vs Markdown  (Δ Raw-MD)

| Model | Size | Δ Raw-MD | CI 95% | p-value | n |
|-------|------|:-------:|:------:|:-------:|:-:|
| Gemma 3 4B | 4B | +0.30 | [+0.01, +0.59] | 0.059 | 50 |
| Nemotron 3 | ~3B | +0.18 | [-0.06, +0.44] | 0.190 | 50 |
| DeepSeek V4 Flash | — | +0.22 | [-0.05, +0.49] | 0.133 | 50 |
| Gemma 4 26B | 26B | +0.26 | [-0.03, +0.55] | 0.104 | 50 |

## Raw vs MD-filtered  (Δ Raw-MDf)

| Model | Size | Δ Raw-MDf | CI 95% | p-value | n |
|-------|------|:-------:|:------:|:-------:|:-:|
| Gemma 3 4B | 4B | +0.13 | [-0.20, +0.45] | 0.486 | 50 |
| Nemotron 3 | ~3B | +0.09 | [-0.15, +0.32] | 0.512 | 50 |
| DeepSeek V4 Flash | — | +0.15 | [-0.10, +0.40] | 0.295 | 50 |
| Gemma 4 26B † | 26B | +0.22 | [-0.08, +0.51] | 0.162 | 50 |

† Gemma 4 26B Pipeline C affected by Gemini API 500 errors (18/50 questions). Results diagnostic only.

## Markdown vs MD-filtered  (Δ MD-MDf)

| Model | Size | Δ MD-MDf | CI 95% | p-value | n |
|-------|------|:-------:|:------:|:-------:|:-:|
| Gemma 3 4B | 4B | -0.17 | [-0.47, +0.13] | 0.307 | 50 |
| Nemotron 3 | ~3B | -0.09 | [-0.30, +0.11] | 0.444 | 50 |
| DeepSeek V4 Flash | — | -0.07 | [-0.23, +0.07] | 0.445 | 50 |
| Gemma 4 26B † | 26B | -0.04 | [-0.25, +0.19] | 0.799 | 50 |

† Gemma 4 26B Pipeline C affected by Gemini API 500 errors (18/50 questions). Results diagnostic only.

---

## Per-Question Type Breakdown

### Raw vs Markdown

#### Gemma 3 4B (4B)

| Type | n | Δ | CI 95% | p-value |
|------|:-:|:---:|:------:|:-------:|
| simple | 15 | +0.73 | [+0.33, +1.20] | 0.015 |
| local_reasoning | 10 | +0.40 | [+0.10, +0.70] | 0.125 |
| multi_document | 10 | +0.05 | [-0.50, +0.65] | 1.000 |
| table_extraction | 5 | +0.20 | [-0.60, +1.20] | 1.000 |
| negative | 10 | -0.15 | [-1.05, +0.75] | 1.000 |

#### Nemotron 3 (~3B)

| Type | n | Δ | CI 95% | p-value |
|------|:-:|:---:|:------:|:-------:|
| simple | 15 | +0.73 | [+0.20, +1.33] | 0.065 |
| local_reasoning | 10 | -0.05 | [-0.40, +0.35] | 1.000 |
| multi_document | 10 | -0.15 | [-0.55, +0.25] | 0.653 |
| table_extraction | 5 | +0.00 | [+0.00, +0.00] | 1.000 |
| negative | 10 | +0.00 | [-0.45, +0.45] | 1.000 |

#### DeepSeek V4 Flash (—)

| Type | n | Δ | CI 95% | p-value |
|------|:-:|:---:|:------:|:-------:|
| simple | 15 | +0.40 | [-0.20, +1.00] | 0.318 |
| local_reasoning | 10 | +0.00 | [-0.30, +0.30] | 1.000 |
| multi_document | 10 | +0.05 | [-0.65, +0.80] | 1.000 |
| table_extraction | 5 | +0.00 | [-0.60, +0.60] | 1.000 |
| negative | 10 | +0.45 | [+0.00, +0.90] | 0.248 |

#### Gemma 4 26B (26B)

| Type | n | Δ | CI 95% | p-value |
|------|:-:|:---:|:------:|:-------:|
| simple | 15 | +0.87 | [+0.40, +1.40] | 0.009 |
| local_reasoning | 10 | -0.55 | [-1.50, +0.25] | 0.380 |
| multi_document | 10 | +0.10 | [-0.25, +0.50] | 0.751 |
| table_extraction | 5 | +0.30 | [+0.00, +0.90] | 1.000 |
| negative | 10 | +0.30 | [+0.00, +0.75] | 0.500 |

### Raw vs MD-filtered

#### Gemma 3 4B (4B)

| Type | n | Δ | CI 95% | p-value |
|------|:-:|:---:|:------:|:-------:|
| simple | 15 | +0.40 | [-0.07, +0.93] | 0.260 |
| local_reasoning | 10 | +0.50 | [+0.00, +1.10] | 0.248 |
| multi_document | 10 | +0.10 | [-0.40, +0.60] | 1.000 |
| table_extraction | 5 | +0.10 | [-0.60, +0.90] | 1.000 |
| negative | 10 | -0.60 | [-1.65, +0.45] | 0.432 |

#### Nemotron 3 (~3B)

| Type | n | Δ | CI 95% | p-value |
|------|:-:|:---:|:------:|:-------:|
| simple | 15 | +0.40 | [+0.13, +0.73] | 0.065 |
| local_reasoning | 10 | -0.15 | [-0.60, +0.35] | 0.629 |
| multi_document | 10 | -0.25 | [-0.70, +0.20] | 0.373 |
| table_extraction | 5 | +0.20 | [+0.00, +0.60] | 1.000 |
| negative | 10 | +0.15 | [-0.75, +0.90] | 1.000 |

#### DeepSeek V4 Flash (—)

| Type | n | Δ | CI 95% | p-value |
|------|:-:|:---:|:------:|:-------:|
| simple | 15 | +0.20 | [-0.40, +0.73] | 0.660 |
| local_reasoning | 10 | -0.10 | [-0.45, +0.25] | 0.809 |
| multi_document | 10 | +0.15 | [-0.45, +0.90] | 0.815 |
| table_extraction | 5 | +0.20 | [-0.40, +0.80] | 1.000 |
| negative | 10 | +0.30 | [+0.00, +0.75] | 0.500 |

#### Gemma 4 26B (26B)

| Type | n | Δ | CI 95% | p-value |
|------|:-:|:---:|:------:|:-------:|
| simple | 15 | +0.53 | [+0.20, +0.93] | 0.032 |
| local_reasoning | 10 | -0.30 | [-1.30, +0.65] | 0.628 |
| multi_document | 10 | -0.10 | [-0.50, +0.35] | 0.876 |
| table_extraction | 5 | +0.80 | [+0.00, +2.00] | 0.501 |
| negative | 10 | +0.30 | [+0.00, +0.75] | 0.500 |

### Markdown vs MD-filtered

#### Gemma 3 4B (4B)

| Type | n | Δ | CI 95% | p-value |
|------|:-:|:---:|:------:|:-------:|
| simple | 15 | -0.33 | [-0.67, +0.00] | 0.189 |
| local_reasoning | 10 | +0.10 | [-0.40, +0.80] | 1.000 |
| multi_document | 10 | +0.05 | [-0.15, +0.30] | 1.000 |
| table_extraction | 5 | -0.10 | [-0.30, +0.00] | 1.000 |
| negative | 10 | -0.45 | [-1.65, +0.75] | 0.622 |

#### Nemotron 3 (~3B)

| Type | n | Δ | CI 95% | p-value |
|------|:-:|:---:|:------:|:-------:|
| simple | 15 | -0.33 | [-0.87, +0.13] | 0.377 |
| local_reasoning | 10 | -0.10 | [-0.30, +0.00] | 1.000 |
| multi_document | 10 | -0.10 | [-0.25, +0.00] | 0.502 |
| table_extraction | 5 | +0.20 | [+0.00, +0.60] | 1.000 |
| negative | 10 | +0.15 | [-0.30, +0.60] | 1.000 |

#### DeepSeek V4 Flash (—)

| Type | n | Δ | CI 95% | p-value |
|------|:-:|:---:|:------:|:-------:|
| simple | 15 | -0.20 | [-0.60, +0.13] | 0.516 |
| local_reasoning | 10 | -0.10 | [-0.25, +0.00] | 0.503 |
| multi_document | 10 | +0.10 | [-0.20, +0.40] | 0.743 |
| table_extraction | 5 | +0.20 | [+0.00, +0.60] | 1.000 |
| negative | 10 | -0.15 | [-0.45, +0.00] | 1.000 |

#### Gemma 4 26B (26B)

| Type | n | Δ | CI 95% | p-value |
|------|:-:|:---:|:------:|:-------:|
| simple | 15 | -0.33 | [-0.73, +0.00] | 0.258 |
| local_reasoning | 10 | +0.25 | [+0.00, +0.65] | 0.504 |
| multi_document | 10 | -0.20 | [-0.40, +0.00] | 0.252 |
| table_extraction | 5 | +0.50 | [-0.70, +2.00] | 0.749 |
| negative | 10 | +0.00 | [-0.45, +0.45] | 1.000 |

---

## Caveats

- **Per-type analysis is diagnostic (5-15 examples per type), not statistically robust.** Small sample sizes inflate confidence intervals and reduce power.
- **Gemma 4 26B Pipeline C** affected by Gemini API HTTP 500 errors (36% of questions). Results marked with † are unreliable for this model-pipeline.
- **Bootstrap assumes i.i.d. residuals.** With 50 questions, the paired bootstrap on deltas is the appropriate non-parametric method.
- **Permutation test** tests H₀: mean(Δ) = 0 via label randomization within each question pair.
- **Scoring method**: fuzzy word-overlap (threshold 0.4), same as `evaluate.py`. Same scoring function used for all pipelines.

## Interpretation Guide

- **Δ > 0**: Pipeline X scores higher than Pipeline Y (Raw advantage, or filter recovery)
- **p < 0.05**: Statistically significant at conventional threshold
- **CI excludes 0**: Directional effect supported at 95% confidence
- **Small per-type groups (e.g., table_metric: n=5)**: Interpret with extreme caution