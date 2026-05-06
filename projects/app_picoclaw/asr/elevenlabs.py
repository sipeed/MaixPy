import asyncio
import io
import logging
import wave

import numpy as np
import requests

from .config import load_asr_config

logger = logging.getLogger(__name__)

API_URL = "https://api.elevenlabs.io/v1/speech-to-text"


def _pcm_to_wav_bytes(pcm_int16: np.ndarray, sample_rate: int = 16000) -> bytes:
    """Convert int16 PCM samples to WAV file bytes."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_int16.tobytes())
    return buf.getvalue()


async def asr_session(pcm_data: np.ndarray) -> str:
    if len(pcm_data) < 3200:
        logger.info("Audio too short (%d samples), skipping recognition", len(pcm_data))
        return ""

    # Convert normalized float32 PCM to int16 PCM
    pcm_int16 = (pcm_data * 32768).clip(-32768, 32767).astype(np.int16)

    model, api_key = load_asr_config()
    if not api_key:
        logger.error("API key not found")
        return ""

    logger.debug("ASR model: %s (ElevenLabs)", model)

    wav_bytes = _pcm_to_wav_bytes(pcm_int16)

    headers = {
        "Xi-Api-Key": api_key,
    }
    files = {
        "file": ("audio.wav", wav_bytes, "audio/wav"),
    }
    data = {
        "model_id": model,
    }

    loop = asyncio.get_event_loop()
    resp = await loop.run_in_executor(
        None,
        lambda: requests.post(API_URL, headers=headers, files=files, data=data, timeout=120),
    )

    if resp.status_code != 200:
        logger.error("ElevenLabs API error %d: %s", resp.status_code, resp.text)
        return ""

    try:
        result = resp.json()
        transcript = result["text"]
        logger.info("Recognized: %s", transcript)
        return transcript.strip()
    except (KeyError, TypeError) as exc:
        logger.error("Failed to parse ElevenLabs response: %s — %s", exc, resp.text)
        return ""
