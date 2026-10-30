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
from flask_cors import CORS
from predictor import predict, get_model_info
from datetime import datetime
import os
import socket

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "spam-detection-nlp-2024-aditya-university")
CORS(app)

# ─── Global error handlers — always return JSON, never HTML ──────────────────
@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# ─── Health check ─────────────────────────────────────────────────────────────
@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "message": "Spam Detection API is running"})


# ─── Home ─────────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    try:
        model_info = get_model_info()
    except FileNotFoundError:
        model_info = None
    return render_template("index.html", model_info=model_info, model_ready=model_info is not None)


# ─── Predict ──────────────────────────────────────────────────────────────────
@app.route("/predict", methods=["POST"])
def classify():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body."}), 400

    message = data.get("message", "").strip()
    sender  = data.get("sender", "Unknown")

    if not message:
        return jsonify({"error": "Please enter a message."}), 400

    try:
        result = predict(message)
    except FileNotFoundError:
        return jsonify({"error": "Model not trained yet. Please run: python train.py"}), 503
    except Exception as e:
        return jsonify({"error": f"Prediction error: {str(e)}"}), 500

    result["sender"] = sender
    # Ensure override_type is always a string (never None) so jsonify is happy
    result["override_type"] = result.get("override_type") or ""

    # ── Session history — store only the minimal fields to stay under 4KB ──
    try:
        history = session.get("history", [])
        history.insert(0, {
            "message":    message[:80],
            "label":      result["label"],
            "confidence": result["confidence"],
            "is_spam":    result["is_spam"],
            "time":       datetime.now().strftime("%H:%M:%S"),
        })
        session["history"] = history[:10]
        session.modified = True
    except Exception:
        pass

    return jsonify(result)


# ─── History ──────────────────────────────────────────────────────────────────
@app.route("/history")
def history():
    try:
        past = session.get("history", [])
    except Exception:
        past = []
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
    local_ip = get_local_ip()
    print("\n" + "=" * 55)
    print("  Spam Detection API is running")
    print(f"  Web UI  : http://127.0.0.1:5000")
    print(f"  Android : http://{local_ip}:5000  ← use this IP in Android app")
    print("=" * 55 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
