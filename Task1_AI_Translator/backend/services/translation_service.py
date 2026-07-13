import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


def translate_text(text: str, target_language: str, tone: str = "neutral") -> dict:
    system_prompt = f"""You are a professional translator.
Translate the user's text into {target_language}.
Use a {tone} tone.
Also detect the source language of the original text.

Respond ONLY in this exact JSON format, nothing else:
{{
  "source_language": "detected language name",
  "translation": "the translated text"
}}"""

    response = client.chat.completions.create(
        model="gemini-flash-lite-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    import json
    return json.loads(response.choices[0].message.content)


def correct_grammar(text: str) -> dict:
    system_prompt = """You are a grammar expert. Correct any grammar, spelling,
or punctuation mistakes in the user's text. Keep the meaning and tone identical.

Respond ONLY in this exact JSON format:
{
  "corrected_text": "the corrected version",
  "had_errors": true or false
}"""

    response = client.chat.completions.create(
        model="gemini-flash-lite-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    import json
    return json.loads(response.choices[0].message.content)


def text_to_speech(text: str) -> bytes:
    """
    Generates spoken audio using Gemini's native TTS model.
    Returns raw WAV audio bytes.
    """
    import httpx
    import base64
    import wave
    import io

    api_key = os.getenv("GEMINI_API_KEY")

    candidate_models = [
        "gemini-2.5-flash-preview-tts",
        "gemini-2.5-pro-preview-tts",
        "gemini-3.1-flash-tts-preview",
    ]

    last_error = None
    for model_name in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": text}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {"voiceName": "Kore"}
                    }
                },
            },
        }
        try:
            resp = httpx.post(url, json=payload, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()
            audio_b64 = data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
            pcm_bytes = base64.b64decode(audio_b64)

            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(24000)
                wav_file.writeframes(pcm_bytes)

            return wav_buffer.getvalue()
        except Exception as e:
            last_error = e
            continue

    raise Exception(f"All TTS models failed. Last error: {last_error}")


def explain_word(word_or_phrase: str, context: str = "") -> dict:
    system_prompt = """You are a language teacher. For the given word or phrase,
provide a clear explanation, 3 synonyms, one example sentence, and note if it's
an idiom or has cultural significance (empty string if not applicable).

Respond ONLY in this exact JSON format:
{
  "meaning": "clear simple explanation",
  "synonyms": ["word1", "word2", "word3"],
  "example_sentence": "a natural example sentence using it",
  "idiom_or_cultural_note": "explanation if relevant, else empty string"
}"""

    user_content = f"Word/phrase: {word_or_phrase}"
    if context:
        user_content += f"\nContext it appeared in: {context}"

    response = client.chat.completions.create(
        model="gemini-flash-lite-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        response_format={"type": "json_object"},
        temperature=0.4,
    )

    import json
    return json.loads(response.choices[0].message.content)
