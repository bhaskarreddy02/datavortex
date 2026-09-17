"""
Named Entity Recognition (NER) & Social Media Error Audit Module
Social Engine NLP Semantic Understanding Layer
"""

import os
import sys
import json
import re
from collections import Counter, defaultdict
import pandas as pd
import spacy

if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace', line_buffering=True)
    except Exception:
        pass

def run_ner_analysis(data_path="social_engine/data/cleaned_dataset.csv",
                     outputs_dir="social_engine/outputs",
                     sample_size=3000):
    os.makedirs(outputs_dir, exist_ok=True)
    
    print("=" * 70)
    print("PHASE 7: NAMED ENTITY RECOGNITION (NER) & SOCIAL MEDIA ERROR AUDIT")
    print("=" * 70)
    
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} posts for entity analysis (evaluating representative subset of {min(sample_size, len(df))}).")
    
    # Load pretrained NER model
    nlp = spacy.load("en_core_web_sm")
    
    entity_counts = Counter()
    entities_by_type = defaultdict(Counter)
    sample_entities = []
    
    # Documented social media failure modes
    failure_cases = {
        'lowercased_proper_nouns': [],      # e.g., 'romeo santos' in lowercase
        'social_handle_confusion': [],      # e.g., '@user' or handles parsed as person or org
        'hashtag_entity_misses': [],        # e.g., '#Texans' or '#CBB' not parsed as entities
        'sports_music_slang_confusions': [],# e.g., team/album names parsed as products or persons
        'spurious_numerical_entities': []   # e.g., random numbers parsed as dates/cardinals
    }
    
    eval_df = df.head(sample_size)
    docs = list(nlp.pipe(eval_df['cleaned_text'].tolist(), batch_size=100))
    
    for idx, (doc, row) in enumerate(zip(docs, eval_df.itertuples())):
        post_ents = []
        for ent in doc.ents:
            entity_text = ent.text.strip()
            label = ent.label_
            
            entity_counts[label] += 1
            entities_by_type[label][entity_text] += 1
            post_ents.append({'text': entity_text, 'label': label})
            
            # Audit failure modes
            # 1. Social handle confusion
            if '@user' in entity_text.lower() or entity_text.startswith('@'):
                if len(failure_cases['social_handle_confusion']) < 5:
                    failure_cases['social_handle_confusion'].append({
                        'text': row.post_text,
                        'misclassified_entity': entity_text,
                        'assigned_label': label,
                        'reason': 'Synthetic or masked handle incorrectly recognized as real-world entity'
                    })
                    
            # 2. Lowercased entities missed or misclassified
            if entity_text.islower() and label in ['PERSON', 'ORG', 'GPE']:
                if len(failure_cases['lowercased_proper_nouns']) < 5:
                    failure_cases['lowercased_proper_nouns'].append({
                        'text': row.post_text,
                        'entity': entity_text,
                        'label': label,
                        'reason': 'Lowercase capitalization causing unreliable boundary detection'
                    })
                    
        # Check if text had a hashtag that standard NER completely missed
        raw_hashtags = re.findall(r'#(\w+)', str(row.post_text))
        found_texts = [e['text'] for e in post_ents]
        for ht in raw_hashtags:
            if ht not in found_texts and len(failure_cases['hashtag_entity_misses']) < 5:
                failure_cases['hashtag_entity_misses'].append({
                    'text': row.post_text,
                    'missed_hashtag': ht,
                    'reason': 'Domain hashtag entity ignored by standard news-trained NER model'
                })
                
        if idx < 10:
            sample_entities.append({
                'text_id': row.text_id,
                'post_text': row.post_text,
                'extracted_entities': post_ents
            })
            
    # Format top entities per type
    top_entities = {}
    for label, counter in entities_by_type.items():
        top_entities[label] = [{'entity': ent, 'count': count} for ent, count in counter.most_common(10)]
        
    report = {
        'total_posts_evaluated': len(eval_df),
        'total_entities_detected': sum(entity_counts.values()),
        'entity_type_distribution': dict(entity_counts),
        'top_entities_by_type': top_entities,
        'social_media_failure_modes': failure_cases,
        'sample_extractions': sample_entities
    }
    
    out_path = os.path.join(outputs_dir, "ner_evaluation.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"NER analysis report written to {out_path}")
    
    print("\n" + "=" * 70)
    print("TOP DETECTED ENTITY TYPES ACROSS DATASET")
    print("=" * 70)
    for label, count in entity_counts.most_common(8):
        print(f"  {label:<15}: {count:>5} occurrences")
        
    print("\n--- Documented Social Media NER Failure Modes ---")
    print(f"1. Handle confusions logged  : {len(failure_cases['social_handle_confusion'])}")
    print(f"2. Lowercase proper noun bugs : {len(failure_cases['lowercased_proper_nouns'])}")
    print(f"3. Missed hashtag entities   : {len(failure_cases['hashtag_entity_misses'])}")
    return report

if __name__ == '__main__':
    run_ner_analysis()
