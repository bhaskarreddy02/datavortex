"""
Deep Error Analysis & Model Failure Taxonomy Module
Social Engine NLP Semantic Understanding Layer
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd

if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace', line_buffering=True)
    except Exception:
        pass

def perform_error_analysis(data_dir="social_engine/data",
                           models_dir="social_engine/models",
                           outputs_dir="social_engine/outputs"):
    os.makedirs(outputs_dir, exist_ok=True)
    print("=" * 70)
    print("PHASE 12: DEEP ERROR ANALYSIS & FAILURE TAXONOMY")
    print("=" * 70)
    
    # 1. Load Test Set (Completely unseen during training & model selection)
    test_df = pd.read_csv(os.path.join(data_dir, "test.csv"))
    
    # 2. Load Vectorizer and Best Baseline Models
    tfidf = joblib.load(os.path.join(models_dir, "tfidf_vectorizer.joblib"))
    sent_model = joblib.load(os.path.join(models_dir, "sentiment_Logistic_Regression.joblib"))
    topic_model = joblib.load(os.path.join(models_dir, "topic_Linear_SVM.joblib"))
    
    X_test = tfidf.transform(test_df['cleaned_text'])
    test_df['pred_sentiment'] = sent_model.predict(X_test)
    test_df['pred_topic'] = topic_model.predict(X_test)
    
    # Probabilities/confidence
    sent_probs = sent_model.predict_proba(X_test)
    topic_probs = topic_model.predict_proba(X_test)
    test_df['sent_confidence'] = np.max(sent_probs, axis=1).round(4)
    test_df['topic_confidence'] = np.max(topic_probs, axis=1).round(4)
    
    # Flags for errors
    test_df['sentiment_error'] = test_df['sentiment_label'] != test_df['pred_sentiment']
    test_df['topic_error'] = test_df['topic_category'] != test_df['pred_topic']
    
    analysis = {
        'total_test_samples': len(test_df),
        'sentiment_errors_count': int(test_df['sentiment_error'].sum()),
        'sentiment_error_rate': round(float(test_df['sentiment_error'].mean() * 100), 2),
        'topic_errors_count': int(test_df['topic_error'].sum()),
        'topic_error_rate': round(float(test_df['topic_error'].mean() * 100), 2),
        'failure_categories': {}
    }
    
    # =========================================================================
    # TAXONOMY CATEGORY 1: TOPIC MINORITY CLASS CONFUSION WITH COMMUNITY DISCUSSION
    # =========================================================================
    # When Account_Security or Technical_Issues or Feature_Feedback is predicted as Community_Discussion
    minority_swallowed = test_df[
        (test_df['topic_category'].isin(['Account_Security', 'Technical_Issues', 'Feature_Feedback'])) &
        (test_df['pred_topic'] == 'Community_Discussion')
    ]
    analysis['failure_categories']['minority_swallowed_by_majority'] = {
        'count': len(minority_swallowed),
        'description': "Minority domain posts misclassified as generic Community Discussion due to domain vocabulary sparsity or conversational tone.",
        'samples': minority_swallowed[['text_id', 'post_text', 'topic_category', 'pred_topic', 'topic_confidence']].head(5).to_dict(orient='records')
    }
    
    # =========================================================================
    # TAXONOMY CATEGORY 2: SUBTLE SARCASM / MIXED POLARITY IN SENTIMENT
    # =========================================================================
    # True Negative predicted as Positive, or True Positive predicted as Negative
    extreme_sentiment_flips = test_df[
        ((test_df['sentiment_label'] == 'Negative') & (test_df['pred_sentiment'] == 'Positive')) |
        ((test_df['sentiment_label'] == 'Positive') & (test_df['pred_sentiment'] == 'Negative'))
    ]
    analysis['failure_categories']['sentiment_polarity_inversions'] = {
        'count': len(extreme_sentiment_flips),
        'description': "Severe sentiment inversion (Negative <-> Positive) triggered by sarcasm, conflicting lexical cues (e.g. 'haha DUKE what a joke'), or polite complaint phrasing.",
        'samples': extreme_sentiment_flips[['text_id', 'post_text', 'sentiment_label', 'pred_sentiment', 'sent_confidence']].head(5).to_dict(orient='records')
    }
    
    # =========================================================================
    # TAXONOMY CATEGORY 3: NEUTRAL VS POLAR BOUNDARY AMBIGUITY
    # =========================================================================
    # Neutral posts predicted as Positive/Negative or vice versa with low confidence (< 0.55)
    neutral_ambiguity = test_df[
        ((test_df['sentiment_label'] == 'Neutral') & (test_df['pred_sentiment'].isin(['Positive', 'Negative']))) |
        ((test_df['sentiment_label'].isin(['Positive', 'Negative'])) & (test_df['pred_sentiment'] == 'Neutral'))
    ]
    analysis['failure_categories']['neutral_boundary_ambiguity'] = {
        'count': len(neutral_ambiguity),
        'description': "Subjective boundary between neutral factual reporting and mild personal sentiment in conversational text.",
        'samples': neutral_ambiguity.sort_values(by='sent_confidence').head(5)[['text_id', 'post_text', 'sentiment_label', 'pred_sentiment', 'sent_confidence']].to_dict(orient='records')
    }
    
    # =========================================================================
    # TAXONOMY CATEGORY 4: SHORT POSTS WITH LOW CONTEXT
    # =========================================================================
    test_df['word_count'] = test_df['cleaned_text'].apply(lambda x: len(str(x).split()))
    short_post_errors = test_df[(test_df['word_count'] <= 10) & (test_df['sentiment_error'] | test_df['topic_error'])]
    analysis['failure_categories']['short_low_context_posts'] = {
        'count': len(short_post_errors),
        'description': "Extremely short social posts (<10 words) lacking sufficient discriminative tokens for bag-of-words classifiers.",
        'samples': short_post_errors[['text_id', 'post_text', 'sentiment_label', 'pred_sentiment', 'topic_category', 'pred_topic']].head(5).to_dict(orient='records')
    }
    
    out_file = os.path.join(outputs_dir, "error_analysis_report.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)
    print(f"Error analysis report successfully exported to {out_file}")
    
    print("\n" + "=" * 70)
    print("ERROR TAXONOMY SUMMARY (HELD-OUT TEST SET)")
    print("=" * 70)
    print(f"Total Test Posts Analyzed      : {len(test_df)}")
    print(f"Sentiment Classification Errors: {analysis['sentiment_errors_count']} ({analysis['sentiment_error_rate']}%)")
    print(f"Topic Classification Errors    : {analysis['topic_errors_count']} ({analysis['topic_error_rate']}%)")
    print("\nDominant Error Classes:")
    for cat_name, cat in analysis['failure_categories'].items():
        print(f"  • {cat_name:<32}: {cat['count']} cases")
        print(f"    Rationale: {cat['description']}")
        print(f"    Sample post: \"{cat['samples'][0]['post_text'][:80]}...\"")
        print()
    return analysis

if __name__ == '__main__':
    perform_error_analysis()
