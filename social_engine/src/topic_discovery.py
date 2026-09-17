"""
Unsupervised Topic Discovery & Latent Semantic Modelling Module
Social Engine NLP Semantic Understanding Layer
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from sentence_transformers import SentenceTransformer

if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace', line_buffering=True)
    except Exception:
        pass

def extract_ctfidf_keywords(docs_per_topic, top_n=10):
    """
    Computes class-based TF-IDF (c-TF-IDF) across discovered clusters
    to extract the most distinctive, representative keywords for each topic.
    """
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words='english',
        min_df=2,
        max_features=5000
    )
    X = vectorizer.fit_transform(docs_per_topic)
    words = vectorizer.get_feature_names_out()
    
    topic_keywords = {}
    for topic_id in range(X.shape[0]):
        row = X[topic_id].toarray().flatten()
        top_indices = row.argsort()[-top_n:][::-1]
        top_words = [words[idx] for idx in top_indices if row[idx] > 0]
        topic_keywords[topic_id] = top_words
    return topic_keywords

def discover_latent_topics(data_path="social_engine/data/cleaned_dataset.csv",
                            outputs_dir="social_engine/outputs",
                            figures_dir="social_engine/figures",
                            n_clusters=6,
                            random_state=42):
    os.makedirs(outputs_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    
    print("=" * 70)
    print("PHASE 6: UNSUPERVISED TOPIC DISCOVERY & LATENT SEMANTIC MODELLING")
    print("=" * 70)
    
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} posts for unsupervised discovery.")
    
    # 1. Generate dense semantic sentence embeddings
    print("Encoding posts using sentence-transformers/all-MiniLM-L6-v2 (384-d)...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = embedder.encode(df['cleaned_text'].tolist(), batch_size=64, show_progress_bar=False, normalize_embeddings=True)
    print(f"Generated embeddings shape: {embeddings.shape}")
    
    # 2. Cluster dense semantic vectors using KMeans
    print(f"Clustering into {n_clusters} latent topics via KMeans...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    cluster_labels = kmeans.fit_predict(embeddings)
    df['discovered_topic'] = cluster_labels
    
    sil_score = float(silhouette_score(embeddings[::5], cluster_labels[::5])) # Sampled for speed
    print(f"Silhouette Score: {sil_score:.4f}")
    
    # 3. Concatenate text within each cluster for c-TF-IDF keyword extraction
    docs_per_topic = []
    for topic_id in range(n_clusters):
        topic_text = " ".join(df[df['discovered_topic'] == topic_id]['cleaned_text'].tolist())
        docs_per_topic.append(topic_text)
        
    topic_keywords = extract_ctfidf_keywords(docs_per_topic, top_n=10)
    
    # 4. Extract representative posts closest to cluster centroids
    centroids = kmeans.cluster_centers_
    cluster_summary = {}
    
    for topic_id in range(n_clusters):
        cluster_indices = df[df['discovered_topic'] == topic_id].index
        cluster_embeddings = embeddings[cluster_indices]
        centroid = centroids[topic_id]
        
        # Cosine distance to centroid (dot product since normalized)
        similarities = np.dot(cluster_embeddings, centroid)
        top_rep_idx = cluster_indices[similarities.argsort()[-3:][::-1]]
        
        rep_posts = df.loc[top_rep_idx, ['text_id', 'post_text', 'sentiment_label', 'topic_category']].to_dict(orient='records')
        post_count = int(len(cluster_indices))
        pct = float((post_count / len(df)) * 100)
        
        cluster_summary[f"Topic_{topic_id}"] = {
            'cluster_id': topic_id,
            'post_count': post_count,
            'percentage': round(pct, 2),
            'representative_keywords': topic_keywords[topic_id],
            'representative_posts': rep_posts
        }
        
    # 5. Cross-tabulate Discovered Topics vs Labeled Categories
    cross_tab_counts = pd.crosstab(df['discovered_topic'], df['topic_category'])
    cross_tab_props = pd.crosstab(df['discovered_topic'], df['topic_category'], normalize='index').round(4) * 100
    
    # Build complete topic discovery report
    report = {
        'n_clusters': n_clusters,
        'silhouette_score': round(sil_score, 4),
        'clusters': cluster_summary,
        'cross_tabulation_counts': cross_tab_counts.to_dict(),
        'cross_tabulation_proportions': cross_tab_props.to_dict()
    }
    
    out_file = os.path.join(outputs_dir, "unsupervised_topics.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"Unsupervised topic report written to {out_file}")
    
    # 6. Generate Plot: Discovered Clusters vs Labeled Category Alignment
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(cross_tab_props, annot=True, fmt='.1f', cmap='Blues', ax=ax,
                cbar_kws={'label': '% within Discovered Topic'}, linewidths=1, linecolor='white')
    ax.set_title(f'Alignment: {n_clusters} Discovered Latent Topics vs. Labeled Topic Categories (%)', pad=15, fontsize=13, fontweight='bold')
    ax.set_xlabel('Supervised Labeled Category', fontsize=11, fontweight='bold')
    ax.set_ylabel('Unsupervised Discovered Topic ID', fontsize=11, fontweight='bold')
    plt.tight_layout()
    fig.savefig(os.path.join(figures_dir, "unsupervised_topic_clusters.png"), dpi=300)
    plt.close()
    print("Saved alignment heatmap to", os.path.join(figures_dir, "unsupervised_topic_clusters.png"))
    
    # Print Discovered Topics Overview
    print("\n" + "=" * 70)
    print("DISCOVERED LATENT TOPICS OVERVIEW")
    print("=" * 70)
    for topic_id in range(n_clusters):
        c = cluster_summary[f"Topic_{topic_id}"]
        kw_str = ", ".join(c['representative_keywords'][:6])
        print(f"Cluster {topic_id} ({c['post_count']} posts, {c['percentage']}%): Keywords: [{kw_str}]")
        print(f"  Sample: \"{c['representative_posts'][0]['post_text'][:80]}...\"")
        print("-" * 70)
        
    return report

if __name__ == '__main__':
    discover_latent_topics()
