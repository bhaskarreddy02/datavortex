"""
Transformer & Multi-Task Semantic Understanding Pipeline
Social Engine NLP Semantic Understanding Layer
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sentence_transformers import SentenceTransformer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace', line_buffering=True)
    except Exception:
        pass

SENTIMENT_MAP = {"Negative": 0, "Neutral": 1, "Positive": 2}
REV_SENTIMENT_MAP = {v: k for k, v in SENTIMENT_MAP.items()}

TOPIC_MAP = {
    "Account_Security": 0,
    "Community_Discussion": 1,
    "Feature_Feedback": 2,
    "Technical_Issues": 3
}
REV_TOPIC_MAP = {v: k for k, v in TOPIC_MAP.items()}

# -----------------------------------------------------------------------------
# ARCHITECTURES
# -----------------------------------------------------------------------------

class DedicatedSentimentHead(nn.Module):
    def __init__(self, in_dim=384, hidden_dim=192, num_classes=3, dropout=0.25):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 64),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes)
        )
    def forward(self, x):
        return self.net(x)

class DedicatedTopicHead(nn.Module):
    def __init__(self, in_dim=384, hidden_dim=192, num_classes=4, dropout=0.25):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 64),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes)
        )
    def forward(self, x):
        return self.net(x)

class MultiTaskSocialTransformer(nn.Module):
    """
    Multi-Task Neural Architecture:
    Shared contextual representation -> Shared Dense Projection -> Task-Specific Heads.
    Jointly predicts Sentiment and Topic.
    """
    def __init__(self, in_dim=384, shared_dim=256, num_sent=3, num_topic=4, dropout=0.25):
        super().__init__()
        self.shared_proj = nn.Sequential(
            nn.Linear(in_dim, shared_dim),
            nn.LayerNorm(shared_dim),
            nn.GELU(),
            nn.Dropout(dropout)
        )
        self.sentiment_head = nn.Sequential(
            nn.Linear(shared_dim, 96),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(96, num_sent)
        )
        self.topic_head = nn.Sequential(
            nn.Linear(shared_dim, 96),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(96, num_topic)
        )

    def forward(self, x):
        shared_rep = self.shared_proj(x)
        sent_logits = self.sentiment_head(shared_rep)
        topic_logits = self.topic_head(shared_rep)
        return sent_logits, topic_logits

# -----------------------------------------------------------------------------
# EVALUATION & VISUALIZATION HELPERS
# -----------------------------------------------------------------------------

def compute_metrics(y_true, y_pred, label_names):
    acc = accuracy_score(y_true, y_pred)
    prec_m, rec_m, f1_m, _ = precision_recall_fscore_support(y_true, y_pred, average='macro', zero_division=0)
    prec_w, rec_w, f1_w, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
    
    p_c, r_c, f_c, s_c = precision_recall_fscore_support(y_true, y_pred, labels=list(range(len(label_names))), zero_division=0)
    per_class = {}
    for i, name in enumerate(label_names):
        per_class[name] = {
            'precision': float(p_c[i]),
            'recall': float(r_c[i]),
            'f1_score': float(f_c[i]),
            'support': int(s_c[i])
        }
    return {
        'accuracy': float(acc),
        'macro_precision': float(prec_m),
        'macro_recall': float(rec_m),
        'macro_f1': float(f1_m),
        'weighted_precision': float(prec_w),
        'weighted_recall': float(rec_w),
        'weighted_f1': float(f1_w),
        'per_class': per_class,
        'confusion_matrix': confusion_matrix(y_true, y_pred, labels=list(range(len(label_names)))).tolist()
    }

def plot_cm(cm, labels, title, save_path):
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

# -----------------------------------------------------------------------------
# MAIN EXECUTION PIPELINE
# -----------------------------------------------------------------------------

def run_transformers_pipeline():
    print("=" * 70)
    print("PHASES 4 & 5: TRANSFORMER & MULTI-TASK ARCHITECTURAL BENCHMARK")
    print("=" * 70)
    
    data_dir = "social_engine/data"
    models_dir = "social_engine/models"
    outputs_dir = "social_engine/outputs"
    figures_dir = "social_engine/figures"
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    
    # 1. Load Data Splits
    train_df = pd.read_csv(os.path.join(data_dir, "train.csv"))
    val_df = pd.read_csv(os.path.join(data_dir, "val.csv"))
    test_df = pd.read_csv(os.path.join(data_dir, "test.csv"))
    print(f"Loaded Splits: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")
    
    # 2. Extract Dense Contextual Transformer Embeddings
    emb_train_path = os.path.join(models_dir, "train_embeddings.npy")
    emb_val_path = os.path.join(models_dir, "val_embeddings.npy")
    emb_test_path = os.path.join(models_dir, "test_embeddings.npy")
    
    print("\nLoading sentence-transformers/all-MiniLM-L6-v2 contextual backbone...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    if os.path.exists(emb_train_path) and os.path.exists(emb_val_path) and os.path.exists(emb_test_path):
        print("Loading pre-computed contextual transformer embeddings from disk...")
        X_train = np.load(emb_train_path)
        X_val = np.load(emb_val_path)
        X_test = np.load(emb_test_path)
    else:
        print("Computing contextual representations for train, val, and test...")
        t0 = time.time()
        X_train = embedder.encode(train_df['cleaned_text'].tolist(), batch_size=64, normalize_embeddings=True, show_progress_bar=False)
        X_val = embedder.encode(val_df['cleaned_text'].tolist(), batch_size=64, normalize_embeddings=True, show_progress_bar=False)
        X_test = embedder.encode(test_df['cleaned_text'].tolist(), batch_size=64, normalize_embeddings=True, show_progress_bar=False)
        print(f"Contextual extraction completed in {time.time() - t0:.2f}s!")
        np.save(emb_train_path, X_train)
        np.save(emb_val_path, X_val)
        np.save(emb_test_path, X_test)
        
    y_train_sent = torch.tensor(train_df['sentiment_label'].map(SENTIMENT_MAP).values, dtype=torch.long)
    y_val_sent = torch.tensor(val_df['sentiment_label'].map(SENTIMENT_MAP).values, dtype=torch.long)
    y_test_sent = torch.tensor(test_df['sentiment_label'].map(SENTIMENT_MAP).values, dtype=torch.long)
    
    y_train_topic = torch.tensor(train_df['topic_category'].map(TOPIC_MAP).values, dtype=torch.long)
    y_val_topic = torch.tensor(val_df['topic_category'].map(TOPIC_MAP).values, dtype=torch.long)
    y_test_topic = torch.tensor(test_df['topic_category'].map(TOPIC_MAP).values, dtype=torch.long)
    
    # Calculate inverse class weights for topic to handle the 86% vs 1.5% imbalance
    topic_counts = train_df['topic_category'].map(TOPIC_MAP).value_counts().sort_index()
    topic_weights = torch.tensor(
        [len(train_df) / (len(TOPIC_MAP) * topic_counts[i]) for i in range(len(TOPIC_MAP))],
        dtype=torch.float
    )
    print(f"Computed Topic Class Weights: {topic_weights.tolist()}")
    
    X_train_t = torch.tensor(X_train, dtype=torch.float)
    X_val_t = torch.tensor(X_val, dtype=torch.float)
    X_test_t = torch.tensor(X_test, dtype=torch.float)
    
    train_loader = DataLoader(TensorDataset(X_train_t, y_train_sent, y_train_topic), batch_size=64, shuffle=True)
    val_loader = DataLoader(TensorDataset(X_val_t, y_val_sent, y_val_topic), batch_size=128, shuffle=False)
    test_loader = DataLoader(TensorDataset(X_test_t, y_test_sent, y_test_topic), batch_size=128, shuffle=False)
    
    results = {}
    
    # =========================================================================
    # TASK 1: DEDICATED SENTIMENT TRANSFORMER
    # =========================================================================
    print("\n" + "=" * 50)
    print("1. TRAINING DEDICATED SENTIMENT TRANSFORMER")
    print("=" * 50)
    
    torch.manual_seed(42)
    sent_model = DedicatedSentimentHead()
    sent_criterion = nn.CrossEntropyLoss()
    sent_opt = torch.optim.AdamW(sent_model.parameters(), lr=1.5e-3, weight_decay=0.01)
    
    best_sent_val_f1 = -1.0
    best_sent_state = None
    t0 = time.time()
    
    for epoch in range(1, 21):
        sent_model.train()
        for bx, by_sent, _ in train_loader:
            sent_opt.zero_grad()
            logits = sent_model(bx)
            loss = sent_criterion(logits, by_sent)
            loss.backward()
            sent_opt.step()
            
        # Validate
        sent_model.eval()
        with torch.no_grad():
            val_logits = sent_model(X_val_t)
            val_preds = torch.argmax(val_logits, dim=1).numpy()
            m = compute_metrics(y_val_sent.numpy(), val_preds, list(SENTIMENT_MAP.keys()))
            
        if m['macro_f1'] > best_sent_val_f1:
            best_sent_val_f1 = m['macro_f1']
            best_sent_state = {k: v.clone() for k, v in sent_model.state_dict().items()}
            
    sent_train_time = time.time() - t0
    print(f"Dedicated Sentiment Finished in {sent_train_time:.2f}s | Best Val Macro F1: {best_sent_val_f1:.4f}")
    
    # Test evaluation
    sent_model.load_state_dict(best_sent_state)
    sent_model.eval()
    with torch.no_grad():
        test_preds = torch.argmax(sent_model(X_test_t), dim=1).numpy()
    sent_test_m = compute_metrics(y_test_sent.numpy(), test_preds, list(SENTIMENT_MAP.keys()))
    sent_test_m['val_macro_f1'] = best_sent_val_f1
    sent_test_m['training_time_sec'] = round(sent_train_time, 2)
    results['dedicated_sentiment'] = sent_test_m
    
    torch.save(best_sent_state, os.path.join(models_dir, "dedicated_sentiment_transformer.pt"))
    plot_cm(
        np.array(sent_test_m['confusion_matrix']),
        list(SENTIMENT_MAP.keys()),
        f"Dedicated Transformer Sentiment Test CM (Macro F1: {sent_test_m['macro_f1']:.3f})",
        os.path.join(figures_dir, "confusion_matrix_transformer_sentiment.png")
    )
    
    # =========================================================================
    # TASK 2: DEDICATED TOPIC TRANSFORMER (BALANCED LOSS)
    # =========================================================================
    print("\n" + "=" * 50)
    print("2. TRAINING DEDICATED TOPIC TRANSFORMER (Class Weighted)")
    print("=" * 50)
    
    torch.manual_seed(42)
    topic_model = DedicatedTopicHead()
    topic_criterion = nn.CrossEntropyLoss(weight=topic_weights)
    topic_opt = torch.optim.AdamW(topic_model.parameters(), lr=1.5e-3, weight_decay=0.01)
    
    best_topic_val_f1 = -1.0
    best_topic_state = None
    t0 = time.time()
    
    for epoch in range(1, 21):
        topic_model.train()
        for bx, _, by_topic in train_loader:
            topic_opt.zero_grad()
            logits = topic_model(bx)
            loss = topic_criterion(logits, by_topic)
            loss.backward()
            topic_opt.step()
            
        topic_model.eval()
        with torch.no_grad():
            val_logits = topic_model(X_val_t)
            val_preds = torch.argmax(val_logits, dim=1).numpy()
            m = compute_metrics(y_val_topic.numpy(), val_preds, list(TOPIC_MAP.keys()))
            
        if m['macro_f1'] > best_topic_val_f1:
            best_topic_val_f1 = m['macro_f1']
            best_topic_state = {k: v.clone() for k, v in topic_model.state_dict().items()}
            
    topic_train_time = time.time() - t0
    print(f"Dedicated Topic Finished in {topic_train_time:.2f}s | Best Val Macro F1: {best_topic_val_f1:.4f}")
    
    topic_model.load_state_dict(best_topic_state)
    topic_model.eval()
    with torch.no_grad():
        test_preds = torch.argmax(topic_model(X_test_t), dim=1).numpy()
    topic_test_m = compute_metrics(y_test_topic.numpy(), test_preds, list(TOPIC_MAP.keys()))
    topic_test_m['val_macro_f1'] = best_topic_val_f1
    topic_test_m['training_time_sec'] = round(topic_train_time, 2)
    results['dedicated_topic'] = topic_test_m
    
    torch.save(best_topic_state, os.path.join(models_dir, "dedicated_topic_transformer.pt"))
    plot_cm(
        np.array(topic_test_m['confusion_matrix']),
        list(TOPIC_MAP.keys()),
        f"Dedicated Transformer Topic Test CM (Macro F1: {topic_test_m['macro_f1']:.3f})",
        os.path.join(figures_dir, "confusion_matrix_transformer_topic.png")
    )
    
    # =========================================================================
    # TASK 3: MULTI-TASK LEARNING TRANSFORMER
    # =========================================================================
    print("\n" + "=" * 50)
    print("3. TRAINING MULTI-TASK JOINT TRANSFORMER")
    print("=" * 50)
    
    torch.manual_seed(42)
    mtl_model = MultiTaskSocialTransformer()
    mtl_opt = torch.optim.AdamW(mtl_model.parameters(), lr=1.8e-3, weight_decay=0.01)
    
    best_mtl_score = -1.0
    best_mtl_state = None
    t0 = time.time()
    
    for epoch in range(1, 26):
        mtl_model.train()
        for bx, by_sent, by_topic in train_loader:
            mtl_opt.zero_grad()
            s_logits, t_logits = mtl_model(bx)
            l_sent = sent_criterion(s_logits, by_sent)
            l_topic = topic_criterion(t_logits, by_topic)
            loss = l_sent + 1.2 * l_topic
            loss.backward()
            mtl_opt.step()
            
        mtl_model.eval()
        with torch.no_grad():
            s_logits, t_logits = mtl_model(X_val_t)
            s_preds = torch.argmax(s_logits, dim=1).numpy()
            t_preds = torch.argmax(t_logits, dim=1).numpy()
            
            m_s = compute_metrics(y_val_sent.numpy(), s_preds, list(SENTIMENT_MAP.keys()))
            m_t = compute_metrics(y_val_topic.numpy(), t_preds, list(TOPIC_MAP.keys()))
            joint_val = 0.5 * (m_s['macro_f1'] + m_t['macro_f1'])
            
        if joint_val > best_mtl_score:
            best_mtl_score = joint_val
            best_mtl_state = {k: v.clone() for k, v in mtl_model.state_dict().items()}
            
    mtl_train_time = time.time() - t0
    print(f"Multi-Task Model Finished in {mtl_train_time:.2f}s | Best Joint Val Macro F1: {best_mtl_score:.4f}")
    
    mtl_model.load_state_dict(best_mtl_state)
    mtl_model.eval()
    with torch.no_grad():
        s_logits, t_logits = mtl_model(X_test_t)
        s_preds = torch.argmax(s_logits, dim=1).numpy()
        t_preds = torch.argmax(t_logits, dim=1).numpy()
        
    mtl_sent_test = compute_metrics(y_test_sent.numpy(), s_preds, list(SENTIMENT_MAP.keys()))
    mtl_topic_test = compute_metrics(y_test_topic.numpy(), t_preds, list(TOPIC_MAP.keys()))
    
    results['multitask'] = {
        'sentiment': mtl_sent_test,
        'topic': mtl_topic_test,
        'joint_val_macro_f1': best_mtl_score,
        'training_time_sec': round(mtl_train_time, 2),
        'total_parameters': sum(p.numel() for p in mtl_model.parameters())
    }
    
    torch.save(best_mtl_state, os.path.join(models_dir, "multitask_social_transformer.pt"))
    plot_cm(
        np.array(mtl_sent_test['confusion_matrix']),
        list(SENTIMENT_MAP.keys()),
        f"Multi-Task Sentiment Test CM (Macro F1: {mtl_sent_test['macro_f1']:.3f})",
        os.path.join(figures_dir, "confusion_matrix_multitask_sentiment.png")
    )
    plot_cm(
        np.array(mtl_topic_test['confusion_matrix']),
        list(TOPIC_MAP.keys()),
        f"Multi-Task Topic Test CM (Macro F1: {mtl_topic_test['macro_f1']:.3f})",
        os.path.join(figures_dir, "confusion_matrix_multitask_topic.png")
    )
    
    # Save full evaluation JSON
    out_json = os.path.join(outputs_dir, "transformer_evaluation.json")
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nTransformer evaluation metrics successfully exported to {out_json}")
    
    # Summary Table
    print("\n" + "=" * 70)
    print("TRANSFORMER & MULTI-TASK TEST BENCHMARK SUMMARY")
    print("=" * 70)
    rows = [
        {
            'Architecture': 'Dedicated Transformer',
            'Task': 'Sentiment',
            'Val Macro F1': f"{results['dedicated_sentiment']['val_macro_f1']:.4f}",
            'Test Acc': f"{results['dedicated_sentiment']['accuracy']:.4f}",
            'Test Macro F1': f"{results['dedicated_sentiment']['macro_f1']:.4f}",
            'Test Weighted F1': f"{results['dedicated_sentiment']['weighted_f1']:.4f}",
            'Train Time': f"{results['dedicated_sentiment']['training_time_sec']}s"
        },
        {
            'Architecture': 'Dedicated Transformer',
            'Task': 'Topic',
            'Val Macro F1': f"{results['dedicated_topic']['val_macro_f1']:.4f}",
            'Test Acc': f"{results['dedicated_topic']['accuracy']:.4f}",
            'Test Macro F1': f"{results['dedicated_topic']['macro_f1']:.4f}",
            'Test Weighted F1': f"{results['dedicated_topic']['weighted_f1']:.4f}",
            'Train Time': f"{results['dedicated_topic']['training_time_sec']}s"
        },
        {
            'Architecture': 'Multi-Task Transformer',
            'Task': 'Sentiment',
            'Val Macro F1': f"{results['multitask']['joint_val_macro_f1']:.4f} (joint)",
            'Test Acc': f"{results['multitask']['sentiment']['accuracy']:.4f}",
            'Test Macro F1': f"{results['multitask']['sentiment']['macro_f1']:.4f}",
            'Test Weighted F1': f"{results['multitask']['sentiment']['weighted_f1']:.4f}",
            'Train Time': f"{results['multitask']['training_time_sec']}s (joint)"
        },
        {
            'Architecture': 'Multi-Task Transformer',
            'Task': 'Topic',
            'Val Macro F1': f"{results['multitask']['joint_val_macro_f1']:.4f} (joint)",
            'Test Acc': f"{results['multitask']['topic']['accuracy']:.4f}",
            'Test Macro F1': f"{results['multitask']['topic']['macro_f1']:.4f}",
            'Test Weighted F1': f"{results['multitask']['topic']['weighted_f1']:.4f}",
            'Train Time': f"{results['multitask']['training_time_sec']}s (joint)"
        }
    ]
    df_res = pd.DataFrame(rows)
    print(df_res.to_string(index=False))
    return results

if __name__ == '__main__':
    run_transformers_pipeline()
