# Pipeline C Sensitivity Analysis

*Generated: 2026-05-13*

## Shallow Threshold Sweep

| Threshold | Total | Kept | Filtered | % Filtered |
|----------:|:----:|:----:|:--------:|:----------:|
| 100 | 553 | 548 | 5 | 0.9% |
| 150 | 553 | 548 | 5 | 0.9% |
| 200 | 553 | 544 | 9 | 1.6% |
| 250 | 553 | 544 | 9 | 1.6% |
| 300 | 553 | 544 | 9 | 1.6% |

## Key Findings

- **Threshold plateaus**: T=100 and T=150 behave identically (5 chunks filtered). T=200, T=250, and T=300 also behave identically (9 chunks filtered). This means the shallow chunk size distribution is bimodal: very small (≤150 chars) and medium-small (151–200 chars), with nothing in the 200–300 range.
- **Default T=200** filters 9 shallow chunks (1.6% of collection), which is the effective separation point.
- **Maximum filter rate is 1.6%** even at T=300, confirming that shallow chunks are a small fraction of the total corpus.

## Interpretation

- **T=100**: Removes only extreme headers (~5 chunks). Nearly equivalent to unfiltered Markdown.
- **T=200 (default)**: Matches the shallow chunk definition used in the paper and comparative analysis. Removes all 9 shallow chunks.
- **T=300**: Same as T=200 — no additional chunks between 200–300 chars, meaning no shallow chunk exceeds 200 informative characters.

The 200-character threshold is robust: increasing beyond 200 has no effect, and lowering to 150 removes only 5 chunks instead of 9. The default threshold captures all shallow chunks without being overly aggressive.

## Recommendation

Use **T=200** as the primary threshold for Pipeline C. The comparative ABC analysis uses this value.
