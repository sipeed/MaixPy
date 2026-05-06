import asyncio
import json
import logging
import os
import re
import socket
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator

import websockets

logger = logging.getLogger(__name__)

GATEWAY_HOST = "127.0.0.1"
GATEWAY_PORT = 18790
SECURITY_YML_PATH = Path(os.environ.get("PICOCLAW_SECURITY_YML", "/root/.picoclaw/.security.yml"))


def _load_pico_token() -> str:
    env_token = os.environ.get("PICO_TOKEN", "").strip()
    if env_token:
        return env_token

    try:
        if not SECURITY_YML_PATH.exists():
            return ""

        lines = SECURITY_YML_PATH.read_text(encoding="utf-8").splitlines()
        in_channels = False
        in_pico = False

        for raw in lines:
            line = raw.rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            indent = len(line) - len(line.lstrip(" "))

            if not in_channels:
                if indent == 0 and stripped in ("channels:", "channel_list:"):
                    in_channels = True
                continue

            if in_channels and indent == 0:
                break

            if not in_pico:
                if indent == 2 and stripped == "pico:":
                    in_pico = True
                continue

            if in_pico and indent <= 2:
                in_pico = False
                continue

            if in_pico and indent >= 4 and stripped.startswith("token:"):
                token = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                return token
    except Exception:
        pass

    return ""


@dataclass
class ToolCall:
    name: str
    args: str


@dataclass
class PicoEvent:
    kind: str
    content: str = ""
    delta: str = ""
    message_id: str = ""
    tool: ToolCall | None = None
    error_code: str = ""
    error_message: str = ""
    raw: dict | None = None


_TOOL_RE = re.compile(r'^🔧\s*`([^`]+)`\s*\n```\n(.*?)\n```\s*$', re.DOTALL)


def _parse_message(content: str) -> ToolCall | None:
    m = _TOOL_RE.match(content.strip())
    if m:
        return ToolCall(name=m.group(1), args=m.group(2).strip())
    return None


def _parse_tool_calls_payload(raw) -> ToolCall | None:
    if not isinstance(raw, list):
        return None
    for item in raw:
        if not isinstance(item, dict):
            continue
        fn = item.get("function") if isinstance(item.get("function"), dict) else None
        if not fn:
            continue
        name = fn.get("name") if isinstance(fn.get("name"), str) else ""
        args = fn.get("arguments") if isinstance(fn.get("arguments"), str) else ""
        if name:
            return ToolCall(name=name, args=args or "")
    return None


