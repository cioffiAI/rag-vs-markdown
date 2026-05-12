# Error Taxonomy

This taxonomy classifies every failed answer by where the error originated in the pipeline. The goal is to move from "this answer scored low" to "this answer failed because of X".

## Error Codes

| Code | Name | Meaning | Example |
|------|------|---------|---------|
| `E01` | retrieval_miss | The correct document was not retrieved at all (not in top-k). | Query asks about YOLOv7 backbone, but all retrieved chunks are from Transformer paper. |
| `E02` | retrieval_weak | The correct document was retrieved, but the specific chunk with the answer was not among the top-k. | Correct paper is in top-3, but the chunk containing the answer is ranked 4th or lower. |
| `E03` | context_ignored | The correct chunk was retrieved, but the LLM ignored it and answered from parametric knowledge (or guessed). | Chunk contains "RAG-Sequence selects one document for the full sequence" but the LLM answers "there is no distinction". |
| `E04` | citation_missing | The answer is factually correct, but the LLM did not cite the source document. | Correctly explains RAG-Token but never mentions the paper name. |
| `E05` | hallucination | The answer contains information not present in any retrieved chunk. | LLM invents a GPU model, a learning rate, or a paper detail not in the context. |
| `E06` | false_refusal | The LLM declined to answer even though the correct answer was in the retrieved context. | "I cannot find information" when the chunk explicitly contains the answer. |
| `E07` | scoring_fuzzy | The automated scoring (word-overlap) may have misjudged a semantically correct answer. | Answer paraphrases "RAG-Sequence uses one document per sequence" as "each sequence is generated from a single document" — same meaning, low word overlap. |

## Pipeline Stage Mapping

```
Retrieval stage           Generation stage          Evaluation stage
                          
E01 retrieval_miss ──┐   E03 context_ignored ──┐   E07 scoring_fuzzy
E02 retrieval_weak ──┤   E04 citation_missing ─┤
                     ├──► E05 hallucination ───┤
                     │    E06 false_refusal ────┘
                     │
                     └──► (no retrieval error → E03+)
```

## How to Classify an Error

1. Check if the expected document was retrieved (in `retrieved_chunks`).
   - No → **E01** or **E02** (retrieval error)
2. Check if the LLM declined to answer despite having the right chunk.
   - Yes → **E06** (false refusal)
3. Check if the answer contains facts not in the chunks.
   - Yes → **E05** (hallucination)
4. Check if the answer is factually correct but does not cite the source.
   - Yes → **E04** (citation missing)
5. Check if the correct chunk was present but the LLM gave a wrong answer.
   - Yes → **E03** (context ignored)
6. If none of the above, check for **E07** (scoring artifact).

## Primary vs. Secondary Errors

A single answer can have multiple errors. In that case, classify the **primary** one (the earliest in the pipeline):

```
retrieval_miss (primary)
  └── hallucination (secondary, because the model had to guess without the right doc)

context_ignored (primary)
  └── citation_missing (secondary, consequence of ignoring context)
```

## Per-Dataset Error Profile (current Qwen 0.8B baseline)

To be filled after running `scripts/error_analysis.py` (planned, Fase 3).

| Pipeline | E01 | E02 | E03 | E04 | E05 | E06 | E07 |
|----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| B — Markdown | ? | ? | ? | ? | ? | ? | ? |
| A — Raw text | ? | ? | ? | ? | ? | ? | ? |

## Usage

When reporting results, append error codes to each score:

```
Q008: 1.0/5.0 [E01 retrieval_miss + E05 hallucination]
Q044: 0.0/5.0 [E05 hallucination: invented GPU specs for HELM]
```
