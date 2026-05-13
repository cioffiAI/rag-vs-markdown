# Local Evidence RAG — Piano Esecutivo

## Regola ferrea

**Non si aggiorna il paper con risultati non ancora generati.** La Fase 1 modifica solo il testo esistente (tono, claim, onestà). I nuovi numeri (Pipeline C, bootstrap, embedding) entrano nel paper solo dopo essere stati generati e validati. Se una fase produce risultati, si scrive un report separato (`reports/`); il paper `main.tex` si aggiorna solo alla Fase 8.

---

## Fase 0 — Freeze baseline

| # | Task | Dove | Done quando |
|---|------|------|-------------|
| 0.1 | `git tag v0.1-baseline` | `git tag -a v0.1-baseline -m "Stato pre-revisione: 10 doc, 50 domande, 4 modelli, 2 pipeline, scoring fuzzy overlap"` | Tag creato |
| 0.2 | Copia risultati attuali in `results/v0.1_baseline/` | `mkdir -p results/v0.1_baseline/` + copia `reports/*.md`, `data/logs/batch_*.json`, eventuali chunk metadata | Tutti i file copiati |
| 0.3 | Crea `configs/baseline.yaml` | `mkdir -p configs/` | File esiste e documenta: `embedder: all-MiniLM-L6-v2, chunk_size: 1500 (closing threshold), overlap: 150, top_k: 3, distance: cosine, temperature: 0.1, max_tokens: 256, models: [qwen3.5-0.8b, nemotron-3-super-free, deepseek-v4-flash, gemma-4-26b-a4b-it]` |
| 0.4 | Crea `reports/v0.1_baseline_audit.md` | Descrive: cosa è stato testato (2 pipeline, 4 modelli, 50 domande), cosa no (nessuna Pipeline C, nessun bootstrap, nessun secondo embedding, nessun LLM judge, nessun corpus sintetico) | Audit approvato |

---

## Fase 1 — Paper revision (solo testo, zero esperimenti)

| # | Task | Dove | Done quando |
|---|------|------|-------------|
| 1.1 | Cambia titolo in `When Markdown Hurts RAG: Shallow Structural Chunks as Dense Retrieval False Positives` | `main.tex:19-21` e `hyperref:38` | Compila senza errori |
| 1.2 | Riscrivi abstract: claim ristretto, non "larger models prefer raw text" ma "in our 4 model-provider configurations, Markdown advantage reverses; pattern consistent with model × pipeline interaction" | `main.tex:47-49` | Nessun claim causale su "model size" |
| 1.3 | Riscrivi sezioni model gradient (Results + Discussion): ogni menzione di "larger models prefer raw text" diventa "our four configurations show a monotonic reversal; this is confounded by provider identity" | `main.tex:214-241, 329-341` | Parola "confounded" appare prima di ogni generalizzazione |
| 1.4 | "Previously unreported phenomenon" → "we characterize a retrieval failure mode we call shallow chunks" | `main.tex:61` | Testo corretto |
| 1.5 | "Strictly harmful" riferito a Markdown → "in our setup, for models 3B+, Markdown's shallow-chunk cost outweighs structural benefit" | `main.tex:331` | Sfumato |
| 1.6 | Aggiungi parametri sperimentali completi in tabella/appendice: temperatura, max_tokens, top_k, prompt letterale, model ID completi | `main.tex:146-168` + Appendix | Tutti i parametri documentati |
| 1.7 | Aggiungi tabella "Claims vs Evidence" in Discussion | `main.tex:~323` | Tabella presente |
| 1.8 | Aggiungi limitation esplicita: "we test one specific Markdown pipeline, not Markdown in general. A different compiler, chunker, or threshold may produce different results" | `main.tex:343-354` | Riga presente in Limitations |

### Contenuto tabella Claims vs Evidence (1.7)

