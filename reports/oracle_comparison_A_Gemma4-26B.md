# Oracle Comparison: A / Gemma4-26B

**Retrieval batch:** batch_gemma26b_a_20260512_122008.json
**Oracle batch:** oracle_oracle_b_20260512_135401.json
**Questions compared:** 30

## Overall

| Metric | Retrieval | Oracle | Delta |
|--------|-----------|--------|-------|
| Mean score | 1.73 | 2.90 | +1.17 |
| Improvement | — | — | 67.3% |

## By Type

| Type | Retrieval | Oracle | Delta |
|------|-----------|--------|-------|
| local_reasoning | 1.80 | 2.80 | +1.00 |
| multi_document | 1.60 | 3.20 | +1.60 |
| simple | 1.73 | 2.87 | +1.13 |

## Per-Question

| ID | Type | Retrieval | Oracle | Delta |
|----|------|-----------|--------|-------|
| Q001 | simple | 1.0 | 4.0 | +3.0 |
| Q002 | simple | 1.0 | 1.0 | +0.0 |
| Q003 | simple | 4.0 | 2.0 | -2.0 |
| Q004 | simple | 1.0 | 1.0 | +0.0 |
| Q005 | simple | 1.0 | 4.0 | +3.0 |
| Q006 | simple | 4.0 | 4.0 | +0.0 |
| Q007 | simple | 1.0 | 4.0 | +3.0 |
| Q008 | simple | 1.0 | 4.0 | +3.0 |
| Q009 | simple | 1.0 | 3.0 | +2.0 |
| Q010 | simple | 1.0 | 2.0 | +1.0 |
| Q011 | simple | 4.0 | 4.0 | +0.0 |
| Q012 | simple | 1.0 | 1.0 | +0.0 |
| Q013 | simple | 3.0 | 4.0 | +1.0 |
| Q014 | simple | 1.0 | 3.0 | +2.0 |
| Q015 | simple | 1.0 | 2.0 | +1.0 |
| Q016 | local_reasoning | 1.0 | 3.0 | +2.0 |
| Q017 | local_reasoning | 2.0 | 4.0 | +2.0 |
| Q018 | local_reasoning | 3.0 | 2.0 | -1.0 |
| Q019 | local_reasoning | 4.0 | 4.0 | +0.0 |
| Q020 | local_reasoning | 1.0 | 2.0 | +1.0 |
| Q021 | local_reasoning | 1.0 | 1.0 | +0.0 |
| Q022 | local_reasoning | 1.0 | 3.0 | +2.0 |
| Q023 | local_reasoning | 1.0 | 4.0 | +3.0 |
| Q024 | local_reasoning | 3.0 | 1.0 | -2.0 |
| Q025 | local_reasoning | 1.0 | 4.0 | +3.0 |
| Q026 | multi_document | 4.0 | 4.0 | +0.0 |
| Q027 | multi_document | 1.0 | 4.0 | +3.0 |
| Q028 | multi_document | 1.0 | 3.0 | +2.0 |
| Q029 | multi_document | 1.0 | 1.0 | +0.0 |
| Q030 | multi_document | 1.0 | 4.0 | +3.0 |