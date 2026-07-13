from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.translation_service import translate_text, correct_grammar, explain_word, text_to_speech

app = FastAPI(title="AI Translator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TranslateRequest(BaseModel):
    text: str
    target_language: str
    tone: str = "neutral"


class GrammarRequest(BaseModel):
    text: str


class ExplainRequest(BaseModel):
    word: str
    context: str = ""


class SpeakRequest(BaseModel):
    text: str


@app.get("/")
def health_check():
    return {"status": "AI Translator backend is running"}


@app.post("/api/translate")
def translate(request: TranslateRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    try:
        return translate_text(
            text=request.text,
            target_language=request.target_language,
            tone=request.tone
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.post("/api/grammar-check")
def grammar_check(request: GrammarRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    try:
        return correct_grammar(request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grammar check failed: {str(e)}")


@app.post("/api/explain")
def explain(request: ExplainRequest):
    if not request.word.strip():
        raise HTTPException(status_code=400, detail="Word cannot be empty")
    try:
        return explain_word(request.word, request.context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")


@app.post("/api/speak")
def speak(request: SpeakRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    try:
        audio_bytes = text_to_speech(request.text)
        return Response(content=audio_bytes, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech generation failed: {str(e)}")