| Claim | Evidence | Status |
|-------|----------|--------|
| Markdown preprocessing can harm retrieval quality | Supported in our setup (Δ -3.6% to -5.2% for 3B+ models) | Moderate |
| Shallow structural chunks (~25%) compete with substantive chunks in cosine retrieval | Supported: 38/150 MD chunks ≤200 chars vs 0% in Raw | Strong |
| Larger models prefer raw text | Observed across 4 configs but confounded by provider/API/prompt | Weak — needs controlled family test |
| Markdown is harmful in general | Not demonstrated | Do not claim |
| Filtering shallow chunks would recover Markdown's position | Hypothesis only, not tested until Pipeline C | Untested |

---

## Fase 2 — Pipeline C ablation (priorità scientifica #1)

**Definizione**: `informative_len = len(re.sub(r'[#*`|---\[\]>]', '', chunk_text).strip())`
**Regola**: `keep if informative_len > threshold`, default `threshold=200`.

| # | Task | Dove | Done quando |
|---|------|------|-------------|
| 2.1 | `build_index.py`: aggiungi `--pipeline c` = `md_filtered` | `build_index.py` flag args | `python build_index.py --pipeline c` funziona |
| 2.2 | Calcola `informative_len` per ogni chunk Markdown prima del filtro | `build_index.py` funzione `informative_text_len()` | Valore loggato nei metadata |
| 2.3 | Filtra chunk con `informative_len ≤ threshold` (flag `--shallow-threshold`, default 200) | `build_index.py` smart_chunk_text o post-filter | Collezione `rag_papers_md_filtered` creata |
| 2.4 | Sensitivity: esegui build con threshold 100, 150, 200, 250, 300 → log numero chunk filtrati ciascuno | Script interno o parametro iterativo | Report `reports/pipeline_c_sensitivity.md` |
| 2.5 | `query.py`: supporta `--pipeline c` | `scripts/query.py` COLLECTIONS + get_collection | Funziona |
| 2.6 | Esegui batch query su Pipeline C con tutti e 4 i modelli (stesse 50 domande, stessi parametri) | `python scripts/query.py --pipeline c --file data/benchmark_questions.json --model ...` | 4 batch JSON salvati |
| 2.7 | Valuta con `evaluate.py` + genera report comparativo A/B/C | `python scripts/evaluate.py` + `scripts/compare_pipelines.py` | Report `reports/comparative_abc.md` |

**Output atteso**: tabella `Model | A (Raw) | B (MD) | C (MD-filtered) | Δ B-A | Δ C-A | Δ C-B`.

---

## Fase 3 — Statistica inferenziale

| # | Task | Metodo | Done quando |
|---|------|--------|-------------|
| 3.1 | Bootstrap sui delta appaiati: per ogni modello, campiona con replacement 10k volte la media dei `delta_i = score_raw_i - score_md_i` | `scripts/bootstrap.py` con `--pairs` | CI 95% stampato |
| 3.2 | Permutation test: permuta casualmente l'etichetta raw/md dentro ogni domanda, 10k ripetizioni, p-value = frazione di permutazioni con Δ ≥ osservato | Stesso script, flag `--permutation` | p-value per modello |
| 3.3 | Stessa analisi per sottotipo (factual, local, multi, table, negative) e per Pipeline C vs A, C vs B | `--by-type` flag | Report `reports/bootstrap_results.md` |
| 3.4 | Caveat nei risultati: "per-category analysis is diagnostic (few examples), not statistically robust" | Testo nel report | Presente |

**Output per modello**:
```
Model | Δ Raw-MD | CI 95% | p-value
Qwen 0.8B  | +0.06 | [-0.31, +0.43] | 0.38
Nemotron 3 | -0.18 | [-0.52, +0.16] | 0.15
...
```

---

## Fase 4 — Robustezza embedding

| # | Task | Done quando |
|---|------|-------------|
| 4.1 | `build_index.py`: flag `--embedder` (default all-MiniLM-L6-v2), accetta nome modello sentence-transformers | `python build_index.py --pipeline a --embedder bge-small-en-v1.5` funziona |
| 4.2 | Rebuild A/B/C con `bge-small-en-v1.5` | Collezioni ChromaDB distinte per embedder |
| 4.3 | Opzionale: `e5-small-v2` con formato `query: ...` / `passage: ...` corretto | Se implementato, documentare formato |
| 4.4 | Esegui query + eval su A/B/C con nuovo embedder (almeno modello più grande, es. Gemma 4) | Report `reports/embedder_comparison.md` |
| 4.5 | Confronta: proporzione shallow chunks cambia? Δ C-A è stabile? | Conclusione nel report |

