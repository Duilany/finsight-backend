from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

from utils.financial import analyze_financial
from services.ai_service import generate_insight

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({
        "message": "FinSight AI Backend is running 🚀"
    })

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json

        if not data:
            return jsonify({"error": "No input data provided"}), 400

        analysis = analyze_financial(data)
        ai_result = generate_insight(data, analysis)

        return jsonify({
            "analysis": analysis,
            "insight": ai_result["insight"],
            "profile": ai_result["profile"]
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "error": "Internal server error"
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)