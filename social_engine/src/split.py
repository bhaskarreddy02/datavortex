"""
Dataset Splitting & Leak-Free Partitioning Module
Social Engine NLP Semantic Understanding Layer
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold
from preprocessing import preprocess_dataframe

if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except Exception:
        pass

def create_leak_free_splits(data_path="Labeled_Social_NLP_Training_Data.csv",
                            data_dir="social_engine/data",
                            random_state=42):
    os.makedirs(data_dir, exist_ok=True)
    print("=" * 70)
    print("CREATING LEAK-FREE STRATIFIED TRAIN / VAL / TEST SPLITS")
    print("=" * 70)
    
    # 1. Load original dataset (DO NOT MODIFY IN-PLACE)
    raw_df = pd.read_csv(data_path)
    print(f"Loaded {len(raw_df)} records from {data_path}")
    
    # 2. Apply preprocessing to add raw_text and cleaned_text
    df = preprocess_dataframe(raw_df, text_col='post_text')
    
    # Save full cleaned dataset
    cleaned_full_path = os.path.join(data_dir, "cleaned_dataset.csv")
    df.to_csv(cleaned_full_path, index=False)
    print(f"Saved preprocessed dataset with raw_text & cleaned_text to {cleaned_full_path}")
    
    # 3. Create composite stratify label (sentiment + topic) to maintain both distributions
    df['stratify_key'] = df['sentiment_label'].astype(str) + "___" + df['topic_category'].astype(str)
    
    # 4. Group by cleaned_text so identical posts NEVER cross between Train, Val, and Test
    # Use StratifiedGroupKFold (10 folds -> 8 folds for train, 1 fold for val, 1 fold for test)
    sgkf = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=random_state)
    
    folds = list(sgkf.split(df, y=df['stratify_key'], groups=df['cleaned_text']))
    
    # Fold 0 -> Test (10%)
    # Fold 1 -> Validation (10%)
    # Folds 2..9 -> Train (80%)
    test_idx = folds[0][1]
    val_idx = folds[1][1]
    train_idx = np.concatenate([folds[i][1] for i in range(2, 10)])
    
    train_df = df.iloc[train_idx].copy().reset_index(drop=True)
    val_df = df.iloc[val_idx].copy().reset_index(drop=True)
    test_df = df.iloc[test_idx].copy().reset_index(drop=True)
    
    # Drop intermediate stratify key
    for d in [train_df, val_df, test_df]:
        d.drop(columns=['stratify_key'], inplace=True)
        
    # Verify zero leakage between splits
    train_texts = set(train_df['cleaned_text'])
    val_texts = set(val_df['cleaned_text'])
    test_texts = set(test_df['cleaned_text'])
    
    leak_train_val = len(train_texts.intersection(val_texts))
    leak_train_test = len(train_texts.intersection(test_texts))
    leak_val_test = len(val_texts.intersection(test_texts))
    
    print("\n--- Leakage Verification ---")
    print(f"Text overlap between Train and Val : {leak_train_val}")
    print(f"Text overlap between Train and Test: {leak_train_test}")
    print(f"Text overlap between Val and Test  : {leak_val_test}")
    assert leak_train_val == 0, "Data leakage detected between Train and Val!"
    assert leak_train_test == 0, "Data leakage detected between Train and Test!"
    assert leak_val_test == 0, "Data leakage detected between Val and Test!"
    print("-> STRICT ZERO LEAKAGE CONFIRMED! Post groups are completely isolated.")
    
    # Verify class proportions across splits
    print("\n--- Split Size & Class Distributions ---")
    print(f"Train: {len(train_df)} rows ({len(train_df)/len(df)*100:.1f}%)")
    print(f"Val  : {len(val_df)} rows ({len(val_df)/len(df)*100:.1f}%)")
    print(f"Test : {len(test_df)} rows ({len(test_df)/len(df)*100:.1f}%)")
    
    print("\nSentiment Distribution across splits (%):")
    sent_summary = pd.DataFrame({
        'Train': train_df['sentiment_label'].value_counts(normalize=True) * 100,
        'Val': val_df['sentiment_label'].value_counts(normalize=True) * 100,
        'Test': test_df['sentiment_label'].value_counts(normalize=True) * 100,
    }).round(2)
    print(sent_summary)
    
    print("\nTopic Distribution across splits (%):")
    topic_summary = pd.DataFrame({
        'Train': train_df['topic_category'].value_counts(normalize=True) * 100,
        'Val': val_df['topic_category'].value_counts(normalize=True) * 100,
        'Test': test_df['topic_category'].value_counts(normalize=True) * 100,
    }).round(2)
    print(topic_summary)
    
    # Save splits
    train_df.to_csv(os.path.join(data_dir, "train.csv"), index=False)
    val_df.to_csv(os.path.join(data_dir, "val.csv"), index=False)
    test_df.to_csv(os.path.join(data_dir, "test.csv"), index=False)
    print(f"\nSaved train.csv, val.csv, test.csv to {data_dir}")
    return train_df, val_df, test_df

if __name__ == '__main__':
    create_leak_free_splits()
