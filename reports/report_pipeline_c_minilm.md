# RAG Benchmark Evaluation Report

*Generated: 2026-05-13T17:48:49.624223*

*Batch file: batch_gemma4b_c_20260513_145354.json*

---

## Overall Results

| Metric | Value |
|--------|-------|
| Questions | 50 |
| Mean Score (max 5) | 2.16 |
| Normalized (%) | 43.2% |

## Results by Question Type

| Type | Count | Mean | Min | Max |
|------|-------|------|-----|-----|
| local_reasoning | 10 | 1.9 | 0.0 | 4.0 |
| multi_document | 10 | 2.35 | 1.0 | 4.0 |
| negative | 10 | 2.1 | 0.0 | 3.0 |
| simple | 15 | 2.33 | 1.0 | 4.0 |
| table_extraction | 5 | 1.9 | 1.0 | 3.0 |

## Results by Category

| Category | Count | Mean |
|----------|-------|------|
| comparison | 10 | 2.35 |
| factual_evidence | 15 | 2.33 |
| false_premise | 3 | 1.5 |
| out_of_domain | 2 | 2.25 |
| same_document | 10 | 1.9 |
| table_metric | 5 | 1.9 |
| true_absence | 5 | 2.4 |

## Detailed Scores

```
[4.0, 3.0, 1.0, 1.0, 3.0, 4.0, 4.0, 2.0, 3.0, 3.0, 1.0, 1.0, 1.0, 1.0, 3.0, 1.0, 2.5, 2.0, 4.0, 1.0, 1.0, 2.5, 4.0, 0.0, 1.0, 3.0, 1.0, 1.0, 3.0, 1.0, 4.0, 2.0, 3.0, 2.5, 3.0, 3.0, 2.0, 2.5, 1.0, 1.0, 3.0, 3.0, 3.0, 3.0, 0.0, 3.0, 0.0, 1.5, 3.0, 1.5]
```