# Error Profile: A (Raw) / Gemma 4 26B

**Batch file:** batch_gemma26b_a_20260512_122008.json
**Oracle file:** N/A
**Questions:** 50

## Error Counts

| Code | Name | Count |
|------|------|-------|
| E01 | retrieval_miss | 4 |
| E02 | retrieval_weak | 0 |
| E03 | context_ignored | 4 |
| E04 | citation_missing | 9 |
| E05 | hallucination | 0 |
| E06 | false_refusal | 21 |
| E07 | scoring_fuzzy | 0 |
| CORRECT_REFUSAL | correct refusal (negative) | 10 |
| LLM_ERROR | LLM error | 2 |

**Retrieval errors (E01):** 4/50
**Generation errors (E03-E06):** 34/50
**Correct refusals:** 10/50

## Per-Type Error Profile

| Type | Count | E01 | E03 | E04 | E05 | E06 | E07 | REF |
|------|-------|-----|-----|-----|-----|-----|-----|-----|
| local_reasoning | 10 | 1 | 2 | 1 | 0 | 4 | 0 | 0 |
| multi_document | 10 | 2 | 0 | 2 | 0 | 6 | 0 | 0 |
| negative | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 10 |
| simple | 15 | 1 | 1 | 3 | 0 | 10 | 0 | 0 |
| table_extraction | 5 | 0 | 1 | 3 | 0 | 1 | 0 | 0 |

## Per-Question Classification

| ID | Type | Doc OK | Codes | Answer Preview |
|----|------|--------|-------|----------------|
| Q001 | simple | True | E06 | *   Question: "In RAG, qual è la differenza fondamentale tra |
| Q002 | simple | True | E06 | *   Question: "Nel paper RAG, il retriever usa DPR. Cosa dis |
| Q003 | simple | True | E04,+E04 | *   Question: "Quali sono i tre tipi di critique token gener |
| Q004 | simple | True | E06 | *   Question: "Il paper Self-RAG dichiara esplicitamente il  |
| Q005 | simple | True | E06 | *   Question: "Quali sono i tre iperparametri architetturali |
| Q006 | simple | True | E04,+E04 | *   Question: "Nel Transformer, da quali due sotto-strati pr |
| Q007 | simple | True | E06 | *   Question: "Cosa sono i 'bag-of-freebies' in YOLOv7 e qua |
| Q008 | simple | True | E06 | *   Question: "Quale architettura backbone viene utilizzata  |
| Q009 | simple | True | E06 | *   Question: "Secondo il survey, quali sono le tre grandi a |
| Q010 | simple | True | E06 | *   Question: "Quali due benchmark specifici cita il survey  |
| Q011 | simple | True | E04,+E04 | *   Question: "Secondo Bommasani et al., quali sono le due p |
| Q012 | simple | True | E06 | *   Question: "Quali sono le quattro metriche principali pro |
| Q013 | simple | True | E03,+E04 | *   Question: "Quali sono i cinque domini specifici del benc |
| Q014 | simple | False | E01 | *   Question: "Come sono suddivise le 4.409 domande di CRAG  |
| Q015 | simple | True | E06 | *   Question: "Quali sono le 7 metriche di valutazione usate |
| Q016 | local_reasoning | False | LLM_ERROR | [ERROR LLM: Gemini HTTP 500 - {
  "error": {
    "code": 500 |
| Q017 | local_reasoning | True | LLM_ERROR | [ERROR LLM: Gemini HTTP 500 - {
  "error": {
    "code": 500 |
| Q018 | local_reasoning | True | E03,+E04 | *   Question: "Quali risultati emergono dagli ablation study |
| Q019 | local_reasoning | True | E04,+E04 | *   Question: "Spiega come funziona il meccanismo di scaled  |
| Q020 | local_reasoning | False | E01 | *   Question: "Qual è il contributo specifico della 'planned |
| Q021 | local_reasoning | True | E06 | *   Question: "Il survey discute i compromessi tra valutazio |
| Q022 | local_reasoning | True | E06 | *   Question: "Quali sono i rischi principali associati ai f |
| Q023 | local_reasoning | True | E06 | *   Question: "Come vengono calcolate faithfulness e answer  |
| Q024 | local_reasoning | True | E03,+E04 | *   Question: "CRAG analizza la degradazione della retrieval |
| Q025 | local_reasoning | True | E06 | *   Question: "HELM valuta 7 metriche su 42 scenari. Quali m |
| Q026 | multi_document | True | E04,+E04 | *   Question: "Confronta i meccanismi di retrieval in RAG or |
| Q027 | multi_document | True | E06 | *   Question: "Quali sono le principali differenze metodolog |
| Q028 | multi_document | False | E01 | *   Question: "Cosa distingue il dataset CRAG dalle domande  |
| Q029 | multi_document | False | E01 | *   Question: "In che modo Self-RAG e CRAG affrontano il pro |
| Q030 | multi_document | True | E06 | *   Question: "Quali elementi architetturali del Transformer |
| Q031 | multi_document | True | E04,+E04 | *   Question: "Quali metriche di valutazione sono comuni tra |
| Q032 | multi_document | True | E06 | *   Question: "Come vengono trattati i temi di bias e fairne |
| Q033 | multi_document | True | E06 | *   Question: "Sia Ragas che Self-RAG si occupano di faithfu |
| Q034 | multi_document | True | E06 | *   Question: "Entrambi i paper (YOLOv7 e Transformer) usano |
| Q035 | multi_document | True | E06 | *   Question: "Quali sono le differenze nel concetto di 'ret |
| Q036 | table_extraction | True | E04,+E04 | *   Question: "Nella tabella dei risultati BLEU sul WMT 2014 |
| Q037 | table_extraction | True | E04,+E04 | *   Question: "Nella tabella comparativa su MS COCO, quale A |
| Q038 | table_extraction | True | E06 | *   Question: "Secondo la tabella riassuntiva di HELM, quali |
| Q039 | table_extraction | True | E04,+E04 | *   Question: "Nelle tabelle di ablation di Self-RAG, quale  |
| Q040 | table_extraction | True | E03,+E04 | *   Question: "Nella tabella dei risultati per dominio di CR |
| Q041 | negative | True | CORRECT_REFUSAL | *   Question: "Quanto e' costato addestrare Self-RAG in term |
| Q042 | negative | False | CORRECT_REFUSAL | *   Question: "Quale framework di deep learning (PyTorch, Te |
| Q043 | negative | True | CORRECT_REFUSAL | *   Question: "In RAG, quale dataset specifico (oltre a Wiki |
| Q044 | negative | True | CORRECT_REFUSAL | *   Question: "Quale GPU e' stata usata per eseguire la valu |
| Q045 | negative | True | CORRECT_REFUSAL | *   Question: "Il paper RAG originale menziona 12 autori nel |
| Q046 | negative | True | CORRECT_REFUSAL | *   Question: "Tree of Thoughts propone un metodo specifico  |
| Q047 | negative | True | CORRECT_REFUSAL | *   Question: "Nel paper Transformer, quale learning rate co |
| Q048 | negative | True | CORRECT_REFUSAL | *   Question: "In HELM, quale modello ha ottenuto il puntegg |
| Q049 | negative | False | CORRECT_REFUSAL | *   Question: "Quali sono i nomi dei revisori del paper CRAG |
| Q050 | negative | False | CORRECT_REFUSAL | *   Question: "Tree of Thoughts valuta la qualita' del retri |