# Bootstrap & Permutation Test Results

*Generated: 2026-05-13T17:52:52.064731*
*Resamples: 5000 | Seed: 42 | CI: 95%*

## Raw vs Markdown  (Δ Raw-MD)

| Model | Size | Δ Raw-MD | CI 95% | p-value | n |
|-------|------|:-------:|:------:|:-------:|:-:|
| Gemma 3 4B | 4B | +0.30 | [+0.01, +0.59] | 0.061 | 50 |

## Raw vs MD-filtered  (Δ Raw-MDf)

| Model | Size | Δ Raw-MDf | CI 95% | p-value | n |
|-------|------|:-------:|:------:|:-------:|:-:|
| Gemma 3 4B | 4B | +0.13 | [-0.20, +0.45] | 0.482 | 50 |

## Markdown vs MD-filtered  (Δ MD-MDf)

| Model | Size | Δ MD-MDf | CI 95% | p-value | n |
|-------|------|:-------:|:------:|:-------:|:-:|
| Gemma 3 4B | 4B | -0.17 | [-0.47, +0.13] | 0.304 | 50 |

---

## Per-Question Type Breakdown

### Raw vs Markdown

#### Gemma 3 4B (4B)

| Type | n | Δ | CI 95% | p-value |
|------|:-:|:---:|:------:|:-------:|
| simple | 15 | +0.73 | [+0.33, +1.27] | 0.015 |
| local_reasoning | 10 | +0.40 | [+0.10, +0.70] | 0.122 |
| multi_document | 10 | +0.05 | [-0.50, +0.65] | 1.000 |
| table_extraction | 5 | +0.20 | [-0.60, +1.20] | 1.000 |
| negative | 10 | -0.15 | [-1.05, +0.75] | 1.000 |

### Raw vs MD-filtered

#### Gemma 3 4B (4B)

| Type | n | Δ | CI 95% | p-value |
|------|:-:|:---:|:------:|:-------:|
| simple | 15 | +0.40 | [-0.07, +0.93] | 0.262 |
| local_reasoning | 10 | +0.50 | [+0.00, +1.10] | 0.246 |
| multi_document | 10 | +0.10 | [-0.40, +0.60] | 1.000 |
| table_extraction | 5 | +0.10 | [-0.60, +0.90] | 1.000 |
| negative | 10 | -0.60 | [-1.65, +0.45] | 0.427 |

### Markdown vs MD-filtered

#### Gemma 3 4B (4B)

| Type | n | Δ | CI 95% | p-value |
|------|:-:|:---:|:------:|:-------:|
| simple | 15 | -0.33 | [-0.67, +0.00] | 0.183 |
| local_reasoning | 10 | +0.10 | [-0.40, +0.80] | 1.000 |
| multi_document | 10 | +0.05 | [-0.15, +0.30] | 1.000 |
| table_extraction | 5 | -0.10 | [-0.30, +0.00] | 1.000 |
| negative | 10 | -0.45 | [-1.65, +0.75] | 0.623 |

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