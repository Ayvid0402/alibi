# 🕵️ The Alibi

A noir interrogation game where a real LLM plays the detective — it reads
your typed answers, decides how suspicious each one is, catches real
contradictions in your story, and delivers its own verdict at the end.

Built with Python (Flask), HTML/JS, and the Groq API (OpenAI's open-weight
GPT-OSS models, running on Groq's fast inference hardware).

---

## 🗺️ How It Works

👤 You choose a role (Innocent or Killer)
↓
🕵️ Detective asks an opening question
↓
✍️ You type a free-text answer
↓
🖥️ Flask backend sends the full transcript to Groq, with your real API key
↓
🧠 The model (playing the detective) replies in character, adjusts a
   suspicion meter, and flags contradictions with what you said earlier
↓
🔁 Repeat until suspicion hits 100%, 8 questions pass, or you end it
↓
⚖️ The detective delivers a final verdict + reasoning, based only on the
   transcript

---

## 📁 Project Structure

```
the-alibi-app/
│
├── 📁 templates/
│   └── index.html         ← the game itself (frontend)
├── 📁 logs/                ← created automatically, one log file per day
├── 📄 app.py                ← Flask backend, proxies calls to Groq
├── 📄 requirements.txt       ← Python dependencies
├── 📄 .env.example           ← copy this to .env and add your key
├── 📄 .env                   ← your real API key (never share this!)
└── 📄 README.md              ← this file
```

---

## ⚙️ Setup Instructions

### STEP 1: Open the project folder
```bash
cd the-alibi-app
```

### STEP 2: Install required libraries
```bash
pip install -r requirements.txt
```

### STEP 3: Get your FREE Groq API key
1. Go to https://console.groq.com
2. Sign up for free (no credit card needed!)
3. Click API Keys → Create API Key
4. Copy the key (starts with `gsk_...`)

### STEP 4: Create your .env file
Copy the example file and paste in your real key:
```bash
cp .env.example .env
```
Then edit `.env` so it looks like:
```
GROQ_API_KEY=gsk_your_real_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

### STEP 5: Run the app
```bash
python app.py
```

### STEP 6: Open it in your browser
Go to:
```
http://localhost:5000
```

---

## 🔒 How the key stays safe

The browser never talks to Groq directly. The game's JavaScript calls
`/api/chat` on your own Flask server. `app.py` reads `GROQ_API_KEY` from
`.env`, attaches it server-side, and forwards the request to Groq. The key
never appears in any file your browser downloads or can inspect.

```
Browser (game)  →  POST /api/chat  →  Flask (app.py)  →  Groq API
                                            ↑
                                  GROQ_API_KEY (from .env)
```

---

## 📝 Logs

Every call to Groq is logged automatically:
```
logs/
└── alibi_20260927.log
```

Log format:
```
2026-09-27 10:04:12 - INFO - Calling Groq API | model=openai/gpt-oss-20b | 3 messages
2026-09-27 10:04:13 - INFO - Groq call succeeded
```

---

## ⚠️ Important Notes

- Never share your `.env` file or API key
- `.env` should never be committed to git — add it to `.gitignore`
- If you see "GROQ_API_KEY not set" in the game, check that `.env` exists
  in the same folder as `app.py` and contains a real key
- Groq's older `llama-3.1-8b-instant` / `llama-3.3-70b-versatile` models
  were retired from the free/dev tier in August 2026 — this project uses
  the current `openai/gpt-oss-20b` model by default. Swap to
  `openai/gpt-oss-120b` in `.env` (`GROQ_MODEL=...`) if you want a sharper
  detective and don't mind it being slower
- Check https://console.groq.com for current free-tier limits and pricing

---

## 🔮 Future Improvements

- Save finished case transcripts to an `outputs/` folder
- Add a difficulty setting (stricter or more lenient detective)
- Support multiple concurrent players/sessions
- Deploy it (e.g. Render, Railway, Fly.io) so it's reachable outside localhost

