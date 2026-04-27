from flask import Flask, request, jsonify, render_template
from datetime import datetime
import os
import json
import re
import requests
from dotenv import load_dotenv
import PyPDF2

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

MAX_QUESTIONS_PER_DAY = 15
COOLDOWN_SECONDS = 60
usage = {}

DATA_FILE = "data.json"


def load_stats():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"xp": 0, "level": 1, "streak": 0}


def save_stats(stats):
    with open(DATA_FILE, "w") as f:
        json.dump(stats, f)


def can_request(ip, requested_questions):
    now = datetime.now()

    if ip not in usage:
        usage[ip] = {"count": 0, "last_request": now, "day": now.date()}
        return True, None

    user = usage[ip]

    if user["day"] != now.date():
        user["count"] = 0
        user["day"] = now.date()

    if (now - user["last_request"]).total_seconds() < COOLDOWN_SECONDS:
        return False, f"Wait {COOLDOWN_SECONDS} seconds."

    if user["count"] + requested_questions > MAX_QUESTIONS_PER_DAY:
        return False, "Daily limit reached (5 questions)."

    return True, None


def record_request(ip, num_questions):
    now = datetime.now()
    usage[ip]["count"] += num_questions
    usage[ip]["last_request"] = now


def clean_json(text):
    if not text:
        return ""
    text = text.replace("```json", "").replace("```", "")
    return text.strip()


def generate_quiz_with_retry(text, num_questions, retries=3):
    prompt = f"""
You are a strict JSON generator.

Return ONLY valid JSON.
No explanations.
No markdown.
No extra text.

Rules:
- Output MUST be valid JSON array
- Each object must include:
  - question (full sentence)
  - choices (exactly 4 full options)
  - answer (must match one choice)
  - explanation (complete sentence)

Do NOT cut off output.

TEXT:
{text[:1500]}
"""

    last_raw = None

    for _ in range(retries):
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                }
            )

            data = response.json()
            raw = data.get("response", "")

            if not raw:
                continue

            raw = clean_json(raw)
            last_raw = raw

            parsed = json.loads(raw)

            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed

        except Exception:
            continue

    raise Exception(f"Failed to generate valid JSON. Last output: {last_raw}")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate_quiz", methods=["POST"])
def generate_quiz_route():
    ip = request.remote_addr
    data = request.json

    text = data.get("text", "")
    num_questions = min(int(data.get("num_questions", 1)), MAX_QUESTIONS_PER_DAY)

    allowed, message = can_request(ip, num_questions)
    if not allowed:
        return jsonify({"error": message}), 429

    try:
        quiz_data = generate_quiz_with_retry(text, num_questions)
        record_request(ip, num_questions)
        return jsonify({"quiz": quiz_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    try:
        file = request.files.get("file")

        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        if not file.filename.endswith(".pdf"):
            return jsonify({"error": "Only PDF files allowed"}), 400

        reader = PyPDF2.PdfReader(file)
        text = ""

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        return jsonify({"text": text[:8000]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/stats", methods=["GET"])
def get_stats():
    return jsonify(load_stats())


@app.route("/update_stats", methods=["POST"])
def update_stats():
    data = request.json
    stats = load_stats()

    stats["xp"] = data.get("xp", stats["xp"])
    stats["level"] = data.get("level", stats["level"])
    stats["streak"] = data.get("streak", stats["streak"])

    save_stats(stats)

    return jsonify(stats)


if __name__ == "__main__":
    app.run(debug=True)