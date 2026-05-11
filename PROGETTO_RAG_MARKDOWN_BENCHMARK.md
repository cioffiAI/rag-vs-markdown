
---

## 🗺️ 8. Roadmap di Implementazione (Step-by-Step)
1. [ ] Setup ambiente virtuale + installazione Ollama + verifica modello leggero
2. [ ] Raccolta e organizzazione dei 10-12 PDF in `data/raw/`
3. [ ] Script di estrazione (`extract.py`) con `PyMuPDF`
4. [ ] Script di conversione Markdown (`compile_markdown.py`) con euristiche base
5. [ ] Pipeline di indicizzazione (`build_index.py`) con chunking + embedding + ChromaDB
6. [ ] Modulo di query e generazione (`query.py`) con prompt templating e logging
7. [ ] Creazione manuale del `gold_questions.csv`
8. [ ] Script di valutazione (`evaluate.py`) + calcolo score composito
9. [ ] Generazione report finale (`reports/benchmark_results.md`) con esempi qualitativi
10. [ ] Revisione, commit strategici su Git, stesura `README.md` e `limitations.md`

---

## 🧠 9. Learning Outcomes & Valore per il Portfolio
**Competenze sviluppate:**
- RAG fundamentals (chunking, embedding, retrieval, context injection)
- Data engineering & cleaning (PDF → testo → MD strutturato)
- Scientific evaluation design (gold standard, metriche composite, validità interna)
- Reproducible research (seed, config, versioning, logging)
- Prompt engineering & citation forcing
- Critical analysis dei failure mode

**Elevator Pitch per il Portfolio:**  
> *"Ho progettato e implementato un benchmark locale per confrontare tre strategie di Retrieval-Augmented Generation su documenti PDF: estrazione diretta, preprocessing in Markdown strutturato e arricchimento con schede concettuali. Ho valutato accuratezza, fedeltà alle fonti e tasso di allucinazioni su un dataset di 50 domande annotate manualmente, dimostrando empiricamente il valore della knowledge compilation preliminare."*

---

## 📚 10. Riferimenti Bibliografici (APA 7ª ed.) & Integrità Accademica
- Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *Advances in Neural Information Processing Systems, 33*, 1939–1952. https://doi.org/10.48550/arXiv.2005.11401
- Gao, Y., et al. (2023). Precise Zero-Shot Dense Retrieval without Relevance Labels. *Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics*, 1762–1780. https://doi.org/10.18653/v1/2023.acl-long.100
- Mialon, G., et al. (2023). Augmented Language Models: A Survey. *Transactions on Machine Learning Research*. https://doi.org/10.48550/arXiv.2302.07842
- Bai, Y., et al. (2023). Scaling Instruction-Finetuned Language Models. *arXiv preprint*. https://doi.org/10.48550/arXiv.2212.09093

🔒 **Nota sull'integrità accademica:**  
Leggi almeno gli abstract originali dei paper citati. Parafrasa con parole tue, cita sempre le fonti e dichiara esplicitamente nel report quali passaggi sono stati assistiti da AI e quali sono stati validati manualmente. La trasparenza metodologica è parte del rigore scientifico.

---
*Documento generato per supporto accademico. Ultimo aggiornamento: 2024. Mantenere versioning tramite Git.*