---

## Fase 5 — Valutazione multi-metodo

| # | Task | Done quando |
|---|------|-------------|
| 5.1 | LLM-as-judge: script `scripts/llm_judge.py` che prende `(question, answer, context, ground_truth)` → score 0-5 con rubrica rigida, usando Gemma 4 26B via stessa API | Report `reports/llm_judge_results.md` |
| 5.2 | Esegui su tutti i batch A/B/C per tutti i modelli | Confronto `fuzzy vs llm_judge` per-pipeline |
| 5.3 | Human audit: 20 domande campione (stratificate per tipo), score manuale su scala 0-5 | File `reports/human_audit_20.csv` |
| 5.4 | Confronto: `fuzzy mean / LLM judge mean / human mean` per pipeline, annotando discrepanze | Sezione nel report |

---

## Fase 6 — Espansione corpus

| # | Task | Done quando |
|---|------|-------------|
| 6.1 | Aggiungi 5-10 documenti oscuri reali (paper poco citati, report tecnici) in `data/raw/` | Estratti e processati |
| 6.2 | Aggiungi 5-10 documenti sintetici con fatti artificiali (es. "Zorvian Retrieval Protocol", fatti inventati ma strutturati) | Contenuto verificabile non presente in nessun LLM |
| 6.3 | Aggiungi 25-50 nuove domande per i nuovi documenti in `gold_questions.csv` | Domande validate |
| 6.4 | **Rerun Fasi 2-3** su corpus espanso (Pipeline C + bootstrap) | Report `reports/corpus_expanded_comparison.md` |

---

## Fase 7 — Controllo famiglia modelli (OPZIONALE, non bloccante)

| # | Task | Done quando |
|---|------|-------------|
| 7.1 | Scegli famiglia: Qwen 2.5 (0.5B, 1.5B, 3B, 7B) via stessa API (es. OpenRouter o Together) | Decisione documentata |
| 7.2 | Stesso prompt, stessa temperatura, stesso sistema | Prompt identico |
| 7.3 | Rerun A/B/C su tutti i size della famiglia | Report `reports/model_family_control.md` |

Se non fattibile (costi API, modelli non disponibili), si documenta come limitation e si procede.

---

## Fase 8 — Versione submission

| # | Task | Done quando |
|---|------|-------------|
| 8.1 | Riscrittura completa `main.tex` con claim finale: non "Markdown vs Raw", ma "Markdown preprocessing can create shallow structural chunks that harm dense retrieval unless filtered" | Paper completo |
| 8.2 | Inserisci tutti i nuovi risultati (Pipeline C, bootstrap, secondo embedder, LLM judge, corpus espanso) | Figure e tabelle aggiornate |
| 8.3 | Aggiungi reproducibility checklist (parametri, seed, API versioni, date esecuzione) | Appendix |
| 8.4 | Aggiungi limitations aggiornate (cosa NON è stato testato: famiglia modelli controllata se Fase 7 saltata, ecc.) | Sezione Limitations |
| 8.5 | Prepara per arXiv / workshop (formato, abstract breve, keyword, copyright) | `paper/` pronto per submission |

---

## Schema dipendenze

```
Fase 0 ──blocca──► Fase 1 (paper edit, solo testo)
                    │
                    ▼
                 Fase 2 (Pipeline C)
                    │
                    ▼
                 Fase 3 (bootstrap + permutation)
                    │
              ┌─────┼─────┐
              ▼     ▼     ▼
           Fase 4  Fase 5  Fase 6
           (embed) (eval)  (corpus)
              │     │     │
              └─────┼─────┘
                    ▼
                 Fase 7 (opzionale)
                    │
                    ▼
                 Fase 8 (submission)
```
