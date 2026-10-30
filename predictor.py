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


# ─── Rule-based spam keywords (prize / money / numbers) ──────────────────────
# If a message matches ANY of these patterns it is forced to spam
# regardless of what the ML model says.
_SPAM_RULES = [
    # Prize / winning
    r"\b(won|win|winner|winning|prize|jackpot|lottery|lucky\s*draw|reward|awarded)\b",
    # Money keywords
    r"\b(cash|money|funds|rupees?|dollars?|pounds?|euros?|lakh|crore|lacs?)\b",
    # Claim / collect urgency
    r"\b(claim|collect|redeem|receive\s*your|get\s*your\s*(money|cash|prize|reward))\b",
    # Large numbers (4+ digits) — e.g. 1000 / 50000 / 1000000
    r"\b\d{4,}\b",
    # Currency symbols followed by numbers
    r"[$\u20b9\xa3\u20ac]\s*\d+",
    # Common spam phrases
    r"\b(free\s*money|free\s*cash|free\s*prize|free\s*gift|free\s*reward)\b",
    r"\b(call\s*now|text\s*now|reply\s*(yes|now)|click\s*here|click\s*to\s*claim)\b",
    r"\b(selected|pre[\s-]?selected|chosen|qualified)\b.{0,30}\b(prize|money|cash|reward|gift)\b",
]

_SPAM_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _SPAM_RULES]

# ─── Hard-override: threat / violence / harassment patterns ──────────────────
# A single match here is enough to classify as dangerous regardless of ML.
_THREAT_RULES = [
    # Direct physical threats
    r"\b(kill|murder|kidnap|abduct|shoot|stab|attack|beat\s*you|beat\s*up|rape|assault|strangle|torture)\b",
    # "I will / I am going to" violence
    r"\b(i\s*(will|am\s*going\s*to|gonna|'?ll)\s*(kill|hurt|harm|shoot|stab|attack|destroy|kidnap|murder|rape|f+u+c+k))\b",
    # Bomb / explosion threats
    r"\b(bomb|blast|explode|detonate|blow\s*up)\b",
    # Extortion with consequences
    r"\b(pay\s*(or|else|otherwise)|bitcoin.{0,30}(or|else)|transfer.{0,20}(or\s*i|else\s*i))\b",
    # Doxxing / exposure threats
    r"\b(expose\s*you|leak\s*your|release\s*(the\s*)?(video|photo|footage|pics)|destroy\s*your\s*(life|career|family))\b",
    # Death / serious harm language
    r"\b(you\s*will\s*(die|suffer|regret|pay\s*for)|your\s*(life|family).{0,20}(danger|risk|harm|threat))\b",
    # Self-harm / hate speech directed at person
    r"\b(go\s*die|kill\s*yourself|kys|end\s*your\s*life)\b",
    # Threatening "want to" statements
    r"\bi\s*(want\s*to|wanna)\s*(kill|hurt|harm|kidnap|rape|murder|shoot|stab|attack|f+u+c+k)\b",
]

_THREAT_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _THREAT_RULES]

