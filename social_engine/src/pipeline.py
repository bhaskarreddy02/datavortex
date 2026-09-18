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
try:
    import spacy
except ImportError:
    spacy = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

try:
    from preprocessing import SocialTextPreprocessor
except ImportError:
    from social_engine.src.preprocessing import SocialTextPreprocessor

if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace', line_buffering=True)
    except Exception:
        pass

def derive_semantic_profile(sentiment: str, topic: str) -> str:
    """
    Generates a high-level derived social insight combining Sentiment and Topic.
    NOTE: This is an explicit rule-based derived interpretation, NOT a supervised label.
    """
    insight_matrix = {
        ('Negative', 'Feature_Feedback'): 'Negative Product / Feature Complaint (Feature friction detected)',
        ('Positive', 'Feature_Feedback'): 'Positive Feature Appreciation (User satisfaction with capability)',
        ('Neutral',  'Feature_Feedback'): 'Objective Feature Inquiry or Product Discussion',
        ('Negative', 'Technical_Issues'): 'Critical Technical Incident / System Degradation Alert',
        ('Positive', 'Technical_Issues'): 'Praise for Issue Resolution / Recovery Appreciation',
        ('Neutral',  'Technical_Issues'): 'Informational Technical Status / Diagnostic Inquiry',
        ('Negative', 'Account_Security'): 'Urgent Account Compromise or Security Vulnerability Concern',
        ('Positive', 'Account_Security'): 'Confirmation of Secure Recovery / Security Feature Endorsement',
        ('Neutral',  'Account_Security'): 'Routine Security Protocol or Credential Inquiry',
        ('Negative', 'Community_Discussion'): 'Negative Community Sentiment / Public Criticism',
        ('Positive', 'Community_Discussion'): 'Positive Community Engagement / Enthusiasm',
        ('Neutral',  'Community_Discussion'): 'General Social Commentary / Neutral Factual Discourse',
    }
    return insight_matrix.get((sentiment, topic), f"{sentiment} sentiment in {topic}")

