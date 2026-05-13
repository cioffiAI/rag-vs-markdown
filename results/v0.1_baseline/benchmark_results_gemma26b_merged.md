# RAG Benchmark Evaluation Report

*Generated: 2026-05-12T12:19:16.483822*

*Batch file: batch_gemma26b_b_merged.json*

---

## Overall Results

| Metric | Value |
|--------|-------|
| Questions | 50 |
| Mean Score (max 5) | 2.86 |
| Normalized (%) | 57.2% |

## Results by Question Type

| Type | Count | Mean | Min | Max |
|------|-------|------|-----|-----|
| local_reasoning | 10 | 3.05 | 1.5 | 4.0 |
| multi_document | 10 | 2.85 | 1.5 | 4.0 |
| negative | 10 | 2.7 | 1.5 | 3.0 |
| simple | 15 | 2.67 | 1.0 | 4.0 |
| table_extraction | 5 | 3.4 | 1.0 | 4.0 |

## Results by Category

| Category | Count | Mean |
|----------|-------|------|
| comparison | 10 | 2.85 |
| factual_evidence | 15 | 2.67 |
| false_premise | 3 | 2.5 |
| out_of_domain | 2 | 3.0 |
| same_document | 10 | 3.05 |
| table_metric | 5 | 3.4 |
| true_absence | 5 | 2.7 |

## Detailed Scores

```
[2.0, 3.0, 2.0, 3.0, 2.0, 4.0, 4.0, 2.0, 3.0, 1.0, 4.0, 3.0, 3.0, 1.0, 3.0, 3.0, 4.0, 2.5, 4.0, 2.5, 2.0, 3.0, 4.0, 1.5, 4.0, 4.0, 1.5, 1.5, 3.0, 2.0, 4.0, 3.0, 3.0, 2.5, 4.0, 4.0, 4.0, 4.0, 4.0, 1.0, 3.0, 3.0, 1.5, 1.5, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]
```