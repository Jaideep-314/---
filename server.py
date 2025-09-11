import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

API_KEY = "fde5f7db-e95f-41f8-abdb-75b6cd7d461a"
BASE_URL = "https://api.sambanova.ai/v1/chat/completions"
MODEL = "DeepSeek-R1-Distill-Llama-70B"  # ✅ use one of your available models

def remove_think(content: str) -> str:
    """Remove <think>...</think> blocks from model output."""
    return re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "")
        if not user_message:
            return jsonify({"reply": "⚠️ No message received."})

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        }

        resp = requests.post(
            BASE_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=20
        )

        if resp.status_code != 200:
            return jsonify({"reply": f"⚠️ Error: {resp.status_code} — {resp.text}"})

        resp_json = resp.json()
        ai_reply = resp_json["choices"][0]["message"]["content"]

        # 🧹 Clean out hidden reasoning
        ai_reply_clean = remove_think(ai_reply)

        return jsonify({"reply": ai_reply_clean})

    except Exception as e:
        return jsonify({"reply": f"⚠️ Server error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
