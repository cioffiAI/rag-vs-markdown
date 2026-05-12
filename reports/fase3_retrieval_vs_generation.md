# Fase 3: Oracle Test + Error Classification (RQ3)

**RQ3:** Are errors primarily caused by retrieval failures or generation failures?

## Setup

| Parameter | Value |
|-----------|-------|
| LLM | Gemma 4 26B A4B via Google Gemini API |
| Retrieval | TOP_K = 3 chunks, cosine distance |
| Oracle | Full raw extracted text (up to 50k chars/document) |
| Pipeline A | Raw chunks from `rag_papers_raw` (542 chunks) |
| Pipeline B | Markdown chunks from `rag_papers` (553 chunks) |
| Oracle questions | 30/50 completed (3 HTTP 500 errors excluded) |
| Error taxonomy | E01–E07 classification |

## Error Classification (E01–E07)

For each of the 50 questions, we classified the error using the taxonomy:

| Code | Name | Pipeline A | Pipeline B | Meaning |
|------|------|:---------:|:---------:|---------|
| E01 | retrieval_miss | **4** | **6** | Correct document not in top-3 |
| E02 | retrieval_weak | 0 | 0 | Doc retrieved but specific chunk missing (not distinguishable from E01 without oracle) |
| E03 | context_ignored | **4** | **1** | Correct chunk retrieved but LLM ignored it |
| E04 | citation_missing | **9** | **8** | Answer correct but no source citation |
| E05 | hallucination | 0 | **1** | Answer contains facts not in chunks |
| E06 | false_refusal | **21** | **23** | LLM said "cannot find" despite having the correct chunk |
| E07 | scoring_fuzzy | 0 | 0 | Word-overlap metric misjudged correct answer |
| | *LLM error (HTTP 500)* | 2 | 3 | API error |
| | *Correct refusal (negative)* | 10 | 8 | Properly declined unanswerable questions |

### Per-Type Error Profile (Pipeline B)

| Type | Count | E01 | E03 | E04 | E05 | E06 | REF |
|------|-------|:---:|:---:|:---:|:---:|:---:|:---:|
| simple | 15 | 3 | 0 | 2 | 0 | 9 | 0 |
| local_reasoning | 10 | 1 | 1 | 2 | 0 | 6 | 0 |
| multi_document | 10 | 2 | 0 | 2 | 0 | 6 | 0 |
| table_extraction | 5 | 0 | 0 | 2 | 0 | 2 | 0 |
| negative | 10 | 0 | 0 | 0 | 1 | 0 | 8 |

### Per-Type Error Profile (Pipeline A)

| Type | Count | E01 | E03 | E04 | E05 | E06 | REF |
|------|-------|:---:|:---:|:---:|:---:|:---:|:---:|
| simple | 15 | 1 | 1 | 3 | 0 | 10 | 0 |
| local_reasoning | 10 | 1 | 2 | 1 | 0 | 4 | 0 |
| multi_document | 10 | 2 | 0 | 2 | 0 | 6 | 0 |
| table_extraction | 5 | 0 | 1 | 3 | 0 | 1 | 0 |
| negative | 10 | 0 | 0 | 0 | 0 | 0 | 10 |

## Oracle Test Results

Giving the LLM the full document text (instead of top-3 chunks) produces a dramatic improvement:

| Metric | Pipeline B Retr. | Oracle | Delta | Pipeline A Retr. | Oracle | Delta |
|--------|:--------------:|:-----:|:-----:|:--------------:|:-----:|:-----:|
| Mean score (30 Qs) | 1.58 | **2.93** | **+1.35 (+85%)** | 1.73 | **2.90** | **+1.17 (+67%)** |
| simple | 1.47 | 2.87 | +1.40 | 1.73 | 2.87 | +1.13 |
| local_reasoning | 1.75 | 3.00 | +1.25 | 1.80 | 2.80 | +1.00 |
| multi_document | 1.60 | 3.00 | +1.40 | 1.60 | 3.20 | +1.60 |

**Diagnostic interpretation (not causal):**
- When given full document context, Gemma 4 scores 2.90–2.93/5.0 regardless of pipeline.
- The +67–85% improvement from oracle context is mostly driven by converting E06 (false_refusal) → correct answers. This is consistent with retrieval insufficiency but **E06 may also reflect generation-side over-cautiousness** — the model refuses unless the answer is obvious, and full-document context makes the answer more salient.
- ~47% of questions (14/30) improved by 2+ points with oracle context — these are cases where the oracle context added information that the top-3 chunks lacked.
- ~33% of questions (10/30) showed no improvement or slight degradation — these are cases where the oracle context did not help, suggesting generation-side or prompt-format limitations rather than retrieval failures.

**Important oracle test limitations:**
1. **Upper-bound only**: replacing top-3 chunks with full document text eliminates retrieval error entirely, which is unrealistic for any deployed RAG system. The +67–85% is a ceiling, not a typical improvement.
2. **Single-context oracle**: both pipelines use the same raw-text oracle. A Markdown oracle for Pipeline B would give a more diagnostic comparison but was not feasible due to API rate limits.
3. **E06 is ambiguous**: "false refusal" sits at the retrieval–generation boundary. It may be retrieval insufficiency (correct passage missing from top-3), generation-side over-cautiousness (model refuses unless answer is trivial), or both. The oracle +85% suggests retrieval plays a role, but E06's 42–46% prevalence includes both effects.

## Answer to RQ3 (Diagnostic)

**The data are consistent with retrieval being the dominant performance constraint on this benchmark**, but the evidence is correlational, not causal:

1. **~12%** of errors are pure retrieval failures (E01: correct document not in top-3).
2. **~42–47%** are plausible retrieval *insufficiency* (E06: false refusal with correct document in top-3 — the specific passage may be ranked 4th+, or the model may be over-cautious).
3. **~20–33%** are persistent generation failures — even with full oracle context, scores remain low. This is partly a **prompt-format issue** (Gemma 4 repeats/analyzes the question instead of answering directly) and partly genuine knowledge gaps.
4. **~16%** are citation errors (E04): correct answers without source attribution.

**Bottom line:** The evidence is consistent with ~60% of the error budget being retrieval-related, ~25% generation-related, ~15% scoring/citation artifacts. These are diagnostic proportions, not causal attributions. The Markdown pipeline (B) has slightly *more* retrieval errors than raw text (A), which is consistent with the shallow-chunk hypothesis (Markdown produces many near-empty chunks that consume retrieval slots). See [docs/results.md](../docs/results.md) section 5 for the formal shallow-chunk definition.

## Files Created/Modified

- `docs/error_taxonomy.md` — Updated with filled per-dataset error profile
- `reports/error_profile_B_Gemma4-26B.md` — Detailed E01–E07 classification (Pipeline B)
- `reports/error_profile_A_Gemma4-26B.md` — Detailed E01–E07 classification (Pipeline A)
- `reports/oracle_comparison_B_Gemma4-26B.md` — Retrieval vs oracle comparison (Pipeline B)
- `reports/oracle_comparison_A_Gemma4-26B.md` — Retrieval vs oracle comparison (Pipeline A)
- `scripts/error_analysis.py` — Error classification script
- `scripts/oracle_test.py` — Oracle context test script
- `scripts/oracle_compare.py` — Retrieval vs oracle comparison script
