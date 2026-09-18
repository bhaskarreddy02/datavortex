"""
Baseline Classical Machine Learning Models Module
Social Engine NLP Semantic Understanding Layer
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.naive_bayes import ComplementNB
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    classification_report, confusion_matrix
)

if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except Exception:
        pass

def compute_metrics(y_true, y_pred, labels):
    acc = accuracy_score(y_true, y_pred)
    prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(y_true, y_pred, average='macro', zero_division=0)
    prec_weighted, rec_weighted, f1_weighted, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
    
    # Per-class metrics
    p_class, r_class, f_class, s_class = precision_recall_fscore_support(y_true, y_pred, labels=labels, zero_division=0)
    per_class = {}
    for i, label in enumerate(labels):
        per_class[str(label)] = {
            'precision': float(p_class[i]),
            'recall': float(r_class[i]),
            'f1_score': float(f_class[i]),
            'support': int(s_class[i])
        }
        
    return {
        'accuracy': float(acc),
        'macro_precision': float(prec_macro),
        'macro_recall': float(rec_macro),
        'macro_f1': float(f1_macro),
        'weighted_precision': float(prec_weighted),
        'weighted_recall': float(rec_weighted),
        'weighted_f1': float(f1_weighted),
        'per_class': per_class,
        'confusion_matrix': confusion_matrix(y_true, y_pred, labels=labels).tolist(),
        'classification_report': classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)
    }

def plot_confusion_matrix(cm, labels, title, save_path):
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels, ax=ax,
                cbar=False, annot_kws={"size": 12, "weight": "bold"})
    ax.set_title(title, pad=12, fontsize=13, fontweight='bold')
    ax.set_ylabel('True Label', fontsize=11, fontweight='bold')
    ax.set_xlabel('Predicted Label', fontsize=11, fontweight='bold')
    plt.xticks(rotation=20, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    fig.savefig(save_path, dpi=300)
    plt.close()

def plot_feature_importance(model, feature_names, labels, title, save_path, n_top=10):
    """
    Extracts and visualizes top positive coefficients per class for linear models.
    """
    n_classes = len(labels)
    fig, axes = plt.subplots(1, n_classes, figsize=(5 * n_classes, 4.5))
    if n_classes == 1:
        axes = [axes]
        
    palette = sns.color_palette("tab10", n_classes)
    for idx, (label, color) in enumerate(zip(labels, palette)):
        coefs = model.coef_[idx] if hasattr(model, 'coef_') else np.zeros(len(feature_names))
        top_indices = coefs.argsort()[-n_top:][::-1]
        top_words = feature_names[top_indices]
        top_vals = coefs[top_indices]
        
        axes[idx].barh(top_words[::-1], top_vals[::-1], color=color, alpha=0.85, edgecolor='black')
        axes[idx].set_title(f"Class: {label}", pad=10, fontweight='bold', fontsize=12)
        axes[idx].set_xlabel("Coefficient Weight", fontweight='bold')
        
    plt.suptitle(title, y=1.03, fontsize=14, fontweight='bold')
    plt.tight_layout()
    fig.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

def run_baselines(data_dir="social_engine/data",
                  models_dir="social_engine/models",
                  outputs_dir="social_engine/outputs",
                  figures_dir="social_engine/figures"):
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    
    print("=" * 70)
    print("PHASE 3: TRAINING CLASSICAL ML BASELINE MODELS")
    print("=" * 70)
    
    # 1. Load pre-split datasets
    train_df = pd.read_csv(os.path.join(data_dir, "train.csv"))
    val_df = pd.read_csv(os.path.join(data_dir, "val.csv"))
    test_df = pd.read_csv(os.path.join(data_dir, "test.csv"))
    
    print(f"Data Loaded: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")
    
    # Define labels
    sentiment_labels = ["Negative", "Neutral", "Positive"]
    topic_labels = ["Account_Security", "Community_Discussion", "Feature_Feedback", "Technical_Issues"]
    
    # 2. Build TF-IDF Feature Representation
    print("\nExtracting TF-IDF features (sublinear tf, word n-grams 1-2, min_df=2)...")
    tfidf = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=2,
        max_features=15000,
        token_pattern=r'(?u)\b\w+\b'
    )
    
    X_train = tfidf.fit_transform(train_df['cleaned_text'])
    X_val = tfidf.transform(val_df['cleaned_text'])
    X_test = tfidf.transform(test_df['cleaned_text'])
    
    print(f"TF-IDF Vocabulary Size: {len(tfidf.vocabulary_)} features")
    joblib.dump(tfidf, os.path.join(models_dir, "tfidf_vectorizer.joblib"))
    feature_names = np.array(tfidf.get_feature_names_out())
    
    results = {'sentiment': {}, 'topic': {}}
    
    # =========================================================================
    # TASK 1: SENTIMENT CLASSIFICATION
    # =========================================================================
    print("\n" + "=" * 50)
    print("TASK 1: SENTIMENT CLASSIFICATION BASELINES")
    print("=" * 50)
    
    y_train_sent = train_df['sentiment_label']
    y_val_sent = val_df['sentiment_label']
    y_test_sent = test_df['sentiment_label']
    
    sentiment_candidates = {
        'Logistic_Regression': LogisticRegression(C=1.5, max_iter=1000, random_state=42),
        'Linear_SVM': CalibratedClassifierCV(LinearSVC(C=0.8, random_state=42, max_iter=3000)),
        'Complement_NB': ComplementNB(alpha=0.5)
    }
    
    best_sent_model_name = None
    best_sent_val_f1 = -1.0
    
    for name, model in sentiment_candidates.items():
        print(f"\nTraining Sentiment - {name}...")
        model.fit(X_train, y_train_sent)
        
        # Validate (model selection)
        val_preds = model.predict(X_val)
        val_metrics = compute_metrics(y_val_sent, val_preds, sentiment_labels)
        print(f"Validation Macro F1: {val_metrics['macro_f1']:.4f} | Accuracy: {val_metrics['accuracy']:.4f}")
        
        if val_metrics['macro_f1'] > best_sent_val_f1:
            best_sent_val_f1 = val_metrics['macro_f1']
            best_sent_model_name = name
            
        # Final evaluation on held-out Test set
        test_preds = model.predict(X_test)
        test_metrics = compute_metrics(y_test_sent, test_preds, sentiment_labels)
        test_metrics['validation_macro_f1'] = val_metrics['macro_f1']
        results['sentiment'][name] = test_metrics
        
        # Save model
        joblib.dump(model, os.path.join(models_dir, f"sentiment_{name}.joblib"))
        
        # Save confusion matrix plot
        plot_confusion_matrix(
            np.array(test_metrics['confusion_matrix']),
            sentiment_labels,
            f"Sentiment Test CM: {name} (F1: {test_metrics['macro_f1']:.3f})",
            os.path.join(figures_dir, f"confusion_matrix_sentiment_{name.lower()}.png")
        )
        
    print(f"\n--> Best Sentiment Baseline (selected via Val F1): {best_sent_model_name} (Val F1: {best_sent_val_f1:.4f})")
    
    # Feature Importance for Sentiment
    plot_feature_importance(
        sentiment_candidates['Logistic_Regression'],
        feature_names,
        sentiment_labels,
        "Sentiment Feature Explainability (Top Informative TF-IDF N-grams)",
        os.path.join(figures_dir, "feature_importance_sentiment.png")
    )
    
    # =========================================================================
    # TASK 2: TOPIC CLASSIFICATION (With Severe Class Imbalance Handling)
    # =========================================================================
    print("\n" + "=" * 50)
    print("TASK 2: TOPIC CLASSIFICATION BASELINES (Class Weighted)")
    print("=" * 50)
    
    y_train_topic = train_df['topic_category']
    y_val_topic = val_df['topic_category']
    y_test_topic = test_df['topic_category']
    
    topic_candidates = {
        'Logistic_Regression': LogisticRegression(C=2.0, class_weight='balanced', max_iter=1000, random_state=42),
        'Linear_SVM': CalibratedClassifierCV(LinearSVC(C=1.0, class_weight='balanced', random_state=42, max_iter=3000)),
        'Complement_NB': ComplementNB(alpha=0.5)
    }
    
    best_topic_model_name = None
    best_topic_val_f1 = -1.0
    
    for name, model in topic_candidates.items():
        print(f"\nTraining Topic - {name}...")
        model.fit(X_train, y_train_topic)
        
        # Validate (model selection)
        val_preds = model.predict(X_val)
        val_metrics = compute_metrics(y_val_topic, val_preds, topic_labels)
        print(f"Validation Macro F1: {val_metrics['macro_f1']:.4f} | Weighted F1: {val_metrics['weighted_f1']:.4f} | Accuracy: {val_metrics['accuracy']:.4f}")
        
        if val_metrics['macro_f1'] > best_topic_val_f1:
            best_topic_val_f1 = val_metrics['macro_f1']
            best_topic_model_name = name
            
        # Final evaluation on held-out Test set
        test_preds = model.predict(X_test)
        test_metrics = compute_metrics(y_test_topic, test_preds, topic_labels)
        test_metrics['validation_macro_f1'] = val_metrics['macro_f1']
        results['topic'][name] = test_metrics
        
        # Save model
        joblib.dump(model, os.path.join(models_dir, f"topic_{name}.joblib"))
        
        # Save confusion matrix plot
        plot_confusion_matrix(
            np.array(test_metrics['confusion_matrix']),
            topic_labels,
            f"Topic Test CM: {name} (Macro F1: {test_metrics['macro_f1']:.3f})",
            os.path.join(figures_dir, f"confusion_matrix_topic_{name.lower()}.png")
        )
        
    print(f"\n--> Best Topic Baseline (selected via Val F1): {best_topic_model_name} (Val F1: {best_topic_val_f1:.4f})")
    
    # Feature Importance for Topics
    plot_feature_importance(
        topic_candidates['Logistic_Regression'],
        feature_names,
        topic_labels,
        "Topic Category Feature Explainability (Top Informative TF-IDF N-grams)",
        os.path.join(figures_dir, "feature_importance_topic.png")
    )
    
    # Save all baseline evaluation results to JSON
    out_path = os.path.join(outputs_dir, "baseline_evaluation.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nBaseline metrics report successfully written to {out_path}")
    
    # Print summary performance table
    print("\n" + "=" * 70)
    print("BASELINE PERFORMANCE SUMMARY (TEST SET)")
    print("=" * 70)
    rows = []
    for task in ['sentiment', 'topic']:
        for model_name, m in results[task].items():
            rows.append({
                'Task': task.capitalize(),
                'Model': model_name,
                'Val Macro F1': f"{m['validation_macro_f1']:.4f}",
                'Test Acc': f"{m['accuracy']:.4f}",
                'Test Macro F1': f"{m['macro_f1']:.4f}",
                'Test Weighted F1': f"{m['weighted_f1']:.4f}"
            })
    df_summary = pd.DataFrame(rows)
    print(df_summary.to_string(index=False))
    return results

if __name__ == '__main__':
    run_baselines()
