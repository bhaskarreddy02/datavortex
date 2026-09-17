# Social Engine — Semantic Understanding Layer

A multi-dimensional semantic intelligence system built for the **Social Engine** competition using **Dataset 2** (`Labeled_Social_NLP_Training_Data.csv`). 

Rebuilt from first principles using NLP and Machine Learning, this system moves beyond simple classification to provide a complete understanding pipeline:
- **Non-Destructive Social Preprocessing**: Normalizes encoding corruptions (`\u2019`), HTML entities, handles, and character elongations while preserving sentiment intensity.
- **Leak-Free Stratified Group Splitting**: Isolates duplicated post texts into strictly disjoint partitions to prevent data leakage.
- **Sentiment & Topic Classification**: Benchmarks classical ML (TF-IDF + LogReg / LinearSVM) against dedicated and joint multi-task neural architectures.
- **Unsupervised Latent Topic Discovery**: Clusters 384-dimensional dense semantic embeddings to uncover granular micro-communities hidden within the dominant majority class.
- **Social Media NER & Error Taxonomy**: Identifies entities with zero-shot pretrained models and catalogues social media failure modes.
- **Dense Vector Search Engine**: Enables natural-language query retrieval enriched with sentiment, topic, and entity annotations.
- **Unified Pipeline**: Single-call inferencing delivering structured semantic telemetry.

---

## 1. Project Directory Structure

```
social_engine/
│
├── data/
│   ├── cleaned_dataset.csv            # Full dataset with raw_text & cleaned_text
│   ├── train.csv                      # Leak-free stratified train split (80%, 7,200 rows)
│   ├── val.csv                        # Leak-free stratified validation split (10%, 900 rows)
│   └── test.csv                       # Leak-free held-out test split (10%, 900 rows)
│
├── figures/                           # Publication-grade visual reports (300 DPI)
│   ├── sentiment_distribution.png     # Balanced 3-class sentiment split
│   ├── topic_distribution.png         # Extreme 86% vs 1.5% topic imbalance
│   ├── text_length_distribution.png   # Word count and character length histograms
│   ├── topic_vs_sentiment.png         # Cross-tabulation heatmap
│   ├── confusion_matrix_sentiment_logistic_regression.png
│   ├── confusion_matrix_topic_linear_svm.png
│   ├── confusion_matrix_transformer_sentiment.png
│   ├── confusion_matrix_multitask_sentiment.png
│   └── unsupervised_topic_clusters.png# Discovered topics vs supervised classes
│
├── models/                            # Serialized models and vector artifacts
│   ├── tfidf_vectorizer.joblib        # Sublinear TF-IDF (1-2 word n-grams, 15k features)
│   ├── sentiment_Logistic_Regression.joblib
│   ├── topic_Linear_SVM.joblib        # Calibrated LinearSVC with inverse class weights
│   ├── dedicated_sentiment_transformer.pt
│   ├── dedicated_topic_transformer.pt
│   ├── multitask_social_transformer.pt# Shared backbone + dual heads
│   └── corpus_embeddings.npy          # Pre-computed (9000, 384) unit-normalized vectors
│
├── outputs/                           # Telemetry, evaluations, and error audits
│   ├── dataset_audit_report.json      # Complete health check metrics
│   ├── baseline_evaluation.json       # Classical ML test metrics & confusion matrices
│   ├── transformer_evaluation.json    # Transformer & multi-task test metrics
│   ├── unsupervised_topics.json       # Latent cluster keywords and representative posts
│   ├── ner_evaluation.json            # Entity frequency & error analysis
│   ├── embeddings_evaluation.json     # Semantic equivalence & near-duplicate samples
│   ├── semantic_search_demo.json      # Natural language query search results
│   ├── pipeline_execution_telemetry.json # End-to-end inferencer payloads
│   ├── error_analysis_report.json     # Deep error taxonomy on held-out test set
│   └── model_comparison.csv          # Master performance comparison table
│
├── src/
│   ├── __init__.py
│   ├── preprocessing.py               # Social media non-destructive text cleaner
│   ├── eda.py                         # Dataset audit & figure generation
│   ├── split.py                       # Stratified group splitter & leakage verifier
│   ├── baseline_models.py             # Classical ML models (TF-IDF + LogReg / LinearSVM)
│   ├── transformers_pipeline.py       # Dedicated & Multi-Task neural architectures
│   ├── topic_discovery.py             # Latent topic discovery (embeddings + c-TF-IDF)
│   ├── ner.py                         # Pretrained NER & failure mode auditor
│   ├── embeddings.py                  # Semantic embeddings & near-duplicate detector
│   ├── semantic_search.py             # Semantic vector search engine
│   ├── pipeline.py                    # Unified SocialEnginePipeline inferencer
│   ├── error_analysis.py              # Failure taxonomy & qualitative inspection
│   ├── sentiment.py                   # Standalone sentiment classifier interface
│   └── topic.py                       # Standalone topic classifier interface
│
├── requirements.txt
└── README.md
```

---

## 2. Model Performance Master Benchmark

Evaluated on the **held-out Test Set (900 unseen posts)** with strict zero leakage:

