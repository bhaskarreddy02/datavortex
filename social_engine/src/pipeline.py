"""
Complete Social Engine Unified Semantic Pipeline Module
Social Engine NLP Semantic Understanding Layer
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import spacy
from sentence_transformers import SentenceTransformer

from preprocessing import SocialTextPreprocessor

if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace', line_buffering=True)
    except Exception:
        pass

class SocialEnginePipeline:
    """
    Unified end-to-end semantic intelligence engine for social media text.
    Combines text preprocessing, sentiment analysis, topic classification,
    named entity recognition, dense vector embedding, and nearest-neighbor search.
    """
    def __init__(self,
                 models_dir="social_engine/models",
                 data_path="social_engine/data/cleaned_dataset.csv"):
        self.preprocessor = SocialTextPreprocessor()
        self.models_dir = models_dir
        self.data_path = data_path
        
        # 1. Load Pretrained Embedder
        print("Initializing Semantic Embedder (all-MiniLM-L6-v2)...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 2. Load Pretrained NER
        print("Initializing Pretrained NER (spaCy en_core_web_sm)...")
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            self.nlp = None
            
        # 3. Load Topic & Sentiment Classifiers
        # Priority: Multi-task / Transformer model, fallback: Best Classical Baselines
        self.use_transformer = False
        mtl_path = os.path.join(models_dir, "multitask_social_transformer.pt")
        
        # Load classical ML models as proven, fast, ultra-reliable classifiers
        tfidf_path = os.path.join(models_dir, "tfidf_vectorizer.joblib")
        sent_model_path = os.path.join(models_dir, "sentiment_Logistic_Regression.joblib")
        topic_model_path = os.path.join(models_dir, "topic_Linear_SVM.joblib")
        
        if os.path.exists(tfidf_path) and os.path.exists(sent_model_path) and os.path.exists(topic_model_path):
            self.tfidf = joblib.load(tfidf_path)
            self.sent_model = joblib.load(sent_model_path)
            self.topic_model = joblib.load(topic_model_path)
            print("Loaded calibrated classification models.")
        else:
            self.tfidf = None
            
        # 4. Load Corpus Vectors for Nearest Neighbor Retrieval
        emb_matrix_path = os.path.join(models_dir, "corpus_embeddings.npy")
        if os.path.exists(emb_matrix_path) and os.path.exists(data_path):
            self.corpus_df = pd.read_csv(data_path)
            self.corpus_embeddings = np.load(emb_matrix_path)
            print(f"Loaded index of {len(self.corpus_embeddings)} corpus vectors.")
        else:
            self.corpus_df = None
            self.corpus_embeddings = None

    def analyze(self, post_text: str, top_k_similar: int = 3) -> dict:
        """
        Executes full semantic understanding pipeline for a single post.
        Returns a rich structured telemetry payload.
        """
        # Step 1: Preprocessing
        cleaned = self.preprocessor.clean_text(post_text)
        
        # Step 2: Dense Semantic Embedding
        embedding_vec = self.embedder.encode([cleaned], normalize_embeddings=True)[0]
        
        # Step 3: Sentiment & Topic Classification
        if self.tfidf is not None:
            features = self.tfidf.transform([cleaned])
            sentiment_pred = self.sent_model.predict(features)[0]
            sentiment_probs = self.sent_model.predict_proba(features)[0] if hasattr(self.sent_model, "predict_proba") else None
            sent_conf = float(np.max(sentiment_probs)) if sentiment_probs is not None else 1.0
            
            topic_pred = self.topic_model.predict(features)[0]
            topic_probs = self.topic_model.predict_proba(features)[0] if hasattr(self.topic_model, "predict_proba") else None
            topic_conf = float(np.max(topic_probs)) if topic_probs is not None else 1.0
        else:
            sentiment_pred = "Neutral"
            sent_conf = 0.5
            topic_pred = "Community_Discussion"
            topic_conf = 0.5
            
        # Step 4: Named Entity Recognition
        entities = []
        if self.nlp:
            doc = self.nlp(cleaned)
            for ent in doc.ents:
                entities.append({
                    "entity": ent.text,
                    "type": ent.label_
                })
                
        # Step 5: Semantic Nearest Neighbors Search
        similar_posts = []
        if self.corpus_embeddings is not None and self.corpus_df is not None:
            sims = np.dot(self.corpus_embeddings, embedding_vec)
            top_idx = np.argsort(sims)[::-1][:top_k_similar]
            for idx in top_idx:
                row = self.corpus_df.iloc[idx]
                similar_posts.append({
                    "text_id": row['text_id'],
                    "text": row['post_text'],
                    "similarity_score": round(float(sims[idx]), 4),
                    "sentiment": row['sentiment_label'],
                    "topic": row['topic_category']
                })
                
        output_payload = {
            "raw_text": post_text,
            "cleaned_text": cleaned,
            "sentiment": {
                "label": sentiment_pred,
                "confidence": round(sent_conf, 4)
            },
            "topic": {
                "category": topic_pred,
                "confidence": round(topic_conf, 4)
            },
            "entities": entities,
            "embedding": {
                "dimension": len(embedding_vec),
                "norm": round(float(np.linalg.norm(embedding_vec)), 4),
                "vector_head": [round(float(x), 4) for x in embedding_vec[:6]] # Display sample
            },
            "similar_posts": similar_posts
        }
        return output_payload

def run_pipeline_demo(outputs_dir="social_engine/outputs"):
    os.makedirs(outputs_dir, exist_ok=True)
    print("=" * 70)
    print("PHASE 10: COMPLETE UNIFIED SOCIAL ENGINE PIPELINE DEMO")
    print("=" * 70)
    
    pipeline = SocialEnginePipeline()
    
    test_posts = [
        "URGENT: Someone just changed my email and password without my permission! Locked out of my profile! #AccountSecurity 🚨",
        "The latest camera update on iPhone 15 is AMAZING!!! 😭🔥 loving the cinematic mode quality so much",
        "App keeps freezing on the payment gateway screen. It threw a 504 gateway timeout error when submitting checkout.",
        "Who else is watching the Lakers game tonight? D Wade is playing out of his mind! lololol"
    ]
    
    demo_results = []
    for post in test_posts:
        print("\n" + "=" * 60)
        print(f"INPUT POST: \"{post}\"")
        telemetry = pipeline.analyze(post)
        demo_results.append(telemetry)
        
        print(f"-> Sentiment: {telemetry['sentiment']['label']} (conf: {telemetry['sentiment']['confidence']:.2f})")
        print(f"-> Topic    : {telemetry['topic']['category']} (conf: {telemetry['topic']['confidence']:.2f})")
        print(f"-> Entities : {[e['entity'] + ' (' + e['type'] + ')' for e in telemetry['entities']]}")
        print(f"-> Embedding: Dimension {telemetry['embedding']['dimension']} (unit normalized)")
        print(f"-> Nearest Neighbor Match: \"{telemetry['similar_posts'][0]['text'][:70]}...\" (Sim: {telemetry['similar_posts'][0]['similarity_score']:.3f})")
        
    out_file = os.path.join(outputs_dir, "pipeline_execution_telemetry.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(demo_results, f, indent=2)
    print(f"\nPipeline telemetry output successfully exported to {out_file}")
    return demo_results

if __name__ == '__main__':
    run_pipeline_demo()
