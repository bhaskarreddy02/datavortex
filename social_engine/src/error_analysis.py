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
    print("PHASE 11 & 12: SYSTEMATIC QUALITATIVE ERROR ANALYSIS")
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
    test_df['word_count'] = test_df['cleaned_text'].apply(lambda x: len(str(x).split()))
    
    analysis = {
        'total_test_samples': len(test_df),
        'sentiment_errors_count': int(test_df['sentiment_error'].sum()),
        'sentiment_error_rate': round(float(test_df['sentiment_error'].mean() * 100), 2),
        'topic_errors_count': int(test_df['topic_error'].sum()),
        'topic_error_rate': round(float(test_df['topic_error'].mean() * 100), 2),
        'failure_categories': {}
    }
    
    print(f"Total Held-Out Test Samples    : {len(test_df)}")
    print(f"Sentiment Classification Errors: {analysis['sentiment_errors_count']} ({analysis['sentiment_error_rate']}%)")
    print(f"Topic Classification Errors    : {analysis['topic_errors_count']} ({analysis['topic_error_rate']}%)")
    
    # Helper to print formatted failure case
    def print_case(title, post_text, actual, pred, conf, why):
        print("\n" + "=" * 70)
        print(f"FAILURE MODE: {title}")
        print("=" * 70)
        print(f"Text                          : \"{post_text}\"")
        print(f"Actual label                  : {actual}")
        print(f"Predicted label               : {pred}")
        print(f"Confidence                    : {conf:.4f}")
        print(f"Why the model may have failed : {why}")
    
    # 1. Sarcasm / Polarity Inversion
    sarcasm_cases = test_df[
        (test_df['sentiment_label'] == 'Negative') &
        (test_df['pred_sentiment'] == 'Positive')
    ]
    analysis['failure_categories']['sarcasm_and_polarity_inversion'] = {
        'count': len(sarcasm_cases),
        'description': "Caustic negative sentiment phrased with superficial praise or laughing tokens."
    }
    if len(sarcasm_cases) > 0:
        r = sarcasm_cases.iloc[0]
        print_case(
            "Sarcasm & Polarity Inversion (Lexical Irony)",
            r['post_text'],
            r['sentiment_label'],
            r['pred_sentiment'],
            r['sent_confidence'],
            "The author uses superficially positive/mocking vocabulary (e.g. 'haha', 'great', 'joke'). Without pragmatic world knowledge, bag-of-words linear models aggregate positive token weights and miss the critical sarcastic intent."
        )
        
    # 2. Minority Topic Absorption
    minority_swallowed = test_df[
        (test_df['topic_category'].isin(['Account_Security', 'Technical_Issues', 'Feature_Feedback'])) &
        (test_df['pred_topic'] == 'Community_Discussion')
    ]
    analysis['failure_categories']['minority_topic_absorption'] = {
        'count': len(minority_swallowed),
        'description': "Specific domain problem posts misclassified as generic Community Discussion."
    }
    if len(minority_swallowed) > 0:
        r = minority_swallowed.iloc[0]
        print_case(
            "Minority Topic Swallowed by Majority Class",
            r['post_text'],
            r['topic_category'],
            r['pred_topic'],
            r['topic_confidence'],
            "The post articulates a domain-specific issue using conversational phrasing rather than explicit technical triggers (e.g. 'password reset', 'crash'). In the absence of decisive n-grams, the massive prior probability of Community_Discussion (86.1%) dominates."
        )

    # 3. Slang, Acronyms & Social Noise
    slang_pattern = r'\b(?:tbh|smh|afaik|lol|lmao|idk|rn|fml|af|bc)\b'
    slang_cases = test_df[
        test_df['cleaned_text'].str.contains(slang_pattern, case=False, regex=True) &
        test_df['sentiment_error']
    ]
    analysis['failure_categories']['slang_and_abbreviations'] = {
        'count': len(slang_cases),
        'description': "Informal shorthand and slang carrying compressed emotional valence."
    }
    if len(slang_cases) > 0:
        r = slang_cases.iloc[0]
        print_case(
            "Social Slang, Acronyms & Informal Shorthand",
            r['post_text'],
            r['sentiment_label'],
            r['pred_sentiment'],
            r['sent_confidence'],
            "Colloquial acronyms and casual shorthand carry nuanced emotional intensity that is diluted or out-of-vocabulary in standard n-gram tokenizers, causing polarity attenuation."
        )

    # 4. Short Low-Context Posts
    short_cases = test_df[
        (test_df['word_count'] <= 6) &
        (test_df['sentiment_error'] | test_df['topic_error'])
    ]
    analysis['failure_categories']['short_low_context_posts'] = {
        'count': len(short_cases),
        'description': "Extremely brief posts under 7 words lacking discriminative context."
    }
    if len(short_cases) > 0:
        r = short_cases.iloc[0]
        print_case(
            "Short Low-Context Posts (< 7 words)",
            r['post_text'],
            f"Sentiment={r['sentiment_label']}, Topic={r['topic_category']}",
            f"Sentiment={r['pred_sentiment']}, Topic={r['pred_topic']}",
            min(r['sent_confidence'], r['topic_confidence']),
            "Extremely concise microblog posts contain only 1-4 content words, leaving the feature representation severely sparse and vulnerable to ambiguous priors."
        )
        
    out_file = os.path.join(outputs_dir, "error_analysis_report.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)
    print(f"\nError analysis report successfully exported to {out_file}")
    return analysis

if __name__ == '__main__':
    perform_error_analysis()
