"""
Spam Message Detection System
==============================
NLP Preprocessing + ML Model Training Script

Pipeline:
  1. Load dataset
  2. Text preprocessing (cleaning, tokenization, stopword removal, stemming)
  3. Feature extraction using TF-IDF
  4. Train multiple classifiers (Naive Bayes, Logistic Regression, SVM)
  5. Evaluate and select the best model
  6. Save the model and vectorizer for inference
"""

import os
import re
import string
import pickle
import warnings
import pandas as pd
import numpy as np
warnings.filterwarnings("ignore")

# NLP
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# ML
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

# ─── Download NLTK resources ──────────────────────────────────────────────────
print("=" * 60)
print("  SPAM MESSAGE DETECTION SYSTEM - Model Trainer")
print("=" * 60)

nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, "data", "spam_dataset.csv")
MODEL_DIR  = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "spam_model.pkl")
VECT_PATH  = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")

# ─── Step 1: Load Data ────────────────────────────────────────────────────────
print("\n[1/5] Loading dataset...")
df = pd.read_csv(DATA_PATH)
print(f"      Total samples  : {len(df)}")
print(f"      Spam messages  : {(df['label'] == 'spam').sum()}")
print(f"      Ham  messages  : {(df['label'] == 'ham').sum()}")
print(f"      Columns        : {list(df.columns)}")

# ─── Step 2: Text Preprocessing ───────────────────────────────────────────────
print("\n[2/5] Preprocessing text...")

stemmer        = PorterStemmer()
stop_words     = set(stopwords.words("english"))

def preprocess(text: str) -> str:
    """
    Clean and normalize a raw message:
      - Lowercase
      - Remove URLs
      - Remove email addresses
      - Remove phone numbers
      - Remove punctuation and special characters
      - Tokenize
      - Remove stopwords
      - Apply stemming
    """
    # Lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", " url ", text, flags=re.MULTILINE)

    # Remove email addresses
    text = re.sub(r"\S+@\S+", " email ", text)

    # Remove phone numbers (various formats)
    text = re.sub(r"\b(\+?\d[\d\s\-().]{6,}\d)\b", " phone ", text)

    # Remove punctuation and special characters (keep alphabets + spaces)
    text = re.sub(r"[^a-z\s]", " ", text)

    # Tokenize
    tokens = text.split()

    # Remove stopwords and apply stemming; keep tokens with length > 1
    tokens = [
        stemmer.stem(word)
        for word in tokens
        if word not in stop_words and len(word) > 1
    ]

    return " ".join(tokens)


# Apply preprocessing
df["cleaned_message"] = df["message"].apply(preprocess)

# Encode labels: spam=1, ham=0
df["label_enc"] = df["label"].map({"spam": 1, "ham": 0})

print("      Sample preprocessed messages:")
for i in [0, 1, 2, 3]:
    orig    = df["message"].iloc[i][:60]
    cleaned = df["cleaned_message"].iloc[i][:60]
    label   = df["label"].iloc[i]
    print(f"      [{label}] {orig!r}")
    print(f"            → {cleaned!r}")

# ─── Step 3: Feature Extraction (TF-IDF) ─────────────────────────────────────
print("\n[3/5] Extracting TF-IDF features...")

X = df["cleaned_message"]
y = df["label_enc"]

# Split: 80% train, 20% test (stratified to keep class balance)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

vectorizer = TfidfVectorizer(
    max_features=3000,      # top 3000 tokens
    ngram_range=(1, 2),     # unigrams + bigrams
    sublinear_tf=True       # apply log normalization to TF
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf  = vectorizer.transform(X_test)

print(f"      Vocabulary size : {len(vectorizer.vocabulary_)}")
print(f"      Train samples   : {X_train_tfidf.shape[0]}")
print(f"      Test  samples   : {X_test_tfidf.shape[0]}")
print(f"      Feature matrix  : {X_train_tfidf.shape}")

# ─── Step 4: Train & Evaluate Models ─────────────────────────────────────────
print("\n[4/5] Training and evaluating classifiers...")

classifiers = {
    "Naive Bayes (MultinomialNB)": MultinomialNB(alpha=0.1),
    "Logistic Regression":         LogisticRegression(C=1.0, max_iter=1000, random_state=42),
    "Linear SVM":                  LinearSVC(C=1.0, max_iter=2000, random_state=42),
}

results    = {}
best_name  = None
best_score = 0.0
best_model = None

print(f"\n      {'Model':<35} {'Accuracy':>8} {'Precision':>10} {'Recall':>8} {'F1':>8}")
print("      " + "-" * 75)

for name, clf in classifiers.items():
    clf.fit(X_train_tfidf, y_train)
    y_pred = clf.predict(X_test_tfidf)

    acc  = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec  = recall_score(y_test, y_pred, zero_division=0)
    f1   = f1_score(y_test, y_pred, zero_division=0)

    results[name] = {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "model": clf}
    print(f"      {name:<35} {acc:>8.4f} {prec:>10.4f} {rec:>8.4f} {f1:>8.4f}")

    if f1 > best_score:
        best_score = f1
        best_name  = name
        best_model = clf

print(f"\n      ✔  Best model: {best_name} (F1 = {best_score:.4f})")

# Detailed report for best model
y_pred_best = best_model.predict(X_test_tfidf)
print(f"\n      Classification Report ({best_name}):")
print(classification_report(y_test, y_pred_best, target_names=["Ham (Legit)", "Spam"]))

cm = confusion_matrix(y_test, y_pred_best)
print("      Confusion Matrix:")
print(f"      TN={cm[0][0]}  FP={cm[0][1]}")
print(f"      FN={cm[1][0]}  TP={cm[1][1]}")

# ─── Step 5: Save Model & Vectorizer ─────────────────────────────────────────
print("\n[5/5] Saving model and vectorizer...")

os.makedirs(MODEL_DIR, exist_ok=True)

with open(MODEL_PATH, "wb") as f:
    pickle.dump(best_model, f)

with open(VECT_PATH, "wb") as f:
    pickle.dump(vectorizer, f)

# Also save model metadata
meta = {
    "model_name"  : best_name,
    "f1_score"    : round(best_score, 4),
    "accuracy"    : round(results[best_name]["accuracy"], 4),
    "precision"   : round(results[best_name]["precision"], 4),
    "recall"      : round(results[best_name]["recall"], 4),
    "vocab_size"  : len(vectorizer.vocabulary_),
    "all_results" : {k: {m: round(v, 4) for m, v in vs.items() if m != "model"}
                     for k, vs in results.items()},
}
META_PATH = os.path.join(MODEL_DIR, "model_meta.pkl")
with open(META_PATH, "wb") as f:
    pickle.dump(meta, f)

print(f"      Model saved     → {MODEL_PATH}")
print(f"      Vectorizer saved→ {VECT_PATH}")
print(f"      Metadata saved  → {META_PATH}")

print("\n" + "=" * 60)
print("  Training complete! Run app.py to start the web UI.")
print("=" * 60 + "\n")
