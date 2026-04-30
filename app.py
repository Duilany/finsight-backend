from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from utils.financial import analyze_financial
from services.ai_service import generate_insight

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    analysis = analyze_financial(data)
    ai_result = generate_insight(data, analysis)

    return jsonify({
        "analysis": analysis,
        "insight": ai_result["insight"],
        "profile": ai_result["profile"] 
    })

if __name__ == "__main__":
    app.run(debug=True)