"""
The Alibi — Flask backend
Serves the game's HTML and proxies requests to the Groq API,
so the real API key never touches the browser.

Groq's chat endpoint is OpenAI-compatible: it takes a "messages" array
(with a "system" role message first) and returns choices[0].message.content.
We normalize that response into the same {content: [{type, text}]} shape
the frontend already expects, so the game's JS doesn't need to know or
care which provider is behind it.
"""

import os
import logging
import webbrowser
from threading import Timer
from datetime import datetime

import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# openai/gpt-oss-20b: fast + cheap, good default for this game.
# Swap to openai/gpt-oss-120b in .env (GROQ_MODEL=...) for stronger reasoning
# at higher cost/latency if the detective feels too easy to fool.
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

os.makedirs("logs", exist_ok=True)
log_filename = f"logs/alibi_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def call_groq():
    """
    Receives {system, messages} from the game's JS, forwards it to
    Groq with the real API key attached server-side, and returns a
    normalized response shape the frontend already understands.
    """
    if not GROQ_API_KEY:
        logging.error("GROQ_API_KEY missing from environment")
        return jsonify({"error": "GROQ_API_KEY not set. Add it to your .env file."}), 500

    body = request.get_json(silent=True) or {}
    system_prompt = body.get("system", "")
    messages = body.get("messages", [])

    if not messages:
        return jsonify({"error": "No messages provided."}), 400

    groq_messages = [{"role": "system", "content": system_prompt}] + messages

    try:
        logging.info("Calling Groq API | model=%s | %d messages", MODEL, len(messages))
        response = requests.post(
            GROQ_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}",
            },
            json={
                "model": MODEL,
                "max_tokens": 1000,
                "temperature": 0.7,
                "messages": groq_messages,
            },
            timeout=30,
        )

        try:
            data = response.json()
        except ValueError:
            logging.error("Groq returned non-JSON body, status %s", response.status_code)
            return jsonify({"error": f"Groq returned status {response.status_code} with a non-JSON body."}), 502

        if not response.ok:
            err_msg = data.get("error", {}).get("message", str(data))
            logging.error("Groq API error %s: %s", response.status_code, err_msg)
            return jsonify({"error": err_msg}), response.status_code

        try:
            content_text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            logging.error("Unexpected Groq response shape: %s", data)
            return jsonify({"error": "Unexpected response shape from Groq."}), 502

        logging.info("Groq call succeeded")
        # Normalized to match the {content: [{type, text}]} shape the
        # frontend expects, regardless of which provider is behind it.
        return jsonify({"content": [{"type": "text", "text": content_text}]}), 200

    except requests.exceptions.Timeout:
        logging.error("Groq request timed out")
        return jsonify({"error": "Request to Groq timed out."}), 504
    except requests.exceptions.RequestException as e:
        logging.error("Network error calling Groq: %s", e)
        return jsonify({"error": f"Network error reaching Groq: {e}"}), 502


def open_browser():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    # Give the server a moment to actually start before opening the tab,
    # so we're not opening a page that isn't ready yet.
    Timer(1, open_browser).start()
    app.run(debug=True, port=5000, use_reloader=False)
