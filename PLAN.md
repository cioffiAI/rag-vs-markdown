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

## Fase 4 — Robustezza embedding ✅

| # | Task | Done quando |
|---|------|-------------|
| 4.1 | `build_index.py`: flag `--embedder` (default all-MiniLM-L6-v2), accetta nome modello sentence-transformers | `python build_index.py --pipeline a --embedder BAAI/bge-small-en-v1.5` funziona ✅ |
| 4.2 | Rebuild A/B/C con `BAAI/bge-small-en-v1.5` | Collezioni ChromaDB: `rag_papers_raw_BAAI_bge-small-en-v1.5` (633), `rag_papers_BAAI_bge-small-en-v1.5` (664), `rag_papers_md_filtered_BAAI_bge-small-en-v1.5` (647) ✅ |
| 4.3 | Opzionale: `e5-small-v2` — non implementato | Skippato |
| 4.4 | Esegui query + eval su A/B/C con bge + Gemma 3 4B | `reports/embedder_comparison.md` ✅ |
| 4.5 | Δ medio assoluto 0.12/5.0 — embedder non altera ranking pipeline | Conclusione: MiniML recomendato (non richiede download) ✅ |

**Risultati chiave**: Δ A=-0.08, Δ B=+0.08, Δ C=-0.19 su 50 domande comuni.

---

## Fase 5 — Valutazione multi-metodo ✅

| # | Task | Done quando |
|---|------|-------------|
| 5.1 | LLM-as-judge: script `scripts/llm_judge.py` con `nemotron-3-super:cloud` (Ollama Cloud, non Gemma 4 26B come da piano), rubrica 0-5, temperature=0 | ✅ |
| 5.2 | Eseguito su tutti i 9 batch (3 modelli × 3 pipeline), 50/50 score validi | ✅ |
| 5.3 | Human audit: 20 domande stratificate (5 simple, 4 local, 4 multi, 3 table, 4 negative), colonna `human_score` vuota | `reports/human_audit_20.csv` ✅ |
| 5.4 | Confronto fuzzy vs LLM judge: LLM judge dà punteggi sistematicamente più bassi (Δ -0.21 a -1.20). Correlazione Pearson debole (0.25-0.48). Metriche misurano aspetti diversi. | `reports/llm_judge_results.md` + `scripts/compare_judge_vs_fuzzy.py` ✅ |

**Risultati chiave**: LLM judge costantemente più severo del fuzzy overlap. Due metriche complementari, non sostituibili.

---

## Fase 6 — Espansione corpus ✅

| # | Task | Done quando |
|---|------|-------------|
| 6.1 | 5 paper arXiv oscuri (REPLUG, HyDE, RAPTOR, In-Context RALM, LLM-Augmenter) + 5 sintetici (ZRP, NSIF, QEP, TempRAG, ACF) | `data/raw/` (15 PDF), `data/extracted/` (20 JSON), `data/processed/` (20 MD) ✅ |
| 6.2 | 5 documenti sintetici con fatti artificiali verificabili (Zorvian Retrieval Protocol, Neuro-Symbolic Index Fusion, Quantum Embedding Projection, Temporal RAG, Adversarial Chunk Filter) | Iniettati come JSON+MD direttamente ✅ |
| 6.3 | 25 nuove domande Q051-Q075 (13 su reali, 12 su sintetici). Distribuzione tipi mantenuta. `gold_questions.csv` rigenerato (75 righe). | `data/benchmark_questions.json`: 75 domande ✅ |
| 6.4 | Rerun build index + query + eval + bootstrap su A/B/C con Gemma 3 4B. Vantaggio Raw-MD si attenua (Δ=+0.13 vs +0.30 su 50q). Nessun risultato significativo (p>0.2). | `reports/corpus_expanded_comparison.md` + `reports/bootstrap_expanded_results.md` ✅ |

**Risultati chiave**: Vantaggio Raw persiste ma si riduce (Δ +0.30 → +0.13). Pipeline C non mostra recupero sul corpus espanso.

---

## Fase 7 — Controllo famiglia modelli (OPZIONALE, non bloccante)

| # | Task | Done quando |
|---|------|-------------|
| 7.1 | Scegli famiglia: Qwen 2.5 (0.5B, 1.5B, 3B, 7B) via stessa API (es. OpenRouter o Together) | Decisione documentata |
| 7.2 | Stesso prompt, stessa temperatura, stesso sistema | Prompt identico |
| 7.3 | Rerun A/B/C su tutti i size della famiglia | Report `reports/model_family_control.md` |

Se non fattibile (costi API, modelli non disponibili), si documenta come limitation e si procede.

---

## Fase 8 — Versione submission ✅

| # | Task | Done quando |
|---|------|-------------|
| 8.1 | Riscrittura completa `main.tex` con tutti i risultati Fase 0-6 (4 modelli, 3 pipeline, bootstrap, embedder, LLM judge, corpus espanso, oracle, error taxonomy) | Paper compilato (16 pp, zero errori) ✅ |
| 8.2 | Inseriti tutti i nuovi risultati: Table 1 (gradient), Table 2 (bootstrap), Table 3 (per-type), Table 4 (embedder), Table 5 (judge), Table 6 (expanded), Table 7 (oracle), Table 8 (errors), Claims vs Evidence aggiornata | ✅ |
| 8.3 | Reproducibility checklist in Appendix C (parametri, seed, API, versioni, date esecuzione 12-13 Maggio 2026) | ✅ |
| 8.4 | Limitations aggiornate (9 punti: provider confound, embedding dimension, benchmark size, scoring proxy, single Markdown pipeline, synthetic doc limits, single model expanded, Italian language, famous papers bias) | ✅ |
| 8.5 | PDF compilato: `paper/main.pdf` (16 pagine, 1.37 MB) | ✅ |

---

## Schema dipendenze

```
Fase 0 ──► Fase 1 ──► Fase 2 ──► Fase 3
                                   │
                          ┌────────┼────────┐
                          ▼        ▼        ▼
                       Fase 4   Fase 5   Fase 6
                       (✅)     (✅)     (✅)
                          │        │        │
                          └────────┼────────┘
                                   ▼
                                Fase 7 (❌ saltata — direttamente a Fase 8)
                                   │
                                   ▼
                                Fase 8 (✅ submission paper)
```
