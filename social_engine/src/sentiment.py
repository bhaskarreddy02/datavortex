"""
Sentiment Classification Module
Social Engine NLP Semantic Understanding Layer
"""

import os
import sys
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

from preprocessing import SocialTextPreprocessor

def predict_sentiment(text: str, models_dir="social_engine/models"):
    preprocessor = SocialTextPreprocessor()
    clean = preprocessor.clean_text(text)
    
    tfidf = joblib.load(os.path.join(models_dir, "tfidf_vectorizer.joblib"))
    model = joblib.load(os.path.join(models_dir, "sentiment_Logistic_Regression.joblib"))
    
    feats = tfidf.transform([clean])
    pred = model.predict(feats)[0]
    probs = model.predict_proba(feats)[0]
    classes = model.classes_
    prob_dict = {classes[i]: round(float(probs[i]), 4) for i in range(len(classes))}
    
    return {
        "text": text,
        "cleaned_text": clean,
        "sentiment": pred,
        "probabilities": prob_dict
    }

if __name__ == '__main__':
    sample = "The new update is AMAZING!! loving the speed boost 🚀"
    res = predict_sentiment(sample)
    print("Sentiment Prediction Sample:")
    print(res)
