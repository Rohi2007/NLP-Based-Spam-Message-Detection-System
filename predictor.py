"""
predictor.py
────────────
Reusable inference module.
Loads the saved model + vectorizer and exposes a single
`predict(message)` function used by both the CLI and the Flask app.
"""

import os
import re
import pickle
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download("stopwords", quiet=True)

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "spam_model.pkl")
VECT_PATH  = os.path.join(BASE_DIR, "models", "tfidf_vectorizer.pkl")
META_PATH  = os.path.join(BASE_DIR, "models", "model_meta.pkl")

# ─── Lazy-loaded singletons ───────────────────────────────────────────────────
_model      = None
_vectorizer = None
_meta       = None
_stemmer    = PorterStemmer()
_stop_words = set(stopwords.words("english"))


def _load_artifacts():
    """Load model, vectorizer, and metadata from disk (once)."""
    global _model, _vectorizer, _meta

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "Model not found. Please run train.py first to train the model."
        )

    if _model is None:
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)

    if _vectorizer is None:
        with open(VECT_PATH, "rb") as f:
            _vectorizer = pickle.load(f)

    if _meta is None and os.path.exists(META_PATH):
        with open(META_PATH, "rb") as f:
            _meta = pickle.load(f)


def _preprocess(text: str) -> str:
    """
    Applies the same cleaning steps used during training:
      lowercase → remove URLs/emails/phones → strip special chars
      → tokenize → remove stopwords → stem
    """
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", " url ", text, flags=re.MULTILINE)
    text = re.sub(r"\S+@\S+", " email ", text)
    text = re.sub(r"\b(\+?\d[\d\s\-().]{6,}\d)\b", " phone ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    tokens = text.split()
    tokens = [
        _stemmer.stem(w)
        for w in tokens
        if w not in _stop_words and len(w) > 1
    ]
    return " ".join(tokens)


def predict(message: str) -> dict:
    """
    Classify a single message as spam or ham.

    Parameters
    ----------
    message : str
        Raw input message text.

    Returns
    -------
    dict with keys:
        label       – "spam" or "ham"
        confidence  – float 0–100 (percentage)
        cleaned     – preprocessed text
        is_spam     – bool
    """
    _load_artifacts()

    if not message or not message.strip():
        return {
            "label":      "ham",
            "confidence": 0.0,
            "cleaned":    "",
            "is_spam":    False,
            "error":      "Empty message provided.",
        }

    cleaned = _preprocess(message)
    features = _vectorizer.transform([cleaned])

    prediction = _model.predict(features)[0]  # 0 = ham, 1 = spam

    # Confidence score: use predict_proba if available, else decision_function
    confidence = 0.0
    try:
        proba      = _model.predict_proba(features)[0]
        confidence = round(float(proba[prediction]) * 100, 2)
    except AttributeError:
        # LinearSVC doesn't have predict_proba; use decision_function instead
        score      = _model.decision_function(features)[0]
        # Sigmoid approximation to convert to probability
        import math
        confidence = round((1 / (1 + math.exp(-score))) * 100, 2)

    label = "spam" if prediction == 1 else "ham"

    return {
        "label":      label,
        "confidence": confidence,
        "cleaned":    cleaned,
        "is_spam":    bool(prediction == 1),
    }


def get_model_info() -> dict:
    """Return metadata about the trained model."""
    _load_artifacts()
    return _meta if _meta else {}


# ─── CLI quick-test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_messages = [
        "Congratulations! You've won a FREE iPhone! Click here to claim now: http://win.xyz",
        "Hey, are you coming to the meeting tomorrow at 10am?",
        "URGENT: Your bank account has been compromised. Verify now!",
        "Can you pick up some milk on your way home?",
        "You have been selected to receive $5000 cash prize. Call now!",
        "The project deadline is next Friday. Let me know your progress.",
    ]

    print("\n" + "=" * 60)
    print("  Spam Detector - Quick Test")
    print("=" * 60)

    for msg in test_messages:
        result = predict(msg)
        icon   = "🚨 SPAM" if result["is_spam"] else "✅ HAM "
        print(f"\n  {icon}  ({result['confidence']}% confident)")
        print(f"  Message : {msg[:70]}")
        print(f"  Cleaned : {result['cleaned'][:70]}")

    info = get_model_info()
    if info:
        print(f"\n  Model   : {info.get('model_name', 'N/A')}")
        print(f"  F1 Score: {info.get('f1_score', 'N/A')}")
    print()
