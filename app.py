"""
app.py
──────
Flask web application for the Spam Message Detection System.

Routes:
  GET  /          → Home page with input form
  POST /predict   → Classify a submitted message (JSON response)
  GET  /history   → View past predictions stored in session
  GET  /model-info → Show model performance metrics
"""

from flask import Flask, render_template, request, jsonify, session
from predictor import predict, get_model_info
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)   # for session storage


# ─── Home ─────────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    try:
        model_info = get_model_info()
    except FileNotFoundError:
        model_info = None
    return render_template("index.html", model_info=model_info, model_ready=model_info is not None)


# ─── Predict (AJAX POST) ──────────────────────────────────────────────────────
@app.route("/predict", methods=["POST"])
def classify():
    data    = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Please enter a message."}), 400

    try:
        result = predict(message)
    except FileNotFoundError:
        return jsonify({"error": "Model not trained yet. Please run: python train.py"}), 503

    # Store in session history (keep last 10)
    history = session.get("history", [])
    history.insert(0, {
        "message":    message[:120],
        "label":      result["label"],
        "confidence": result["confidence"],
        "is_spam":    result["is_spam"],
        "time":       datetime.now().strftime("%H:%M:%S"),
    })
    session["history"] = history[:10]

    return jsonify(result)


# ─── History ──────────────────────────────────────────────────────────────────
@app.route("/history")
def history():
    past = session.get("history", [])
    return jsonify(past)


# ─── Model Info ───────────────────────────────────────────────────────────────
@app.route("/model-info")
def model_info():
    info = get_model_info()
    return jsonify(info)


# ─── Clear History ────────────────────────────────────────────────────────────
@app.route("/clear-history", methods=["POST"])
def clear_history():
    session.pop("history", None)
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    print("\n  Spam Detection Web App running at http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)