# ─── Sexual solicitation / harassment / innuendo patterns ────────────────────
# Phrase-level patterns — single match → "abuse" override.
_SEXUAL_RULES = [
    # Classic solicitation phrases
    r"\b(one\s*night\s*stand)\b",
    r"\b(friends?\s*with\s*benefits?|fwb)\b",
    r"\b(hook\s*up|hookup)\b",
    r"\b(no\s*strings?\s*attached|nsa)\b",
    r"\b(come\s*over\s*(tonight|now|and\s*f))\b",
    r"\b(wanna\s*(f+u+c+k|do\s*it|sleep\s*with|have\s*sex|get\s*naughty|get\s*dirty))\b",
    r"\b(want\s*to\s*(have\s*sex|sleep\s*with\s*you|f+u+c+k\s*you|do\s*it))\b",
    r"\b(let'?s?\s*(have\s*sex|f+u+c+k|get\s*naked|do\s*it))\b",
    r"\b(send\s*(me\s*)?(nude|nudes|naked\s*pic|dick\s*pic|pussy\s*pic|your\s*body))\b",
    r"\b(show\s*me\s*(your\s*)?(boobs?|tits?|ass|body|nude|naked))\b",
    # Standalone nude/explicit content requests
    r"\b(nude|nudes)\b",
    r"\b(dick\s*pic|dickpic|cock\s*pic)\b",
    r"\b(tits?|boobs?|titties)\b",
    r"\b(sex(ual)?\s*(favour|favor|service|meet|tonight))\b",
    r"\b(call\s*girl|escort\s*service|massage\s*with\s*happy\s*ending)\b",
    # Sexual body part references used in a harassing context
    r"\b(suck\s*(my|it)|blow\s*(me|job))\b",
    r"\b(get\s*(in\s*)?bed\s*with\s*(me|you))\b",
    r"\b(sleep\s*with\s*(me|you\s*tonight))\b",
    r"\b(you\s*(are|look)\s*(so\s*)?(sexy|hot\s*af|fuckable|bangable))\b",
    r"\b(i\s*want\s*(to\s*)?(f+u+c+k|bang|screw|nail|bone|smash)\s*(you|u))\b",
    r"\b(let\s*me\s*(f+u+c+k|bang|screw|nail|lick|eat\s*you\s*out))\b",
    r"\b(do\s*you\s*(want|like)\s*(to\s*)?(f+u+c+k|have\s*sex|get\s*laid))\b",
    # Adult content solicitation
    r"\b(porn|xxx|adult\s*content|only\s*fans|onlyfans)\b",
    r"\b(cam\s*(girl|boy|show|sex)|live\s*sex\s*(show|cam))\b",
    r"\b(meet\s*(for\s*)?(sex|fun|pleasure|naughty\s*time))\b",
    r"\b(are\s*you\s*(horny|dtf|down\s*to\s*f))\b",
    r"\bdtf\b",
    # Grooming-style phrases
    r"\b(you\s*(are|look)\s*so\s*(mature|grown\s*up)\s*for\s*your\s*age)\b",
    r"\b(don'?t\s*tell\s*(anyone|your\s*(parents?|mum|dad|mom)))\b",
    r"\b(our\s*(little\s*)?secret)\b",
]

_SEXUAL_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _SEXUAL_RULES]