class SocialEnginePipeline:
    """
    Unified end-to-end semantic intelligence engine for social media text.
    Combines text preprocessing, sentiment analysis, topic classification,
    confidence-aware triage, and semantic profiling.
    """
    def __init__(self,
                 models_dir="social_engine/models",
                 data_path="social_engine/data/cleaned_dataset.csv",
                 confidence_threshold: float = 0.55):
        self.preprocessor = SocialTextPreprocessor()
        self.models_dir = models_dir
        self.data_path = data_path
        self.confidence_threshold = confidence_threshold
        
        # 1. Load Pretrained Embedder
        print("Initializing Semantic Embedder (all-MiniLM-L6-v2)...")
        try:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Could not load sentence transformer: {e}")
            self.embedder = None
        
        # 2. Load Pretrained NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            self.nlp = None
            
        # 3. Load Topic & Sentiment Classifiers
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
            self.sent_model = None
            self.topic_model = None
            print("Warning: Model artifacts not found. Please train baseline models first.")
            
        # 4. Load Corpus Vectors for Nearest Neighbor Retrieval
        emb_matrix_path = os.path.join(models_dir, "corpus_embeddings.npy")
        if os.path.exists(emb_matrix_path) and os.path.exists(data_path):
            self.corpus_df = pd.read_csv(data_path)
            self.corpus_embeddings = np.load(emb_matrix_path)
            print(f"Loaded index of {len(self.corpus_embeddings)} corpus vectors.")
        else:
            self.corpus_df = None
            self.corpus_embeddings = None

    def predict_text(self, text: str) -> dict:
        """
        Clean competition inference interface:
        Input: Raw social text
        Output: Schema containing text, sentiment, sentiment_confidence,
                topic, topic_confidence, confidence_status, and derived_semantic_profile.
        """
        cleaned = self.preprocessor.clean_text(text)
        if self.tfidf is not None and self.sent_model is not None and self.topic_model is not None:
            features = self.tfidf.transform([cleaned])
            sent_pred = self.sent_model.predict(features)[0]
            sent_probs = self.sent_model.predict_proba(features)[0] if hasattr(self.sent_model, "predict_proba") else None
            sent_conf = float(np.max(sent_probs)) if sent_probs is not None else 0.75
            
            topic_pred = self.topic_model.predict(features)[0]
            topic_probs = self.topic_model.predict_proba(features)[0] if hasattr(self.topic_model, "predict_proba") else None
            topic_conf = float(np.max(topic_probs)) if topic_probs is not None else 0.75
        else:
            sent_pred = "Neutral"
            sent_conf = 0.50
            topic_pred = "Community_Discussion"
            topic_conf = 0.50

        # Confidence status check
        is_high = (sent_conf >= self.confidence_threshold) and (topic_conf >= self.confidence_threshold)
        status = "High Confidence" if is_high else "Low Confidence / Needs Review"
        
        # Rule-based derived semantic profile
        profile = derive_semantic_profile(sent_pred, topic_pred)
        
        return {
            "text": text,
            "sentiment": sent_pred,
            "sentiment_confidence": round(sent_conf, 4),
            "topic": topic_pred,
            "topic_confidence": round(topic_conf, 4),
            "confidence_status": status,
            "derived_semantic_profile": profile
        }

    def predict(self, text: str) -> dict:
        """Alias for predict_text."""
        return self.predict_text(text)

    def analyze(self, post_text: str, top_k_similar: int = 3) -> dict:
        """
        Executes full semantic understanding pipeline for a single post.
        Returns a rich structured telemetry payload including embeddings and entities.
        """
        cleaned = self.preprocessor.clean_text(post_text)
        pred_dict = self.predict_text(post_text)
        
        embedding_vec = None
        if self.embedder is not None:
            embedding_vec = self.embedder.encode([cleaned], normalize_embeddings=True)[0]
            
        entities = []
        if self.nlp is not None:
            doc = self.nlp(cleaned)
            for ent in doc.ents:
                entities.append({
                    "entity": ent.text,
                    "type": ent.label_
                })
                
        similar_posts = []
        if embedding_vec is not None and self.corpus_embeddings is not None and self.corpus_df is not None:
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
                "label": pred_dict["sentiment"],
                "confidence": pred_dict["sentiment_confidence"]
            },
            "topic": {
                "category": pred_dict["topic"],
                "confidence": pred_dict["topic_confidence"]
            },
            "confidence_status": pred_dict["confidence_status"],
            "derived_semantic_profile": pred_dict["derived_semantic_profile"],
            "entities": entities,
            "similar_posts": similar_posts
        }
        if embedding_vec is not None:
            output_payload["embedding"] = {
                "dimension": len(embedding_vec),
                "norm": round(float(np.linalg.norm(embedding_vec)), 4),
                "vector_head": [round(float(x), 4) for x in embedding_vec[:6]]
            }
        return output_payload

# Global helper function matching the exact user prompt requirement
_default_pipeline = None

def predict_text(text: str) -> dict:
    """
    Standalone function: predict_text(text) -> dict
    """
    global _default_pipeline
    if _default_pipeline is None:
        _default_pipeline = SocialEnginePipeline()
    return _default_pipeline.predict_text(text)

def run_pipeline_demo(outputs_dir="social_engine/outputs"):
    os.makedirs(outputs_dir, exist_ok=True)
    print("=" * 70)
    print("PHASE 10: COMPLETE UNIFIED SOCIAL ENGINE PIPELINE DEMO")
    print("=" * 70)
    
    pipeline = SocialEnginePipeline()
    
    test_posts = [
        "This update completely ruined the app.",
        "URGENT: Someone just changed my email and password without my permission! Locked out of my profile! #AccountSecurity 🚨",
        "The latest camera update on iPhone 15 is AMAZING!!! 😭🔥 loving the cinematic mode quality so much",
        "App keeps freezing on the payment gateway screen. It threw a 504 gateway timeout error when submitting checkout.",
        "Who else is watching the Lakers game tonight? D Wade is playing out of his mind! lololol",
        "game starts at 8pm tonight"
    ]
    
    demo_results = []
    for post in test_posts:
        print("\n" + "=" * 60)
        print(f"INPUT POST: \"{post}\"")
        res = pipeline.predict_text(post)
        demo_results.append(res)
        print(json.dumps(res, indent=2))
        
    out_file = os.path.join(outputs_dir, "pipeline_execution_telemetry.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(demo_results, f, indent=2)
    print(f"\nPipeline telemetry output successfully exported to {out_file}")
    return demo_results

if __name__ == '__main__':
    run_pipeline_demo()

# Backwards compatibility and class name aliases
SemanticUnderstandingPipeline = SocialEnginePipeline
