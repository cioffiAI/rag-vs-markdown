---
title: "Progetti personali AI & Co - Progetti ricerca AI PDF"
source: "https://chatgpt.com/g/g-p-69f1b453dd08819192908e2d2f26cd60-progetti-personali-ai-co/c/6a01d451-95f8-8384-ac7c-a60671310e75"
author:
published:
created: 2026-05-11
description: "ChatGPT è il tuo chatbot IA per l'uso quotidiano. Chatta con l'IA più avanzata per esplorare idee, risolvere problemi e imparare più velocemente."
tags:
  - "clippings"
---
### Idea

Costruire e testare un sistema locale che prende PDF/documenti, li trasforma in Markdown strutturato, li indicizza e poi permette interrogazioni con risposte citate.

Non deve essere “chatta col PDF”, che è già visto mille volte. Il punto di ricerca deve essere:

> **Un documento prima compilato in Markdown ragionato produce risposte migliori di un RAG fatto direttamente sui chunk del PDF?**

Questo si collega molto bene al tuo contesto: AI, workflow assistiti, software tool, automazione personale e portfolio pubblico sono già centrali nel tuo profilo.  
In più, tra le tue competenze già presenti ci sono Markdown, agent workflow, ragionamento procedurale, documentazione e validazione; mentre tra i gap da migliorare ci sono testing, deployment, Git/GitHub e clean architecture. Questo progetto li tocca quasi tutti.

### Perché è forte per il portfolio

Perché non dimostra solo “uso LangChain/Ollama”. Dimostra:

| Competenza | Come la dimostri |
| --- | --- |
| RAG | chunking, embeddings, retrieval, risposta con fonti |
| Data preparation | conversione PDF → Markdown pulito |
| Valutazione | benchmark tra pipeline diverse |
| Engineering | CLI o piccola app Streamlit/Gradio |
| Documentazione | report tecnico con limiti ed errori |
| Uso realistico dell’AI | l’AI aiuta, ma tu misuri e correggi |

### Domanda di ricerca

> **Quanto migliora la qualità delle risposte se prima trasformo documenti lunghi in Markdown strutturato, invece di fare RAG direttamente sul PDF?**

### Setup minimo

Crea 3 pipeline:

1. **Baseline A — PDF diretto**
	- Estrai testo dal PDF.
		- Chunk semplice.
		- Embedding.
		- Retrieval.
		- Risposta.
2. **Pipeline B — PDF → Markdown compilato**
	- Estrai testo.
		- Trasformi in Markdown pulito con sezioni, titoli, tabelle, concetti.
		- Chunk sul Markdown.
		- Retrieval.
		- Risposta.
3. **Pipeline C — Markdown + schede concettuali**
	- Oltre al Markdown, generi schede:
		- concetti principali;
				- definizioni;
				- relazioni;
				- limiti;
				- esempi.
		- Retrieval ibrido su testo + schede.

### Dataset iniziale

Usa documenti non sensibili:

- 5 PDF tecnici pubblici;
- 5 tuoi PDF/progetti già pubblicabili;
- 2 file del tuo AI Vault, se non contengono dati sensibili;
- 1 documento “sporco”, pieno di tabelle o formattazione complicata.

Totale: **10-12 documenti bastano**.

### Parte che devi fare tu, non l’AI

Questa è la parte che rende il progetto credibile:

1. Creare manualmente **50 domande gold standard**:
	- 20 domande semplici;
		- 20 domande multi-sezione;
		- 10 domande trabocchetto, dove il documento non contiene davvero la risposta.
2. Scrivere manualmente la risposta corretta attesa, anche breve.
3. Valutare gli output con una griglia:

| Metrica | Scala |
| --- | --- |
| Risposta corretta | 0/1 |
| Fonte corretta | 0/1 |
| Inventata/allucinata | 0/1 |
| Risposta completa | 0-2 |
| Chiarezza | 0-2 |

4. Fare un report con esempi reali:
	- dove il PDF diretto fallisce;
		- dove il Markdown migliora;
		- dove anche il Markdown fallisce.

### Output finale da mettere su GitHub

Repository:

```
local-evidence-rag-lab/├── README.md├── docs/│   ├── architecture.md│   ├── evaluation_protocol.md│   ├── results.md│   └── limitations.md├── src/│   ├── ingest_pdf.py│   ├── compile_markdown.py│   ├── build_index.py│   ├── query.py│   └── evaluate.py├── data/│   ├── sample_docs/│   └── gold_questions.csv├── reports/│   └── benchmark_results.md├── tests/└── Makefile
```

Frase portfolio:

> Ho costruito un benchmark locale per confrontare RAG diretto su PDF, RAG su Markdown compilato e RAG con schede concettuali, misurando accuratezza, citazioni corrette e allucinazioni su un dataset manualmente annotato.