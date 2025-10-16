from flask import Flask, request, jsonify
import requests, os

app = Flask(__name__)

@app.route("/api/aligenie", methods=["POST"])
def aligenie():
    data = request.json
    user_input = data.get("request", {}).get("intent", {}).get("text", "你好")

    headers = {"Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": user_input}]
    }

    r = requests.post("https://api.deepseek.com/v1/chat/completions",
                      headers=headers, json=payload)
    reply = r.json()["choices"][0]["message"]["content"]

    return jsonify({
        "version": "1.0",
        "response": {
            "to_speak": {"type": 0, "text": reply},
            "open_mic": False
        }
    })

def handler(event, context):
    return app
