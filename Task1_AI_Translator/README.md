# AI Translator

A full-stack AI-powered language translation tool with tone control, grammar correction, idiom explanations, and AI-generated speech  built as a college project to actually learn full-stack development and AI API integration, not just assemble a template.

**Live demo:** [ai-translator-xi-seven.vercel.app](https://ai-translator-xi-seven.vercel.app)
**Built by:** [Vinit Gill](https://github.com/vinitgill) · [LinkedIn](https://linkedin.com/in/vinitgill)

---

## What it does

Most "AI translator" projects wrap a single API call in a form. This one goes further:

- **Tone-aware translation** — the same sentence translates differently depending on whether you pick Neutral, Formal, Casual, or Business tone
- **Automatic language detection** — no need to specify what you're translating from
- **Grammar correction** — fixes the source text before translating it
- **Word & idiom explainer** — look up any word or phrase for its meaning, synonyms, an example sentence, and cultural/idiomatic context
- **AI-generated speech** — hear the translation spoken aloud, powered by Gemini's native TTS model, with automatic fallback to the browser's built-in voice (and script-aware voice matching) if the AI voice is rate-limited
- **26+ languages** built in, plus a free-text option for any language not listed
- **Translation history** with tone tracking, stored locally in the browser
- **Dark/light mode, copy/download/share, keyboard shortcuts** — the small things that make it feel like a real product

## Tech stack

**Backend:** FastAPI (Python) · Google Gemini API (translation, grammar, explanations, TTS) · httpx for direct API calls

**Frontend:** Vanilla HTML/CSS/JavaScript  deliberately no framework, so every part of the app is understandable end-to-end without build tooling

**Why this stack:** built to actually learn the fundamentals (what an API is, how a backend and frontend talk to each other, how AI prompts are structured) rather than lean on a framework's abstractions on a first full-stack project.

## Screenshots

<img width="2474" height="1384" alt="image" src="https://github.com/user-attachments/assets/21bee132-e7dd-4488-bac2-92436a31b269" />


## Project structure

```text
translator-project/
├── backend/
│   ├── main.py
│   ├── services/
│   │   └── translation_service.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html
    ├── style.css
    └── script.js
```
## Running it locally

### 1. Get a free Gemini API key
Go to aistudio.google.com, sign in, and generate a free API key — no credit card required.

### 2. Backend setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```
Backend runs at http://127.0.0.1:8000 — visit /docs for interactive API testing.

### 3. Frontend setup
In a separate terminal:
```bash
cd frontend
python3 -m http.server 5500
```
Visit http://127.0.0.1:5500 in your browser.

## API endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| /api/translate | POST | Translate text with tone control and language auto-detection |
| /api/grammar-check | POST | Correct grammar in the input text |
| /api/explain | POST | Explain a word/phrase: meaning, synonyms, example, cultural notes |
| /api/speak | POST | Generate spoken audio (WAV) for translated text |

## Known limitations

Being upfront about these rather than hiding them:

- **Gemini's free tier has strict rate limits**, especially for the TTS models — a few requests per minute. The app falls back to the browser's built-in voice when the AI voice is rate-limited, but that fallback can't cover every language perfectly.
- **Custom-typed languages** don't have a fixed voice mapping — the app guesses a close voice by detecting the script of the translated text, which is best-effort, not guaranteed.
- **No persistent database** — translation history is stored in the browser's local storage.
- **No authentication** — single-user local/demo project, not a production multi-user deployment.

## What I learned building this

Full-stack architecture, prompt engineering for structured JSON outputs, working with real-world API constraints (model deprecation, rate limits, quota management), debugging build failures across Python versions, and iterating on visual design with intentional typography and color choices instead of defaults.

## License

MIT
