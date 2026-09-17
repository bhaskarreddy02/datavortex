"""
Semantic Vector Search Engine Module
Social Engine NLP Semantic Understanding Layer
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import spacy
from sentence_transformers import SentenceTransformer

if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace', line_buffering=True)
    except Exception:
        pass

class SocialSemanticSearchIndex:
    """
    Lightweight vector search engine for social media posts.
    Indexes 384-dimensional dense semantic vectors and executes top-k
    cosine-similarity retrieval with rich metadata and entity enrichment.
    """
    def __init__(self, data_path="social_engine/data/cleaned_dataset.csv",
                 embeddings_path="social_engine/models/corpus_embeddings.npy",
                 model_name="all-MiniLM-L6-v2"):
        self.df = pd.read_csv(data_path)
        self.embedder = SentenceTransformer(model_name)
        
        if os.path.exists(embeddings_path):
            self.embeddings = np.load(embeddings_path)
        else:
            print(f"Computing embeddings for {len(self.df)} posts...")
            self.embeddings = self.embedder.encode(
                self.df['cleaned_text'].tolist(),
                batch_size=64,
                show_progress_bar=False,
                normalize_embeddings=True
            )
            np.save(embeddings_path, self.embeddings)
            
        # Lightweight NER for search-time entity enrichment
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            self.nlp = None

    def search(self, query: str, top_k: int = 5, min_score: float = 0.0):
        """
        Executes semantic vector search for a natural language query.
        Returns top_k most similar posts enriched with sentiment, topic, and entities.
        """
        # Encode and normalize query
        query_vec = self.embedder.encode([query], normalize_embeddings=True)[0]
        
        # Exact dot-product similarity (equivalent to cosine similarity on unit vectors)
        scores = np.dot(self.embeddings, query_vec)
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score < min_score:
                continue
                
            row = self.df.iloc[idx]
            text = row['post_text']
            
            # Extract entities from post
            entities = []
            if self.nlp:
                doc = self.nlp(row['cleaned_text'])
                entities = [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]
                
            results.append({
                'rank': len(results) + 1,
                'text_id': row['text_id'],
                'post_text': text,
                'similarity_score': round(score, 4),
                'sentiment': row['sentiment_label'],
                'topic': row['topic_category'],
                'entities': entities
            })
            
        return {
            'query': query,
            'top_k': len(results),
            'results': results
        }

def run_semantic_search_demo(outputs_dir="social_engine/outputs"):
    os.makedirs(outputs_dir, exist_ok=True)
    print("=" * 70)
    print("PHASE 9: SEMANTIC SEARCH ENGINE VERIFICATION")
    print("=" * 70)
    
    index = SocialSemanticSearchIndex()
    
    test_queries = [
        "people complaining about account hacking and password reset",
        "app crashes and technical bugs on phone",
        "loving the new features and design updates",
        "basketball and sports match results"
    ]
    
    all_search_results = []
    for q in test_queries:
        print(f"\nSearching for Query: \"{q}\"")
        res = index.search(q, top_k=3)
        all_search_results.append(res)
        
        for r in res['results']:
            ent_summary = ", ".join([f"{e['text']} ({e['label']})" for e in r['entities'][:3]]) or "None"
            print(f"  [{r['rank']}] Score: {r['similarity_score']:.4f} | Topic: {r['topic']} | Sent: {r['sentiment']}")
            print(f"      Text: \"{r['post_text']}\"")
            print(f"      Entities: {ent_summary}")
            
    out_file = os.path.join(outputs_dir, "semantic_search_demo.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(all_search_results, f, indent=2)
    print(f"\nSemantic search demo output exported to {out_file}")
    return all_search_results

if __name__ == '__main__':
    run_semantic_search_demo()
