from flask import Flask, request, jsonify
import requests, os, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/api/aligenie", methods=["POST"])
def aligenie():
    try:
        data = request.get_json(force=True, silent=True) or {}
        user_input = data.get("request", {}).get("intent", {}).get("text", "").strip() or "你好"

        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            logger.error("DEEPSEEK_API_KEY not set")
            return jsonify({"error": "Server misconfigured: DEEPSEEK_API_KEY missing"}), 500

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": user_input}]}

        r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=15)

        if r.status_code != 200:
            logger.error("DeepSeek API error: %s - %s", r.status_code, r.text)
            return jsonify({"error": "DeepSeek API returned error", "detail": r.text}), 502

        j = r.json()
        try:
            reply = j["choices"][0]["message"]["content"]
        except Exception:
            logger.exception("Unexpected DeepSeek response structure: %s", j)
            reply = "抱歉，AI接口返回了不可解析的结果。"

        return jsonify({
            "version": "1.0",
            "response": {"to_speak": {"type": 0, "text": reply}, "open_mic": False}
        })

    except requests.Timeout:
        logger.exception("DeepSeek request timed out")
        return jsonify({"error": "DeepSeek 请求超时"}), 504
    except Exception as e:
        logger.exception("Unhandled exception in aligenie")
        return jsonify({"error": "Server internal error", "detail": str(e)}), 500

# For local debug
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
