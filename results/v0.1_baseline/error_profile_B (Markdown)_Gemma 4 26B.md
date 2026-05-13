# Error Profile: B (Markdown) / Gemma 4 26B

**Batch file:** batch_gemma26b_b_merged.json
**Oracle file:** N/A
**Questions:** 50

## Error Counts

| Code | Name | Count |
|------|------|-------|
| E01 | retrieval_miss | 6 |
| E02 | retrieval_weak | 0 |
| E03 | context_ignored | 1 |
| E04 | citation_missing | 8 |
| E05 | hallucination | 1 |
| E06 | false_refusal | 23 |
| E07 | scoring_fuzzy | 0 |
| CORRECT_REFUSAL | correct refusal (negative) | 8 |
| LLM_ERROR | LLM error | 3 |

**Retrieval errors (E01):** 6/50
**Generation errors (E03-E06):** 33/50
**Correct refusals:** 8/50

## Per-Type Error Profile

| Type | Count | E01 | E03 | E04 | E05 | E06 | E07 | REF |
|------|-------|-----|-----|-----|-----|-----|-----|-----|
| local_reasoning | 10 | 1 | 1 | 2 | 0 | 6 | 0 | 0 |
| multi_document | 10 | 2 | 0 | 2 | 0 | 6 | 0 | 0 |
| negative | 10 | 0 | 0 | 0 | 1 | 0 | 0 | 8 |
| simple | 15 | 3 | 0 | 2 | 0 | 9 | 0 | 0 |
| table_extraction | 5 | 0 | 0 | 2 | 0 | 2 | 0 | 0 |

## Per-Question Classification

| ID | Type | Doc OK | Codes | Answer Preview |
|----|------|--------|-------|----------------|
| Q001 | simple | True | E06 | *   Question: "In RAG, qual è la differenza fondamentale tra |
| Q002 | simple | False | E01 | *   Question: "Nel paper RAG, il retriever usa DPR. Cosa dis |
| Q003 | simple | True | E06 | *   Question: "Quali sono i tre tipi di critique token gener |
| Q004 | simple | False | E01 | *   Role: Precise RAG assistant.
    *   Constraint: Use ONL |
| Q005 | simple | True | E06 | *   Role: Precise RAG assistant.
    *   Constraint: Use ONL |
| Q006 | simple | True | E06 | *   Question: "Nel Transformer, da quali due sotto-strati pr |
| Q007 | simple | True | E06 | *   Question: "Cosa sono i 'bag-of-freebies' in YOLOv7 e qua |
| Q008 | simple | True | E06 | *   Question: "Quale architettura backbone viene utilizzata  |
| Q009 | simple | True | E04,+E04 | *   Question: "Secondo il survey, quali sono le tre grandi a |
| Q010 | simple | True | LLM_ERROR | [ERROR LLM: Gemini HTTP 500 - {
  "error": {
    "code": 500 |
| Q011 | simple | True | E04,+E04 | *   Question: "Secondo Bommasani et al., quali sono le due p |
| Q012 | simple | True | E06 | *   Question: "Quali sono le quattro metriche principali pro |
| Q013 | simple | True | E06 | *   Question: "Quali sono i cinque domini specifici del benc |
| Q014 | simple | False | E01 | *   Question: "Come sono suddivise le 4.409 domande di CRAG  |
| Q015 | simple | True | E06 | *   Question: "Quali sono le 7 metriche di valutazione usate |
| Q016 | local_reasoning | True | E06 | *   Question: "In RAG, descrivi come vengono integrate la me |
| Q017 | local_reasoning | True | E04,+E04 | *   Question: "Descrivi come Self-RAG utilizza i retrieval t |
| Q018 | local_reasoning | True | E03,+E04 | *   Question: "Quali risultati emergono dagli ablation study |
| Q019 | local_reasoning | True | E04,+E04 | *   Question: "Spiega come funziona il meccanismo di scaled  |
| Q020 | local_reasoning | True | E06 | *   Question: "Qual è il contributo specifico della 'planned |
| Q021 | local_reasoning | True | E06 | *   Question: "Il survey discute i compromessi tra valutazio |
| Q022 | local_reasoning | True | E06 | *   Question: "Quali sono i rischi principali associati ai f |
| Q023 | local_reasoning | True | E06 | *   Question: "Come vengono calcolate faithfulness e answer  |
| Q024 | local_reasoning | False | E01 | *   Question: "CRAG analizza la degradazione della retrieval |
| Q025 | local_reasoning | True | E06 | *   Question: "HELM valuta 7 metriche su 42 scenari. Quali m |
| Q026 | multi_document | True | E04,+E04 | *   Question: "Confronta i meccanismi di retrieval in RAG or |
| Q027 | multi_document | False | E01 | *   Question: "Quali sono le principali differenze metodolog |
| Q028 | multi_document | False | E01 | *   Question: "Cosa distingue il dataset CRAG dalle domande  |
| Q029 | multi_document | True | E06 | *   Question: "In che modo Self-RAG e CRAG affrontano il pro |
| Q030 | multi_document | True | E06 | *   Role: Precise RAG assistant.
    *   Constraint: Use *ON |
| Q031 | multi_document | True | E04,+E04 | *   Question: "Quali metriche di valutazione sono comuni tra |
| Q032 | multi_document | True | E06 | *   Question: "Come vengono trattati i temi di bias e fairne |
| Q033 | multi_document | True | E06 | *   Question: "Sia Ragas che Self-RAG si occupano di faithfu |
| Q034 | multi_document | True | E06 | *   User Question: "Entrambi i paper (YOLOv7 e Transformer)  |
| Q035 | multi_document | True | E06 | *   Question: "Quali sono le differenze nel concetto di 'ret |
| Q036 | table_extraction | True | E04,+E04 | *   Question: "Nella tabella dei risultati BLEU sul WMT 2014 |
| Q037 | table_extraction | True | E04,+E04 | *   Question: "Nella tabella comparativa su MS COCO, quale A |
| Q038 | table_extraction | True | E06 | *   Question: "Secondo la tabella riassuntiva di HELM, quali |
| Q039 | table_extraction | True | E06 | *   Question: "Nelle tabelle di ablation di Self-RAG, quale  |
| Q040 | table_extraction | True | LLM_ERROR | [ERROR LLM: Gemini HTTP 500 - {
  "error": {
    "code": 500 |
| Q041 | negative | True | CORRECT_REFUSAL | *   Question: "Quanto e' costato addestrare Self-RAG in term |
| Q042 | negative | False | CORRECT_REFUSAL | *   Question: "Quale framework di deep learning (PyTorch, Te |
| Q043 | negative | True | LLM_ERROR | [ERROR LLM: Gemini HTTP 500 - {
  "error": {
    "code": 500 |
| Q044 | negative | True | E05 | *   Question: "Quale GPU e' stata usata per eseguire la valu |
| Q045 | negative | True | CORRECT_REFUSAL | *   Question: "Il paper RAG originale menziona 12 autori nel |
| Q046 | negative | True | CORRECT_REFUSAL | *   User Question: "Tree of Thoughts propone un metodo speci |
| Q047 | negative | True | CORRECT_REFUSAL | *   Question: "Nel paper Transformer, quale learning rate co |
| Q048 | negative | True | CORRECT_REFUSAL | *   Question: "In HELM, quale modello ha ottenuto il puntegg |
| Q049 | negative | False | CORRECT_REFUSAL | *   Role: Precise RAG assistant.
    *   Constraint 1: Use O |
| Q050 | negative | False | CORRECT_REFUSAL | *   Question: "Tree of Thoughts valuta la qualita' del retri |