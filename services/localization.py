# services/localization.py
import os
import httpx
import base64
from fastapi import HTTPException

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_BASE_URL = "https://api.sarvam.ai"

async def speech_to_text(audio_file_bytes: bytes, language_code: str = "hi-IN") -> str:
    if not SARVAM_API_KEY:
        return "Simulated STT: User requested scheme eligibility assistance in Hindi."

    url = f"{SARVAM_BASE_URL}/speech-to-text"
    headers = {"api-subscription-key": SARVAM_API_KEY}
    files = {"file": ("audio.wav", audio_file_bytes, "audio/wav")}
    data = {"model": "saaras:v1", "language_code": language_code}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, files=files, data=data)
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Sarvam STT failed.")
        return response.json().get("transcript", "")

async def text_to_speech(text: str, target_language_code: str = "hi-IN") -> bytes:
    if not SARVAM_API_KEY:
        return b""

    url = f"{SARVAM_BASE_URL}/text-to-speech"
    headers = {"api-subscription-key": SARVAM_API_KEY, "Content-Type": "application/json"}
    payload = {"inputs": [text], "target_language_code": target_language_code, "speaker": "anant", "model": "bulbul:v1"}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Sarvam TTS failed.")
        audios = response.json().get("audios", [])
        return base64.b64decode(audios[0]) if audios else b""