class PicoclawAgent:
    def __init__(
        self,
        host: str = GATEWAY_HOST,
        port: int = GATEWAY_PORT,
        token: str | None = None,
        idle_timeout: float = 0.0,
    ):
        self.ws_base   = f"ws://{host}:{port}/pico/ws"
        self._token    = token
        self._idle_timeout = idle_timeout
        self._ws       = None
        self._session_id = None
        self._lock     = asyncio.Lock()

    @property
    def token(self) -> str:
        if self._token is not None:
            return self._token
        return _load_pico_token()

    @staticmethod
    def _ws_open(ws) -> bool:
        if ws is None:
            return False
        closed = getattr(ws, "closed", None)
        if closed is not None:
            return not closed
        state = getattr(ws, "state", None)
        if state is not None:
            return getattr(state, "name", "") == "OPEN"
        return True

    async def _ensure_connected(self):
        if self._ws_open(self._ws):
            return
        self._session_id = str(uuid.uuid4())
        url     = f"{self.ws_base}?session_id={self._session_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            self._ws = await websockets.connect(url, additional_headers=headers)
        except TypeError:
            self._ws = await websockets.connect(url, extra_headers=headers)
        logger.debug("Connected session=%s", self._session_id)

    async def close(self):
        if self._ws_open(self._ws):
            await self._ws.close()
        self._ws = None

    async def astream(
        self,
        question: str,
        idle_timeout: float | None = None,
    ) -> AsyncIterator[PicoEvent]:
        if idle_timeout is None:
            idle_timeout = self._idle_timeout

        async with self._lock:
            await self._ensure_connected()
            ws = self._ws
            session_id = self._session_id

            logger.debug("Send: %s", question)
            await ws.send(json.dumps({
                "type":       "message.send",
                "id":         str(uuid.uuid4()),
                "session_id": session_id,
                "timestamp":  int(time.time() * 1000),
                "payload":    {"content": question},
            }, ensure_ascii=False))

            last_answer_id: str | None = None
            last_answer_content: str = ""

            while True:
                try:
                    if idle_timeout and idle_timeout > 0:
                        try:
                            raw = await asyncio.wait_for(ws.recv(), timeout=idle_timeout)
                        except asyncio.TimeoutError:
                            logger.debug("Stream idle for %ss, terminating turn.", idle_timeout)
                            return
                    else:
                        raw = await ws.recv()
                except websockets.ConnectionClosed as e:
                    logger.debug("Pico WS closed (code=%s): %s",
                                getattr(e, "code", "?"), e)
                    self._ws = None
                    return

                try:
                    msg = json.loads(raw)
                except Exception:
                    continue

                ev_type = msg.get("type", "")
                payload = msg.get("payload") or {}

                if ev_type == "typing.start":
                    yield PicoEvent(kind="typing_start", raw=msg)
                    continue

                if ev_type == "typing.stop":
                    yield PicoEvent(kind="typing_stop", raw=msg)
                    continue

                if ev_type == "message.update":
                    msg_id = payload.get("message_id") or ""
                    if msg_id and msg_id == last_answer_id:
                        new_content = payload.get("content", "") or ""
                        delta = (
                            new_content[len(last_answer_content):]
                            if new_content.startswith(last_answer_content)
                            else new_content
                        )
                        last_answer_content = new_content
                        yield PicoEvent(
                            kind="answer_delta",
                            content=new_content,
                            delta=delta,
                            message_id=msg_id,
                            raw=msg,
                        )
                    continue

                if ev_type == "message.delete":
                    if payload.get("message_id") == last_answer_id:
                        last_answer_id = None
                        last_answer_content = ""
                    yield PicoEvent(kind="raw", raw=msg)
                    continue

                if ev_type == "message.create":
                    content = payload.get("content", "") or ""
                    kind = (payload.get("kind") or "").strip().lower()
                    is_thought = bool(payload.get("thought")) or kind == "thought"
                    is_tool_calls = kind == "tool_calls"

                    tc = _parse_tool_calls_payload(payload.get("tool_calls"))
                    if tc is None:
                        tc = _parse_message(content)
                    if tc or is_tool_calls:
                        if tc is None:
                            yield PicoEvent(kind="raw", raw=msg)
                            continue
                        yield PicoEvent(kind="tool_call", tool=tc, raw=msg)
                        continue

                    if is_thought:
                        yield PicoEvent(kind="thought", content=content, raw=msg)
                        continue

                    last_answer_id = payload.get("message_id") or ""
                    last_answer_content = content
                    yield PicoEvent(
                        kind="answer_start",
                        content=content,
                        delta=content,
                        message_id=last_answer_id,
                        raw=msg,
                    )
                    continue

                if ev_type == "error":
                    yield PicoEvent(
                        kind="error",
                        error_code=str(payload.get("code", "")),
                        error_message=str(payload.get("message", "")),
                        raw=msg,
                    )
                    return

                yield PicoEvent(kind="raw", raw=msg)



def gateway_running(host: str = GATEWAY_HOST, port: int = GATEWAY_PORT) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def get_picoclaw_model() -> str:
    try:
        env = dict(os.environ)
        env["HOME"] = "/root"
        result = subprocess.run(
            ["picoclaw", "status"],
            capture_output=True, text=True, timeout=5,
            env=env, cwd="/root",
        )
        for line in result.stdout.splitlines():
            if line.startswith("Model:"):
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return ""


if __name__ == "__main__":
    import sys
    from config import setup_logging
    setup_logging()

    async def _test():
        agent = PicoclawAgent()

        for q in ["Hello, introduce yourself.", "What's the weather in Shenzhen today?"]:
            logger.debug("=" * 60)
            logger.debug("Q: %s", q)
            sys.stdout.write("A (streaming): ")
            sys.stdout.flush()

            tool_calls: list[ToolCall] = []
            fragments: list[str] = []

            async for ev in agent.astream(q):
                if ev.kind == "answer_start":
                    if fragments:
                        sys.stdout.write("\n\n")
                    fragments.append(ev.content)
                    sys.stdout.write(ev.delta)
                elif ev.kind == "answer_delta" and fragments:
                    fragments[-1] = ev.content
                    sys.stdout.write(ev.delta)
                elif ev.kind == "tool_call" and ev.tool:
                    tool_calls.append(ev.tool)
                    logger.debug("Tool: %s args=%s", ev.tool.name, ev.tool.args)
                elif ev.kind == "error":
                    logger.error("Error: %s – %s", ev.error_code, ev.error_message)
                sys.stdout.flush()

            sys.stdout.write("\n")
            sys.stdout.flush()
            full = "\n\n".join(s for s in (f.strip() for f in fragments) if s)
            if tool_calls:
                logger.debug("Tool calls: %s", ", ".join(tc.name for tc in tool_calls))
            logger.debug("Final answer (%d chars):\n%s", len(full), full)
            logger.debug("=" * 60)
            await asyncio.sleep(1)
        await agent.close()

    asyncio.run(_test())
