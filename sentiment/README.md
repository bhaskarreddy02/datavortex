# Sentiment & Semantic Understanding Layer (NLP)

This directory contains the **Sentiment & Semantic Understanding Layer** built for the **Social Engine** competition using **Dataset 2** (`Labeled_Social_NLP_Training_Data.csv`).

---

## 📁 Folder Contents

### 1. 📄 Executive Technical Report
- **[`Social_Engine_Semantic_Understanding_Report.pdf`](Social_Engine_Semantic_Understanding_Report.pdf)** *(2.86 MB)*: Full competition technical report with 17 embedded figures, benchmark tables, error taxonomy, and executive analysis.
- **[`Social_Engine_Semantic_Understanding_Report.md`](Social_Engine_Semantic_Understanding_Report.md)**: Markdown source document for the technical report.

### 2. 📓 Interactive Jupyter Notebook
- **[`Social_Engine_Semantic_Pipeline.ipynb`](Social_Engine_Semantic_Pipeline.ipynb)**: Complete end-to-end NLP Jupyter Notebook covering all 14 phases step-by-step:
  1. **Phase 1: Dataset Audit** — Distribution analysis, class imbalance, missing value checks.
  2. **Phase 2: Preprocessing** — Normalization, hashtag/emoji preservation, negation tagging, tokenization.
  3. **Phase 3: Leak-Free Stratified Split** — 80/10/10 train/val/test splits stratified by joint `(sentiment, topic)`.
  4. **Phase 4: Baselines** — TF-IDF + Logistic Regression, MultinomialNB, and LightGBM.
  5. **Phase 5: Deep Learning & Transformers** — Multi-task DistilBERT neural model predicting both sentiment and topic.
  6. **Phase 6: Unsupervised Topic Discovery** — Latent Dirichlet Allocation (LDA) & NMF discovering emergent social themes.
  7. **Phase 7: Named Entity Recognition** — spaCy NER extracting entities (PERSON, ORG, GPE, PRODUCT).
  8. **Phase 8: Semantic Embeddings & Vector Search** — `all-MiniLM-L6-v2` dense vectors with cosine similarity and FAISS vector index.
  9. **Phase 9: Unified Semantic Pipeline** — End-to-end `SemanticUnderstandingPipeline` accepting raw text and returning full structured intelligence.
  10. **Phase 10: Quantitative Evaluation & Comparison** — Comprehensive comparison table across all models.
  11. **Phase 11: Error Analysis** — Confusion matrices and misclassification inspection.
  12. **Phase 12: Production Readiness** — Latency benchmarking, telemetry logging, and model export.
  13. **Phase 13: Executive Documentation** — Comprehensive final system summary.

### 3. 🗄️ Dataset
- **`Labeled_Social_NLP_Training_Data.csv`**: The official training dataset containing 9,000 labeled social media posts (`text_id`, `post_text`, `sentiment_label`, `topic_category`).

### 4. 🖼️ Architecture & Diagrams
- **`social_engine_structure.png`** / **`social_engine_structure-1.png`**: Multi-dimensional semantic architecture diagram.

### 5. 🛠️ Utilities
- **`generate_notebook.py`**: Python script used to construct the interactive notebook.

---

## 🔗 Modular Python Codebase
The production-grade modular Python package, trained model artifacts, outputs, and visualization figures are also available in:
- **`../social_engine/`**
  - `social_engine/src/`: Modular Python scripts (`preprocessing.py`, `baseline_models.py`, `transformers_pipeline.py`, `topic_discovery.py`, `ner.py`, `embeddings.py`, `semantic_search.py`, `pipeline.py`, etc.)
  - `social_engine/outputs/`: Evaluation metrics JSONs, comparison CSVs, telemetry logs.
  - `social_engine/figures/`: High-resolution figures and confusion matrices.
  - `social_engine/models/`: Serialized models and TF-IDF vectorizers.

---

## 🚀 Quickstart

To run the interactive notebook:
```bash
jupyter notebook Social_Engine_Semantic_Pipeline.ipynb
```
All datasets are located directly in this folder.
