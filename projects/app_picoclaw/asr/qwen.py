import base64
import io
import logging
import wave

import numpy as np
import requests

from .config import load_asr_config

logger = logging.getLogger(__name__)

API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"


def _pcm_to_base64_wav(pcm_int16: np.ndarray, sample_rate: int = 16000) -> str:
    """Convert int16 PCM samples to a base64-encoded WAV data URI."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_int16.tobytes())
    wav_bytes = buf.getvalue()
    b64 = base64.b64encode(wav_bytes).decode("utf-8")
    return f"data:audio/wav;base64,{b64}"


async def asr_session(pcm_data: np.ndarray) -> str:
    if len(pcm_data) < 3200:
        logger.info("Audio too short (%d samples), skipping recognition", len(pcm_data))
        return ""

    # Convert normalized float32 PCM to int16 PCM
    pcm_int16 = (pcm_data * 32768).clip(-32768, 32767).astype(np.int16)

    model, api_key = load_asr_config()
    if not api_key:
        logger.error("API key not found (DASHSCOPE_API_KEY / .security.yml)")
        return ""

    logger.debug("ASR model: %s (non-realtime)", model)

    data_uri = _pcm_to_base64_wav(pcm_int16)

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "input_audio", "input_audio": {"data": data_uri, "format": "wav"}}
                ],
            }
        ],
        "stream": False,
        "asr_options": {"enable_itn": False},
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    import asyncio
    loop = asyncio.get_event_loop()
    resp = await loop.run_in_executor(
        None,
        lambda: requests.post(API_URL, json=payload, headers=headers, timeout=120),
    )

    if resp.status_code != 200:
        logger.error("ASR API error %d: %s", resp.status_code, resp.text)
        return ""

    try:
        data = resp.json()
        transcript = data["choices"][0]["message"]["content"]
        logger.info("Recognized: %s", transcript)
        return transcript.strip()
    except (KeyError, IndexError, TypeError) as exc:
        logger.error("Failed to parse ASR response: %s — %s", exc, resp.text)
        return ""
