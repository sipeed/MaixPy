import asyncio
import base64
import json
import logging

import numpy as np
import websockets

from .config import load_asr_config

logger = logging.getLogger(__name__)

DASHSCOPE_URL_TPL = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime?model={model}"


async def asr_session(pcm_data: np.ndarray) -> str:
    if len(pcm_data) < 3200:
        logger.info("Audio too short (%d samples), skipping recognition", len(pcm_data))
        return ""
    # Convert normalized float32 PCM to int16 PCM
    pcm_int16 = (pcm_data * 32768).clip(-32768, 32767).astype(np.int16)
    audio_bytes = pcm_int16.tobytes()

    model, api_key = load_asr_config()
    if not api_key:
        logger.error("API key not found (DASHSCOPE_API_KEY / .security.yml)")
        return ""

    url = DASHSCOPE_URL_TPL.format(model=model)
    logger.debug("ASR model: %s", model)

    conn_headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1",
    }

    transcript = ""

    async with websockets.connect(url, extra_headers=conn_headers) as ws:
        await ws.send(json.dumps({
            "event_id": "event_001",
            "type": "session.update",
            "session": {
                "modalities": ["text"],
                "input_audio_format": "pcm",
                "sample_rate": 16000,
                "input_audio_transcription": {},
                "turn_detection": None
            }
        }))

        chunk_size = 3200  # 3200 bytes = 1600 samples = 0.1s @ 16kHz PCM16
        start = 0
        total = len(audio_bytes)
        while start < total:
            end = min(start + chunk_size, total)
            encoded = base64.b64encode(audio_bytes[start:end]).decode("utf-8")
            await ws.send(json.dumps({
                "event_id": f"event_audio_{start}",
                "type": "input_audio_buffer.append",
                "audio": encoded
            }))
            start += chunk_size
            await asyncio.sleep(0.01)

        await ws.send(json.dumps({"event_id": "event_commit", "type": "input_audio_buffer.commit"}))
        await ws.send(json.dumps({"event_id": "event_finish", "type": "session.finish"}))

        async for msg in ws:
            try:
                data = json.loads(msg)
                ev_type = data.get("type", "")
                logger.debug("%s", ev_type)
                if ev_type == "error":
                    err_code = data.get("error", {}).get("code", "unknown")
                    err_msg  = data.get("error", {}).get("message", "")
                    logger.error("Server error %s: %s", err_code, err_msg)
                    break
                elif ev_type == "conversation.item.input_audio_transcription.completed":
                    transcript = (
                        data.get("transcript")
                        or data.get("text")
                        or (data.get("transcription") or {}).get("text", "")
                    )
                    logger.info("Recognized: %s", transcript)
                elif ev_type == "session.finished":
                    if not transcript:
                        transcript = data.get("transcript", "")
                    break
            except Exception:
                pass

    return transcript.strip()
