import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

SECURITY_YML_PATH = Path(
    os.environ.get("PICOCLAW_SECURITY_YML", "/root/.picoclaw/.security.yml")
)

_cached_config: tuple[str, str] | None = None


def load_asr_config(prefixes: list[str] | None = None, use_cache: bool = True) -> tuple[str, str]:
    global _cached_config
    if use_cache and _cached_config is not None:
        return _cached_config
    env_model = os.environ.get("ASR_MODEL", "").strip()
    env_key = os.environ.get("DASHSCOPE_API_KEY", "").strip()

    if env_model and env_key:
        _cached_config = (env_model, env_key)
        return _cached_config

    # Try .security.yml
    yml_result = _load_from_yml(prefixes)
    if yml_result is not None:
        yml_model, yml_key = yml_result
        model = env_model or yml_model
        key = env_key or yml_key
        if model and key:
            _cached_config = (model, key)
            return _cached_config

    # Fallback
    model = env_model or ""
    key = env_key or ""
    result = (model, key)
    if model and key:
        _cached_config = result
    return result


def _load_from_yml(prefixes: list[str] | None = None) -> tuple[str, str] | None:
    try:
        if not SECURITY_YML_PATH.exists():
            return None
        text = SECURITY_YML_PATH.read_text(encoding="utf-8")
        return _parse_yml(text, prefixes)
    except Exception as exc:
        logger.debug("Failed to read %s: %s", SECURITY_YML_PATH, exc)
        return None


def _parse_yml(text: str, prefixes: list[str] | None = None) -> tuple[str, str] | None:
    """Extract first model block (matching prefixes) with an api_key.

    Expected structure (indent = 2 spaces per level):
      <model-name>:0:
        api_keys:
          - <key>
    """
    lines = text.splitlines()
    found_model = ""
    in_model = False
    in_api_keys = False

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))

        if not in_model:
            if indent == 2 and stripped.endswith(":0:"):
                candidate = stripped[:-3]
                if prefixes is None or any(candidate.startswith(p) for p in prefixes):
                    found_model = candidate
                    in_model = True
            continue

        # Moved to another top-level model block
        if indent <= 2 and stripped.endswith(":0:"):
            # Check if this new block also matches
            candidate = stripped[:-3]
            in_model = False
            in_api_keys = False
            if prefixes is None or any(candidate.startswith(p) for p in prefixes):
                found_model = candidate
                in_model = True
            continue
        if indent == 0:
            break

        if indent == 4 and stripped == "api_keys:":
            in_api_keys = True
            continue

        if in_api_keys:
            if indent <= 4:
                in_api_keys = False
                continue
            if stripped.startswith("- "):
                key = stripped[2:].strip().strip('"').strip("'")
                if key:
                    return found_model, key

    return None
