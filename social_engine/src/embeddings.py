"""
Semantic Embeddings & Similarity Engine Module
Social Engine NLP Semantic Understanding Layer
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace', line_buffering=True)
    except Exception:
        pass

class SocialSemanticEmbedder:
    """
    High-performance semantic embedding and similarity module.
    Encodes social text into unit-normalized dense vectors (384 dimensions).
    """
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.embedder = SentenceTransformer(model_name)

    def encode(self, texts, batch_size=64, normalize=True):
        if isinstance(texts, str):
            texts = [texts]
        embeddings = self.embedder.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=normalize
        )
        return embeddings

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        emb_a = self.encode(text_a)[0]
        emb_b = self.encode(text_b)[0]
        # Cosine similarity is dot product when vectors are L2-normalized
        sim = float(np.dot(emb_a, emb_b))
        return sim

    def find_near_duplicates(self, embeddings, df, threshold=0.92, max_pairs=5):
        """Identifies near-duplicate posts across the corpus using vector cosine similarity."""
        # Sample subset for rapid quadratic pairwise distance check
        sample_n = min(1000, len(embeddings))
        sub_emb = embeddings[:sample_n]
        sim_matrix = np.dot(sub_emb, sub_emb.T)
        np.fill_diagonal(sim_matrix, 0)
        
        near_dupes = []
        pairs_seen = set()
        
        for i in range(sample_n):
            for j in range(i + 1, sample_n):
                score = float(sim_matrix[i, j])
                if score >= threshold:
                    text_i = df.iloc[i]['post_text']
                    text_j = df.iloc[j]['post_text']
                    if text_i != text_j and (text_i, text_j) not in pairs_seen:
                        pairs_seen.add((text_i, text_j))
                        near_dupes.append({
                            'post_1': text_i,
                            'post_2': text_j,
                            'cosine_similarity': round(score, 4),
                            'topic_1': df.iloc[i]['topic_category'],
                            'topic_2': df.iloc[j]['topic_category'],
                            'sentiment_1': df.iloc[i]['sentiment_label'],
                            'sentiment_2': df.iloc[j]['sentiment_label']
                        })
                        if len(near_dupes) >= max_pairs:
                            return near_dupes
        return near_dupes

def run_embeddings_demo(data_path="social_engine/data/cleaned_dataset.csv",
                        models_dir="social_engine/models",
                        outputs_dir="social_engine/outputs"):
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)
    
    print("=" * 70)
    print("PHASE 8: SEMANTIC EMBEDDINGS & SIMILARITY VERIFICATION")
    print("=" * 70)
    
    embedder = SocialSemanticEmbedder()
    df = pd.read_csv(data_path)
    
    # 1. Semantic Similarity Demonstration (Synonymous intent with disparate lexical tokens)
    demo_pairs = [
        ("My payment isn't going through", "Transaction keeps failing"),
        ("I cannot login to my account, password reset link is broken", "Locked out of my profile and recovery email is not working"),
        ("The new interface looks incredible, loving the fresh design", "Super happy with the UI update, great aesthetic"),
        ("The app crashes whenever I open the camera", "The weather is very sunny in Madrid today") # Control negative pair
    ]
    
    similarity_demo = []
    print("\nDemonstrating Semantic Equivalence Across Different Wordings:")
    for text_a, text_b in demo_pairs:
        sim = embedder.compute_similarity(text_a, text_b)
        similarity_demo.append({
            'text_a': text_a,
            'text_b': text_b,
            'cosine_similarity': round(sim, 4),
            'interpretation': "Strong Semantic Match" if sim > 0.70 else ("Moderate" if sim > 0.40 else "Dissimilar/Unrelated")
        })
        print(f"Text A: \"{text_a}\"")
        print(f"Text B: \"{text_b}\"")
        print(f"--> Cosine Similarity: {sim:.4f} ({similarity_demo[-1]['interpretation']})\n")
        
    # 2. Encode all posts and save embedding matrix for vector search
    emb_path = os.path.join(models_dir, "corpus_embeddings.npy")
    if os.path.exists(emb_path):
        print(f"Loading pre-computed corpus embeddings from {emb_path}...")
        embeddings = np.load(emb_path)
    else:
        print(f"Computing dense normalized embeddings for all {len(df)} corpus posts...")
        embeddings = embedder.encode(df['cleaned_text'].tolist(), batch_size=64)
        np.save(emb_path, embeddings)
        print(f"Saved {embeddings.shape} normalized embedding matrix to {emb_path}")
    
    # 3. Near-duplicate detection
    print("\nScanning for near-duplicate posts in Dataset 2...")
    near_duplicates = embedder.find_near_duplicates(embeddings, df, threshold=0.90)
    for idx, pair in enumerate(near_duplicates, 1):
        print(f"Pair {idx} (Sim: {pair['cosine_similarity']}):")
        print(f"  P1: \"{pair['post_1'][:85]}...\"")
        print(f"  P2: \"{pair['post_2'][:85]}...\"")
        
    report = {
        'embedding_model': embedder.model_name,
        'embedding_dimension': int(embeddings.shape[1]),
        'total_vectors_encoded': int(embeddings.shape[0]),
        'semantic_equivalence_demo': similarity_demo,
        'near_duplicate_samples': near_duplicates
    }
    
    out_file = os.path.join(outputs_dir, "embeddings_evaluation.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"Embeddings evaluation report exported to {out_file}")
    return report

if __name__ == '__main__':
    run_embeddings_demo()
