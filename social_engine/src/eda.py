"""
Dataset 2 Audit and Exploratory Data Analysis (EDA) Module
Social Engine NLP Semantic Understanding Layer
"""

import os
import re
import json
import unicodedata
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configure visual style for professional competition reports
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['figure.titlesize'] = 16

def run_dataset_audit(data_path="Labeled_Social_NLP_Training_Data.csv", output_dir="social_engine/outputs", figures_dir="social_engine/figures"):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    
    print("=" * 70)
    print("PHASE 1: SOCIAL ENGINE DATASET 2 AUDIT & HEALTH CHECK")
    print("=" * 70)
    
    df = pd.read_csv(data_path)
    audit = {}
    
    # Basic shape and metadata
    audit['num_rows'] = int(df.shape[0])
    audit['num_cols'] = int(df.shape[1])
    audit['columns'] = list(df.columns)
    audit['dtypes'] = {col: str(df[col].dtype) for col in df.columns}
    
    # Missing values
    audit['missing_values'] = {col: int(df[col].isna().sum()) for col in df.columns}
    audit['missing_percentage'] = {col: float(df[col].isna().mean() * 100) for col in df.columns}
    
    # Duplication audit
    audit['duplicate_entire_rows'] = int(df.duplicated().sum())
    audit['duplicate_text_id'] = int(df['text_id'].duplicated().sum())
    audit['duplicate_post_text'] = int(df['post_text'].duplicated().sum())
    
    # Unique labels and class distribution
    audit['unique_sentiment_labels'] = list(df['sentiment_label'].unique())
    audit['sentiment_distribution'] = df['sentiment_label'].value_counts().to_dict()
    audit['sentiment_distribution_pct'] = (df['sentiment_label'].value_counts(normalize=True) * 100).round(2).to_dict()
    
    audit['unique_topic_categories'] = list(df['topic_category'].unique())
    audit['topic_distribution'] = df['topic_category'].value_counts().to_dict()
    audit['topic_distribution_pct'] = (df['topic_category'].value_counts(normalize=True) * 100).round(2).to_dict()
    
    # Text length metrics (character and word counts)
    df['char_length'] = df['post_text'].fillna('').astype(str).apply(len)
    df['word_count'] = df['post_text'].fillna('').astype(str).apply(lambda x: len(x.split()))
    
    audit['char_length_stats'] = {
        'min': int(df['char_length'].min()),
        'max': int(df['char_length'].max()),
        'mean': float(df['char_length'].mean()),
        'median': float(df['char_length'].median()),
        'std': float(df['char_length'].std()),
        'p25': float(df['char_length'].quantile(0.25)),
        'p75': float(df['char_length'].quantile(0.75)),
        'p95': float(df['char_length'].quantile(0.95)),
        'p99': float(df['char_length'].quantile(0.99))
    }
    
    audit['word_count_stats'] = {
        'min': int(df['word_count'].min()),
        'max': int(df['word_count'].max()),
        'mean': float(df['word_count'].mean()),
        'median': float(df['word_count'].median()),
        'std': float(df['word_count'].std()),
        'p25': float(df['word_count'].quantile(0.25)),
        'p75': float(df['word_count'].quantile(0.75)),
        'p95': float(df['word_count'].quantile(0.95)),
        'p99': float(df['word_count'].quantile(0.99))
    }
    
    # Identify extremely short and extremely long posts
    short_posts = df[df['word_count'] <= 3][['text_id', 'post_text', 'sentiment_label', 'topic_category']].to_dict(orient='records')
    long_posts = df[df['word_count'] >= 50][['text_id', 'post_text', 'sentiment_label', 'topic_category']].head(5).to_dict(orient='records')
    audit['extremely_short_posts_count'] = len(short_posts)
    audit['extremely_short_samples'] = short_posts[:5]
    audit['extremely_long_posts_count'] = int((df['word_count'] >= 50).sum())
    audit['extremely_long_samples'] = long_posts
    
    # Social media lexical pattern analysis
    # Regex patterns:
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    mention_pattern = re.compile(r'@\w+')
    hashtag_pattern = re.compile(r'#\w+')
    html_entity_pattern = re.compile(r'&[a-zA-Z0-9#]+;')
    escaped_unicode_pattern = re.compile(r'(\\u[0-9a-fA-F]{4}|u2019|u2018|u201c|u201d)')
    repeated_char_pattern = re.compile(r'(.)\1{2,}')
    # Emoji range regex
    emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)
    
    df['has_url'] = df['post_text'].apply(lambda x: bool(url_pattern.search(str(x))))
    df['has_mention'] = df['post_text'].apply(lambda x: bool(mention_pattern.search(str(x))))
    df['has_hashtag'] = df['post_text'].apply(lambda x: bool(hashtag_pattern.search(str(x))))
    df['has_html_entity'] = df['post_text'].apply(lambda x: bool(html_entity_pattern.search(str(x))))
    df['has_escaped_unicode'] = df['post_text'].apply(lambda x: bool(escaped_unicode_pattern.search(str(x))))
    df['has_repeated_chars'] = df['post_text'].apply(lambda x: bool(repeated_char_pattern.search(str(x))))
    df['has_emoji'] = df['post_text'].apply(lambda x: bool(emoji_pattern.search(str(x))))
    
    audit['social_patterns'] = {
        'posts_with_urls': int(df['has_url'].sum()),
        'pct_urls': float((df['has_url'].mean() * 100).round(2)),
        'posts_with_mentions': int(df['has_mention'].sum()),
        'pct_mentions': float((df['has_mention'].mean() * 100).round(2)),
        'posts_with_hashtags': int(df['has_hashtag'].sum()),
        'pct_hashtags': float((df['has_hashtag'].mean() * 100).round(2)),
        'posts_with_html_entities': int(df['has_html_entity'].sum()),
        'pct_html_entities': float((df['has_html_entity'].mean() * 100).round(2)),
        'posts_with_escaped_unicode': int(df['has_escaped_unicode'].sum()),
        'pct_escaped_unicode': float((df['has_escaped_unicode'].mean() * 100).round(2)),
        'posts_with_repeated_chars': int(df['has_repeated_chars'].sum()),
        'pct_repeated_chars': float((df['has_repeated_chars'].mean() * 100).round(2)),
        'posts_with_emojis': int(df['has_emoji'].sum()),
        'pct_emojis': float((df['has_emoji'].mean() * 100).round(2))
    }
    
    # Collect specific examples of noise/corruptions
    audit['noise_samples'] = {
        'escaped_unicode_examples': df[df['has_escaped_unicode']]['post_text'].head(4).tolist(),
        'html_entity_examples': df[df['has_html_entity']]['post_text'].head(4).tolist(),
        'repeated_char_examples': df[df['has_repeated_chars']]['post_text'].head(4).tolist(),
        'emoji_examples': df[df['has_emoji']]['post_text'].head(4).tolist()
    }
    
    # Check for label consistency & data leakage across duplicate texts
    dup_texts = df[df.duplicated(subset=['post_text'], keep=False)]
    audit['duplicate_post_text_total_rows'] = len(dup_texts)
    if len(dup_texts) > 0:
        # Check if duplicated texts have conflicting labels
        conflicts_sentiment = dup_texts.groupby('post_text')['sentiment_label'].nunique()
        conflicts_topic = dup_texts.groupby('post_text')['topic_category'].nunique()
        audit['duplicate_conflicting_sentiment'] = int((conflicts_sentiment > 1).sum())
        audit['duplicate_conflicting_topic'] = int((conflicts_topic > 1).sum())
    else:
        audit['duplicate_conflicting_sentiment'] = 0
        audit['duplicate_conflicting_topic'] = 0

    # Cross-tabulation: Topic vs Sentiment
    contingency_counts = pd.crosstab(df['topic_category'], df['sentiment_label'])
    contingency_props = pd.crosstab(df['topic_category'], df['sentiment_label'], normalize='index').round(4) * 100
    audit['topic_sentiment_crosstab_counts'] = contingency_counts.to_dict()
    audit['topic_sentiment_crosstab_proportions'] = contingency_props.to_dict()
    
    # Save audit report
    with open(os.path.join(output_dir, 'dataset_audit_report.json'), 'w', encoding='utf-8') as f:
        json.dump(audit, f, indent=2)
        
    print("Audit JSON successfully written to", os.path.join(output_dir, 'dataset_audit_report.json'))
    
    # =========================================================================
    # GENERATE PUBLICATION-GRADE VISUALIZATIONS
    # =========================================================================
    
    # 1. Sentiment Distribution Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    sentiment_counts = df['sentiment_label'].value_counts()
    colors = ['#2ca02c', '#d62728', '#1f77b4'] if 'Positive' in sentiment_counts.index else sns.color_palette('tab10', len(sentiment_counts))
    bars = ax.bar(sentiment_counts.index, sentiment_counts.values, color=colors, width=0.55, edgecolor='black', alpha=0.85)
    for bar in bars:
        h = bar.get_height()
        pct = (h / len(df)) * 100
        ax.annotate(f'{h:,}\n({pct:.1f}%)',
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='semibold')
    ax.set_title('Dataset 2 — Sentiment Class Distribution', pad=15)
    ax.set_xlabel('Sentiment Label')
    ax.set_ylabel('Number of Posts')
    ax.set_ylim(0, max(sentiment_counts.values) * 1.18)
    plt.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'sentiment_distribution.png'), dpi=300)
    plt.close()
    
    # 2. Topic Distribution Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    topic_counts = df['topic_category'].value_counts()
    palette = sns.color_palette('viridis', len(topic_counts))
    bars = ax.barh(topic_counts.index[::-1], topic_counts.values[::-1], color=palette[::-1], edgecolor='black', alpha=0.85)
    for bar in bars:
        w = bar.get_width()
        pct = (w / len(df)) * 100
        ax.annotate(f' {w:,} ({pct:.1f}%)',
                    xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points",
                    ha='left', va='center', fontsize=10, fontweight='semibold')
    ax.set_title('Dataset 2 — Topic Category Distribution', pad=15)
    ax.set_xlabel('Number of Posts')
    ax.set_ylabel('Topic Category')
    ax.set_xlim(0, max(topic_counts.values) * 1.22)
    plt.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'topic_distribution.png'), dpi=300)
    plt.close()
    
    # 3. Text Length Distribution (Word & Character count)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    sns.histplot(df['word_count'], bins=35, kde=True, ax=ax1, color='#1f77b4', edgecolor='black')
    ax1.axvline(df['word_count'].median(), color='red', linestyle='--', linewidth=1.5, label=f"Median: {df['word_count'].median():.0f} words")
    ax1.axvline(df['word_count'].mean(), color='orange', linestyle=':', linewidth=1.5, label=f"Mean: {df['word_count'].mean():.1f} words")
    ax1.set_title('Word Count Distribution')
    ax1.set_xlabel('Words per Post')
    ax1.set_ylabel('Frequency')
    ax1.legend()
    
    sns.histplot(df['char_length'], bins=40, kde=True, ax=ax2, color='#2ca02c', edgecolor='black')
    ax2.axvline(df['char_length'].median(), color='red', linestyle='--', linewidth=1.5, label=f"Median: {df['char_length'].median():.0f} chars")
    ax2.axvline(df['char_length'].mean(), color='orange', linestyle=':', linewidth=1.5, label=f"Mean: {df['char_length'].mean():.1f} chars")
    ax2.set_title('Character Length Distribution')
    ax2.set_xlabel('Characters per Post')
    ax2.set_ylabel('Frequency')
    ax2.legend()
    plt.suptitle('Dataset 2 — Text Length Characteristics', y=1.02, fontsize=15, fontweight='bold')
    plt.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'text_length_distribution.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Topic vs Sentiment Relationship Heatmap
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(contingency_props, annot=True, fmt='.1f', cmap='YlGnBu', cbar_kws={'label': '% within Topic Category'},
                linewidths=1, linecolor='white', ax=ax)
    ax.set_title('Topic Category vs. Sentiment Distribution (%)', pad=15)
    ax.set_xlabel('Sentiment Label')
    ax.set_ylabel('Topic Category')
    plt.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'topic_vs_sentiment.png'), dpi=300)
    plt.close()
    
    print("Visualizations successfully saved to", figures_dir)
    return audit, df

if __name__ == '__main__':
    run_dataset_audit()
