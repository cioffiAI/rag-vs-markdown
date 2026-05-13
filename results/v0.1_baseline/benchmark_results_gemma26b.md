# RAG Benchmark Evaluation Report

*Generated: 2026-05-12T11:50:17.495654*

*Batch file: batch_gemma26b_b_20260512_112225.json*

---

## Overall Results

| Metric | Value |
|--------|-------|
| Questions | 50 |
| Mean Score (max 5) | 2.57 |
| Normalized (%) | 51.4% |

## Results by Question Type

| Type | Count | Mean | Min | Max |
|------|-------|------|-----|-----|
| local_reasoning | 10 | 2.9 | 1.0 | 4.0 |
| multi_document | 10 | 2.35 | 1.0 | 4.0 |
| negative | 10 | 2.4 | 1.5 | 3.0 |
| simple | 15 | 2.33 | 1.0 | 4.0 |
| table_extraction | 5 | 3.4 | 1.0 | 4.0 |

## Results by Category

| Category | Count | Mean |
|----------|-------|------|
| comparison | 10 | 2.35 |
| factual_evidence | 15 | 2.33 |
| false_premise | 3 | 2.0 |
| out_of_domain | 2 | 3.0 |
| same_document | 10 | 2.9 |
| table_metric | 5 | 3.4 |
| true_absence | 5 | 2.4 |

## Detailed Scores

```
[2.0, 3.0, 2.0, 3.0, 2.0, 4.0, 1.0, 2.0, 3.0, 1.0, 4.0, 3.0, 1.0, 1.0, 3.0, 3.0, 4.0, 1.0, 4.0, 2.5, 2.0, 3.0, 4.0, 1.5, 4.0, 4.0, 1.5, 1.5, 1.0, 2.0, 1.0, 3.0, 3.0, 2.5, 4.0, 4.0, 4.0, 4.0, 4.0, 1.0, 1.5, 3.0, 1.5, 1.5, 3.0, 3.0, 3.0, 1.5, 3.0, 3.0]
```