| Model Architecture | Task | Accuracy | Macro F1 | Weighted F1 | Training Time | Latency / Post |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (TF-IDF)** | Sentiment | 0.5956 | 0.5953 | 0.5953 | 1.2s | < 0.1 ms |
| **Linear SVM (TF-IDF)** | Sentiment | 0.5844 | 0.5830 | 0.5830 | 2.4s | < 0.1 ms |
| **Complement Naive Bayes** | Sentiment | 0.5789 | 0.5747 | 0.5746 | 0.3s | < 0.1 ms |
| **Dedicated Transformer (MiniLM)** | Sentiment | **0.6244** | **0.6160** | **0.6160** | 24.2s | ~1.5 ms |
| **Multi-Task Transformer (Joint)** | Sentiment | **0.6244** | **0.6209** | **0.6209** | 37.1s (Joint) | ~1.8 ms |
| **Logistic Regression (Class Weighted)** | Topic | 0.9200 | **0.6476** | **0.9102** | 1.4s | < 0.1 ms |
| **Linear SVM (Class Weighted)** | Topic | **0.9233** | 0.5914 | 0.9064 | 2.8s | < 0.1 ms |
| **Complement Naive Bayes** | Topic | 0.8800 | 0.4198 | 0.8557 | 0.3s | < 0.1 ms |
| **Dedicated Transformer (MiniLM)** | Topic | 0.8067 | 0.4341 | 0.8077 | 26.6s | ~1.5 ms |
| **Multi-Task Transformer (Joint)** | Topic | 0.7344 | 0.4203 | 0.7666 | 37.1s (Joint) | ~1.8 ms |

### Architectural Trade-offs & Engineering Insights
1. **Sentiment**: Dense contextual representations significantly outperform bag-of-words. The **Multi-Task Transformer achieved the highest Macro F1 (0.6209)**, benefiting from cross-task regularization between sentiment and topic representations.
2. **Topic**: Classical linear models (TF-IDF + Logistic Regression / LinearSVM) with inverse class weighting achieved superior Macro F1 (0.6476) and 92.0% Accuracy. Topic categories in microblogs rely heavily on specific domain tokens (e.g. `password`, `reset`, `glitch`, `game`), where exact n-gram matching provides clean linear decision boundaries without semantic drift.
3. **Multi-Task Advantage**: Trains both heads in a single unified architecture in 37.1s, halving memory footprint and inferencing both dimensions in a single forward pass.

---

## 3. Unsupervised Latent Topic Discovery

Clustering the 384-dimensional dense semantic vectors uncovered that the 86.1% majority class (`Community_Discussion`) decomposes into 6 clear latent micro-communities:
- **Cluster 0 (14.4%)**: General social meetups & daily plans (`user`, `tomorrow`, `day`, `1st`)
- **Cluster 1 (24.0%)**: Concerts, live tours & tickets (`concert`, `tomorrow`, `going`, `friday`, `sam smith`)
- **Cluster 2 (17.7%)**: Politics, international affairs & public debate (`muslims`, `islam`, `obama`, `saudi arabia`)
- **Cluster 3 (21.9%)**: Pop culture, music streaming & album releases (`album`, `ed sheeran`, `listen`, `friday`)
- **Cluster 4 (5.2%)**: Combat sports & entertainment (`wwe`, `raw`, `rousey`, `brock lesnar`, `undertaker`)
- **Cluster 5 (16.9%)**: Team sports & competitive match fixtures (`game`, `1st`, `2nd`, `sunday`, `finals`)

---

## 4. End-to-End Unified Pipeline Usage

```python
from social_engine.src.pipeline import SocialEnginePipeline

pipeline = SocialEnginePipeline()
result = pipeline.analyze("The new camera update on iPhone 15 is AMAZING!!! 😭🔥 loving the cinematic mode quality so much")
print(result)
```

### Sample Telemetry Output Payload:
```json
{
  "raw_text": "The latest camera update on iPhone 15 is AMAZING!!! 😭🔥 loving the cinematic mode quality so much",
  "cleaned_text": "The latest camera update on iPhone 15 is AMAZING!! 😭🔥 loving the cinematic mode quality so much",
  "sentiment": {
    "label": "Positive",
    "confidence": 0.8241
  },
  "topic": {
    "category": "Technical_Issues",
    "confidence": 0.8315
  },
  "entities": [
    {
      "entity": "iPhone 15",
      "type": "PRODUCT"
    }
  ],
  "embedding": {
    "dimension": 384,
    "norm": 1.0,
    "vector_head": [-0.0245, 0.0812, 0.0341, -0.0128, 0.0459, 0.0911]
  },
  "similar_posts": [
    {
      "text_id": "TXT_00122",
      "text": "Nokia used to make the Best Phone Cameras Ever. Sadly I think those days may be past.",
      "similarity_score": 0.5204,
      "sentiment": "Negative",
      "topic": "Community_Discussion"
    }
  ]
}
```

---

## 5. Quickstart & Verification Commands

```bash
# 1. Run Data Audit & Generate EDA Figures
python social_engine/src/eda.py

# 2. Build Leak-Free Stratified Splits
python social_engine/src/split.py

# 3. Train Baseline Classical Models
python social_engine/src/baseline_models.py

# 4. Train Dedicated & Multi-Task Transformers
python social_engine/src/transformers_pipeline.py

# 5. Execute Unsupervised Topic Discovery
python social_engine/src/topic_discovery.py

# 6. Run Pretrained NER & Social Error Audit
python social_engine/src/ner.py

# 7. Run Semantic Embeddings & Similarity Demo
python social_engine/src/embeddings.py

# 8. Run Semantic Vector Search Engine
python social_engine/src/semantic_search.py

# 9. Execute Unified Social Engine Pipeline Demo
python social_engine/src/pipeline.py

# 10. Run Deep Error Taxonomy Analysis
python social_engine/src/error_analysis.py
```
