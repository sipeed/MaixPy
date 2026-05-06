import asyncio
import logging

import numpy as np
from maix import audio, app, image, display
from key import Key
from touch import Touch
from picoclaw import PicoclawAgent
from asr import asr_session, get_asr_backend, ASRNotConfiguredError
from install_picoclaw import (
    is_picoclaw_installed, install_picoclaw, ensure_picoclaw_launcher_running,
)
import config
from config import (
    setup_logging,
    FONT_PATH, FONT_NAME, FONT_NAME_LARGE,
    SAMPLE_RATE, AUDIO_CHANNELS, RECORDER_VOLUME,
)

logger = logging.getLogger(__name__)
from ui import (
    start_anim, stop_anim,
    show_no_speech, show_error,
    animate_speak_now, animate_transcribing, animate_thinking,
    StreamingRenderer, show_home_icon,
    show_install_prompt, animate_installing,
    get_exit_btn_rect, get_install_btn_rect,
)


# -----------------------------------------------------------------------
# Main application
# -----------------------------------------------------------------------
async def main():
    setup_logging()

    disp = display.Display()
    config.init_display(disp)

    image.load_font(FONT_NAME, FONT_PATH, size=config.FONT_SIZE)
    image.load_font(FONT_NAME_LARGE, FONT_PATH, size=config.FONT_SIZE_LARGE)
    image.set_default_font(FONT_NAME)

    key = Key()
    touch = Touch()

    disp.set_backlight(100)

    logger.debug("exit btn rect = %s, disp = %dx%d",
                 get_exit_btn_rect(), config.DISP_W, config.DISP_H)

    on_home_screen = False
    voice_touch_active = False

    def exit_button_tapped() -> bool:
        nonlocal voice_touch_active
        p = touch.consume_press()
        if p is None:
            if voice_touch_active and not touch.is_pressing():
                voice_touch_active = False
            return False
        if Touch.in_rect(p, get_exit_btn_rect()):
            return True
        if on_home_screen:
            ex, ey, ew, eh = get_exit_btn_rect()
            pad = max(16, int(min(config.DISP_W, config.DISP_H) * 0.06))
            exit_zone = (ex - pad, ey - pad, ew + pad * 2, eh + pad * 2)
            if not Touch.in_rect(p, exit_zone):
                voice_touch_active = True
        return False

    def is_voice_held() -> bool:
        nonlocal voice_touch_active
        if not voice_touch_active:
            return False
        _, _, pressed = touch.update()
        if not pressed:
            voice_touch_active = False
        return voice_touch_active

    async def wait_install_decision() -> str:
        """Wait for user to tap install or tap exit. Returns 'install'/'exit'."""
        while not app.need_exit():
            p = touch.consume_press()
            if p is not None:
                if Touch.in_rect(p, get_exit_btn_rect()):
                    logger.debug("install screen: exit tapped at %s", p)
                    return "exit"
                btn = get_install_btn_rect()
                if btn is not None and Touch.in_rect(p, btn):
                    logger.debug("install screen: install tapped at %s", p)
                    # Brief pressed-state feedback before kicking off install.
                    show_install_prompt(disp, pressed=True)
                    await asyncio.sleep(0.12)
                    return "install"
            await asyncio.sleep(0.03)
        return "exit"

    # If picoclaw isn't installed, show install screen and wait for confirmation.
    if not is_picoclaw_installed():
        logger.debug("picoclaw not installed; prompting user")
        show_install_prompt(disp)
        if (await wait_install_decision()) != "install":
            disp.set_backlight(0)
            key.close()
            touch.close()
            return

        start_anim(animate_installing(disp))
        try:
            await asyncio.to_thread(install_picoclaw, True)
        except Exception as exc:
            stop_anim()
            logger.exception("install failed: %s", exc)
            await show_error(disp, "Install failed")
            disp.set_backlight(0)
            key.close()
            touch.close()
            return
        stop_anim()
    else:
        # Already installed: ensure launcher is running on every startup.
        ensure_picoclaw_launcher_running()

    show_home_icon(disp)
    on_home_screen = True

    recorder = audio.Recorder(sample_rate=SAMPLE_RATE, channel=AUDIO_CHANNELS)
    recorder.volume(RECORDER_VOLUME)
    recorder.reset(True)

    agent = PicoclawAgent()
    _asr_fn = asr_session

    async def record_audio_until_release() -> np.ndarray | None:
        """Record while key is pressed, stop on release, return float32 PCM or None."""
        start_anim(animate_speak_now(disp))

        record_ms = 50
        sr = recorder.sample_rate()
        pcm_chunks: list = []
        loop = asyncio.get_running_loop()

        def _blocking_record() -> bytes:
            return recorder.record(record_ms) or b""

        await loop.run_in_executor(None, lambda: recorder.reset(True))

        retried_first = False
        while (key.is_pressed() or is_voice_held()) and not app.need_exit():
            raw = await loop.run_in_executor(None, _blocking_record)
            if len(raw) >= 2:
                samples = (
                    np.frombuffer(raw, dtype=np.int16)
                    .astype(np.float32) / 32768.0
                )
                pcm_chunks.append(samples)
            elif not retried_first and not pcm_chunks:
                retried_first = True
                await loop.run_in_executor(None, lambda: recorder.reset(True))

        if not pcm_chunks:
            return None
        pcm_all = np.concatenate(pcm_chunks)
        logger.debug("record done: %.2fs", pcm_all.size / max(1, sr))
        return pcm_all

    async def transcribe_audio(pcm_all: np.ndarray) -> str | None:
        nonlocal _asr_fn
        if _asr_fn is None:
            try:
                _asr_fn = get_asr_backend(use_cache=False)
            except (ASRNotConfiguredError, Exception):
                pass
        if _asr_fn is None:
            stop_anim()
            logger.warning("ASR not configured, cannot transcribe")
            await show_error(disp, "ASR not configured")
            return None

        logger.debug("Uploading for transcription...")
        start_anim(animate_transcribing(disp))
        try:
            result = await _asr_fn(pcm_all)
            logger.info("Transcription: %s", result) if result else logger.info("No speech recognized")
            return result or ""
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error("Transcription failed: %s", e)
            return ""

    async def stream_agent_until_interrupt(text: str) -> tuple[str, list[str], bool]:
        logger.debug("Asking PicoClaw...")
        tool_names: list[str] = []
        fragments: list[str] = []
        answer_started = False
        interrupted = False

        start_anim(animate_thinking(disp, tool_names))

        renderer = StreamingRenderer(disp, text)

        def current_answer() -> str:
            return "\n\n".join(s for s in (f.strip() for f in fragments) if s)

        async def render():
            await renderer.update(current_answer(), tool_names)

        async def consume_stream():
            nonlocal answer_started
            async for ev in agent.astream(text):
                if ev.kind == "answer_start":
                    if not answer_started:
                        # Switch from thinking animation to live render.
                        stop_anim()
                        answer_started = True
                    fragments.append(ev.content)
                    await render()
                elif ev.kind == "answer_delta" and fragments:
                    fragments[-1] = ev.content
                    if answer_started:
                        await render()
                elif ev.kind == "tool_call" and ev.tool:
                    tool_names.append(ev.tool.name)
                    if answer_started:
                        await render()
                elif ev.kind == "error":
                    logger.error("PicoClaw error: %s – %s",
                                 ev.error_code, ev.error_message)

        async def wait_key_interrupt():
            while not key.is_pressed() and not app.need_exit():
                await asyncio.sleep(0.05)

        async def wait_exit_interrupt():
            while not app.need_exit():
                if exit_button_tapped():
                    logger.debug("streaming: exit tapped")
                    return True
                await asyncio.sleep(0.03)
            return False

        stream_task = asyncio.create_task(consume_stream())
        interrupt_task = asyncio.create_task(wait_key_interrupt())
        exit_task = asyncio.create_task(wait_exit_interrupt())
        try:
            done, pending = await asyncio.wait(
                [stream_task, interrupt_task, exit_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for t in pending:
                t.cancel()
                try:
                    await t
                except (asyncio.CancelledError, Exception):
                    pass

            if exit_task in done:
                interrupted = True
                logger.debug("PicoClaw exited via touch, returning home")
                try:
                    await agent.close()
                except Exception as e:
                    logger.debug("agent.close on exit: %s", e)
            elif interrupt_task in done and not stream_task.done():
                interrupted = True
                logger.debug("PicoClaw interrupted, ready for next input")
                try:
                    await agent.close()
                except Exception as e:
                    logger.debug("agent.close on interrupt: %s", e)
        except Exception as e:
            logger.error("PicoClaw streaming error: %s", e)
        finally:
            if not stream_task.done():
                stream_task.cancel()
            if not interrupt_task.done():
                interrupt_task.cancel()
            if not exit_task.done():
                exit_task.cancel()
            if not answer_started:
                stop_anim()

        return current_answer(), tool_names, interrupted

    async def _active_cycle():
        """Run one complete voice interaction cycle."""
        try:
            pcm_all = await record_audio_until_release()
            if pcm_all is None:
                return

            result = await transcribe_audio(pcm_all)
            stop_anim()
            if result is None:
                return
            if not result:
                await show_no_speech(disp)
                return

            answer, _tool_names, interrupted = await stream_agent_until_interrupt(result)
            if interrupted:
                return

            if answer:
                logger.debug("PicoClaw response: %s", answer)
            else:
                await show_error(disp, "No response")
                return

            while not key.is_pressed() and not app.need_exit():
                if exit_button_tapped():
                    return
                await asyncio.sleep(0.05)

        finally:
            try:
                stop_anim()
            except Exception:
                pass

    try:
        while not app.need_exit():
            if exit_button_tapped():
                break
            if not key.is_pressed() and not voice_touch_active:
                await asyncio.sleep(0.05)
                continue

            on_home_screen = False
            await _active_cycle()
            show_home_icon(disp)
            on_home_screen = True

    except KeyboardInterrupt:
        logger.info("Exit")
    finally:
        stop_anim()
        disp.set_backlight(0)
        key.close()
        touch.close()
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
