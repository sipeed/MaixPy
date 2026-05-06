import importlib
import logging

from .config import load_asr_config

logger = logging.getLogger(__name__)

_BACKEND_REGISTRY: list[tuple[str, str]] = [
    ("qwen3-asr-flash-realtime", ".qwen_realtime"),
    ("qwen3-asr-flash",          ".qwen"),
    ("whisper",                  ".whisper"),
    ("scribe_v1",                ".elevenlabs"),
]


class ASRNotConfiguredError(Exception):
    """Raised when no ASR model is configured."""


def _resolve_backend(model: str) -> str:
    """Return the module path for the given model name."""
    for prefix, module_path in _BACKEND_REGISTRY:
        if model.startswith(prefix):
            return module_path
    raise ValueError(
        f"No ASR backend registered for model '{model}'. "
        f"Known prefixes: {[p for p, _ in _BACKEND_REGISTRY]}"
    )


def get_asr_backend(use_cache: bool = True):
    prefixes = [p for p, _ in _BACKEND_REGISTRY]
    model, api_key = load_asr_config(use_cache=use_cache, prefixes=prefixes)
    if not model:
        raise ASRNotConfiguredError(
            "No ASR model configured."
        )

    module_path = _resolve_backend(model)
    logger.info("ASR routing: model=%s → %s", model, module_path)

    mod = importlib.import_module(module_path, package=__name__)
    return mod.asr_session


try:
    asr_session = get_asr_backend()
except ASRNotConfiguredError:
    asr_session = None

__all__ = ["asr_session", "get_asr_backend", "ASRNotConfiguredError"]