# ─── Profanity / abuse / curse word patterns ─────────────────────────────────
# Covers common spellings, letter-repetition (fuuuck), leet (f*ck, sh!t),
# and word-boundary variants.  A SINGLE match → "abuse" override.
_PROFANITY_RULES = [
    # The f-word and variants  (f*ck, fuuck, fück, fuk, fvck …)
    r"\bf+[\*@#!\s]*u+[\*@#!\s]*c+[\*@#!\s]*k+\b",
    r"\bfu+k\b",
    r"\bfvck\b",
    r"\bfook\b",
    r"\bfuq\b",
    # s-word variants  (sh!t, sh1t, shyt, shiit …)
    r"\bs+[\*@#!\s]*h+[\*@#!\s]*[i1y]+[\*@#!\s]*t+\b",
    r"\bsh[i1y]t\b",
    # a-word  (a$$, @ss, a55 …)
    r"\ba[\$s][\$s]\b",
    r"\b@+s+\b",
    r"\ba55\b",
    r"\basshole\b",
    r"\bass\b",
    # b-words
    r"\bb+[\*@#!\s]*i+[\*@#!\s]*t+[\*@#!\s]*c+[\*@#!\s]*h+\b",
    r"\bb[i1]tch\b",
    r"\bbastered\b",
    r"\bbastard\b",
    r"\bba5tard\b",
    # d-word
    r"\bd+[\*@#!\s]*[i1]+[\*@#!\s]*c+[\*@#!\s]*k+\b",
    r"\bd[i1]ck\b",
    r"\bdk\b",          # common abbreviation in abusive context (handled with context below)
    # c-word
    r"\bc+[\*@#!\s]*u+[\*@#!\s]*n+[\*@#!\s]*t+\b",
    r"\bcunt\b",
    # p-word
    r"\bp+[\*@#!\s]*u+[\*@#!\s]*s+[\*@#!\s]*s+[\*@#!\s]*y+\b",
    r"\bpussy\b",
    # motherf* variants
    r"\bmother\s*f+[\*@#!\s]*u+[\*@#!\s]*c+[\*@#!\s]*k\w*\b",
    r"\bmf\b",
    r"\bmfer\b",
    # son of a b*
    r"\bson\s+of\s+a\s+b[i1]?tch\b",
    r"\bsoab\b",
    # a-hole
    r"\ba[\-\s]?hole\b",
    # damn / hell used aggressively with you
    r"\b(go\s+to\s+hell|damn\s+you|damned?\s+you)\b",
    # idiot / moron / retard used as abuse
    r"\b(idiot|moron|imbecile|retard|stupid\s+(idiot|ass|fool)|dumb\s+(ass|fuck))\b",
    # shut up variants
    r"\bshut\s*(the\s*f+u+c+k\s*)?up\b",
    # loser / scum / trash used as insults
    r"\b(you\s*(are\s*)?(a\s*)?(loser|scum|trash|garbage|worthless|piece\s*of\s*(sh[i1]t|crap|garbage)))\b",
    # hate / abuse combos
    r"\b(i\s*hate\s*you|i\s*despise\s*you|you\s*(disgust|sicken)\s*me)\b",
    # nsfw slurs (keeping generic to avoid listing them fully)
    r"\b(n[i1]g+[ae]r|n[i1]g+[ae]|f+[ae4]g+[o0]?t?|ch[i1]nk|sp[i1]c|w[e3]tb[ae]ck|k[i1]k[e3])\b",
]

_PROFANITY_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _PROFANITY_RULES]


def _rule_based_spam(text: str) -> bool:
    """
    Returns True if the message triggers:
      - 1+ hard threat/violence pattern, OR
      - 1+ sexual solicitation/harassment pattern, OR
      - 1+ profanity/abuse pattern, OR
      - 2+ general spam-signal patterns
    """
    if any(pat.search(text) for pat in _THREAT_PATTERNS):
        return True
    if any(pat.search(text) for pat in _SEXUAL_PATTERNS):
        return True
    if any(pat.search(text) for pat in _PROFANITY_PATTERNS):
        return True
    hits = sum(1 for pat in _SPAM_PATTERNS if pat.search(text))
    return hits >= 2


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
        import math
        confidence = round((1 / (1 + math.exp(-score))) * 100, 2)

    # ── Rule-based override ────────────────────────────────────────────────────
    is_threat   = any(pat.search(message) for pat in _THREAT_PATTERNS)
    is_sexual   = any(pat.search(message) for pat in _SEXUAL_PATTERNS)
    is_profane  = any(pat.search(message) for pat in _PROFANITY_PATTERNS)
    is_gen_spam = _rule_based_spam(message)

    override_type = None
    if prediction == 0 and is_threat:
        prediction    = 1
        confidence    = max(confidence, 97.0)
        override_type = "threat"
    elif prediction == 0 and is_sexual:
        prediction    = 1
        confidence    = max(confidence, 96.0)
        override_type = "sexual"
    elif prediction == 0 and is_profane:
        prediction    = 1
        confidence    = max(confidence, 95.0)
        override_type = "abuse"
    elif prediction == 0 and is_gen_spam:
        prediction    = 1
        confidence    = max(confidence, 85.0)
        override_type = "spam"
    # Tag already-spam messages with richer type
    elif prediction == 1 and override_type is None:
        if is_sexual:
            override_type = "sexual"
        elif is_profane:
            override_type = "abuse"

    label = "spam" if prediction == 1 else "ham"

    return {
        "label":         label,
        "confidence":    confidence,
        "cleaned":       cleaned,
        "is_spam":       bool(prediction == 1),
        "override_type": override_type,   # "threat", "spam", or None
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
