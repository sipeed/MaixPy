import asyncio
import math
import psutil

from maix import image

import config
from config import (
    ICON_PATH, TEXT_MARGIN,
    FONT_NAME, FONT_NAME_LARGE,
)


# ---------------------------------------------------------------------------
# Animation task management
# ---------------------------------------------------------------------------
_anim_task: asyncio.Task | None = None


def start_anim(coro) -> None:
    global _anim_task
    if _anim_task and not _anim_task.done():
        _anim_task.cancel()
    _anim_task = asyncio.create_task(coro)


def stop_anim() -> None:
    global _anim_task
    if _anim_task and not _anim_task.done():
        _anim_task.cancel()
    _anim_task = None


# Cached splash canvases keyed by prompt text/color tuple.
_home_cache: dict = {}


def get_exit_btn_rect() -> tuple[int, int, int, int]:
    """Return (x, y, w, h) of the top-left exit button hit area."""
    W, H = config.DISP_W, config.DISP_H
    size = max(40, int(min(W, H) * 0.11))
    margin = max(6, int(min(W, H) * 0.02))
    return (margin, margin, size, size)


def _draw_exit_button(canvas) -> None:
    x, y, w, h = get_exit_btn_rect()
    cx, cy = x + w // 2, y + h // 2
    # Simple "<" arrow icon, no background.
    arm = max(8, int(min(w, h) * 0.32))
    thick = max(3, int(min(w, h) * 0.10))
    col = image.Color.from_rgb(235, 235, 240)
    # Two strokes forming '<'
    canvas.draw_line(cx + arm // 2, cy - arm, cx - arm // 2, cy, col, thickness=thick)
    canvas.draw_line(cx - arm // 2, cy, cx + arm // 2, cy + arm, col, thickness=thick)


# Cached install button hit rect, computed in _build_splash when button=True.
_install_btn_rect: tuple[int, int, int, int] | None = None
_home_speak_btn_rect: tuple[int, int, int, int] | None = None
_mic_btn_rect: tuple[int, int, int, int] | None = None


def get_install_btn_rect() -> tuple[int, int, int, int] | None:
    """Return (x, y, w, h) of the install button, or None if not yet built."""
    return _install_btn_rect


def get_home_speak_btn_rect() -> tuple[int, int, int, int] | None:
    """Return (x, y, w, h) of home 'PRESS TO SPEAK' button."""
    return _home_speak_btn_rect


def get_mic_btn_rect() -> tuple[int, int, int, int] | None:
    """Return (x, y, w, h) of microphone hold-to-talk button."""
    return _mic_btn_rect


def _build_splash(text: str, glow_rgb: tuple, core_rgb: tuple,
                  button: bool = False, pressed: bool = False):
    global _install_btn_rect
    W, H = config.DISP_W, config.DISP_H
    icon = image.load(ICON_PATH)
    iw, ih = icon.width(), icon.height()

    bottom_reserve = max(72, int(H * 0.22))
    top_pad = max(8, int(H * 0.04))
    avail_h = H - bottom_reserve - top_pad
    avail_w = W - 2 * max(8, int(W * 0.05))

    scale = min(avail_w / iw, avail_h / ih)
    scale = max(0.1, min(scale, 4.0))
    new_w = max(1, int(iw * scale))
    new_h = max(1, int(ih * scale))
    if (new_w, new_h) != (iw, ih):
        icon = icon.resize(new_w, new_h, image.Fit.FIT_CONTAIN, image.ResizeMethod.BILINEAR)
        iw, ih = new_w, new_h

    canvas = image.Image(W, H, image.Format.FMT_RGB888)
    canvas.draw_rect(0, 0, W, H, image.Color.from_rgb(0, 0, 0), thickness=-1)
    ix = (W - iw) // 2
    iy = top_pad + (avail_h - ih) // 2
    canvas.draw_image(ix, iy, icon)

    image.set_default_font(FONT_NAME_LARGE)
    tw, th = image.string_size(text)
    x = (W - tw) // 2
    y = H - bottom_reserve + (bottom_reserve - th) // 3

    if button:
        # Render text inside a clearly visible button.
        pad_x = max(14, int(W * 0.05))
        pad_y = max(8, int(H * 0.018))
        bw = tw + pad_x * 2
        bh = th + pad_y * 2
        bx = (W - bw) // 2
        # Sit near the top of the bottom band so it feels closer to the icon.
        by = H - bottom_reserve + max(0, int(bottom_reserve * 0.12))

        # Color scheme: fill = darker glow, border = core, text = core.
        fill_rgb = _mix((0, 0, 0), glow_rgb, 0.55 if not pressed else 0.85)
        border_rgb = core_rgb
        text_rgb = core_rgb if not pressed else _mix(core_rgb, (255, 255, 255), 0.2)

        # Drop shadow (skip when pressed for an "inset" feel).
        if not pressed:
            shadow = image.Color.from_rgb(0, 0, 0)
            canvas.draw_rect(bx + 2, by + 3, bw, bh, shadow, thickness=-1)

        canvas.draw_rect(bx, by, bw, bh, _rgb(fill_rgb), thickness=-1)
        border_thick = 2 if not pressed else 3
        canvas.draw_rect(bx, by, bw, bh, _rgb(border_rgb), thickness=border_thick)

        tx = bx + (bw - tw) // 2
        ty = by + (bh - th) // 2
        if pressed:
            tx += 1
            ty += 1
        canvas.draw_string(tx, ty, text, _rgb(text_rgb))

        _install_btn_rect = (bx, by, bw, bh)
    else:
        glow = image.Color.from_rgb(*glow_rgb)
        core = image.Color.from_rgb(*core_rgb)
        canvas.draw_string(x - 1, y, text, glow)
        canvas.draw_string(x + 1, y, text, glow)
        canvas.draw_string(x, y - 1, text, glow)
        canvas.draw_string(x, y + 1, text, glow)
        canvas.draw_string(x, y, text, core)

    image.set_default_font(FONT_NAME)
    _draw_exit_button(canvas)
    return canvas


def _get_wifi_ip() -> str | None:
    try:
        addrs = psutil.net_if_addrs().get('wlan0', [])
        for addr in addrs:
            if addr.family == 2:
                return addr.address
    except Exception:
        pass
    return None


def show_home_icon(disp) -> None:
    global _home_speak_btn_rect
    ip = _get_wifi_ip()
    ip_label = f"http://{ip}:18800" if ip else ""
    key = ("PRESS TO SPEAK", "home_btn", ip_label)
    canvas = _home_cache.get(key)
    if canvas is None:
        canvas = _build_splash("PRESS TO SPEAK", (40, 140, 220), (125, 225, 255),
                               button=True, pressed=False)
        _home_speak_btn_rect = _install_btn_rect
        if ip_label:
            W, H = config.DISP_W, config.DISP_H
            btn = _home_speak_btn_rect
            image.set_default_font(FONT_NAME)
            tw, th = image.string_size(ip_label)
            x = (W - tw) // 2
            if btn is not None:
                bx, by, bw, bh = btn
                gap = max(10, int(H * 0.05))
                y = by - th - gap
            else:
                bottom_reserve = max(72, int(H * 0.22))
                y = H - bottom_reserve - th - max(6, int(H * 0.02))
            canvas.draw_string(x, y, ip_label, image.Color.from_rgb(100, 160, 255))
        _home_cache[key] = canvas
    disp.show(canvas)


def show_record_screen(disp, pressed: bool = False) -> None:
    """Record page with a centered microphone button."""
    global _mic_btn_rect
    key = ("record_screen", "pressed" if pressed else "idle")
    canvas = _home_cache.get(key)
    if canvas is None:
        W, H = config.DISP_W, config.DISP_H
        canvas = image.Image(W, H, image.Format.FMT_RGB888)
        bg = image.Color.from_rgb(8, 12, 24)
        canvas.draw_rect(0, 0, W, H, bg, thickness=-1)

        cx, cy = W // 2, int(H * 0.40)
        r_outer = max(32, int(min(W, H) * 0.15))
        r_inner = max(24, int(r_outer * 0.72))
        ring = image.Color.from_rgb(90, 165, 255)
        fill = image.Color.from_rgb(40, 95, 180)

        canvas.draw_circle(cx, cy, r_outer, ring, thickness=3)
        canvas.draw_circle(cx, cy, r_inner, fill, thickness=-1)

        # Simple mic glyph (capsule + stem + base)
        cap_w = max(12, int(r_inner * 0.52))
        cap_h = max(16, int(r_inner * 0.78))
        cap_x = cx - cap_w // 2
        cap_y = cy - int(cap_h * 0.62)
        mic_col = image.Color.from_rgb(225, 240, 255)
        canvas.draw_rect(cap_x, cap_y, cap_w, cap_h, mic_col, thickness=-1)
        canvas.draw_circle(cx, cap_y, cap_w // 2, mic_col, thickness=-1)
        stem_top = cap_y + cap_h + 2
        stem_h = max(8, int(r_inner * 0.35))
        canvas.draw_line(cx, stem_top, cx, stem_top + stem_h, mic_col, thickness=3)
        base_w = max(16, int(r_inner * 0.8))
        by = stem_top + stem_h + 2
        canvas.draw_line(cx - base_w // 2, by, cx + base_w // 2, by, mic_col, thickness=3)

        image.set_default_font(FONT_NAME_LARGE)
        title = "HOLD TO RECORD"
        tw, _ = image.string_size(title)
        canvas.draw_string((W - tw) // 2, int(H * 0.63), title, image.Color.from_rgb(190, 220, 255))

        image.set_default_font(FONT_NAME)
        hint1 = "Please configure asr first"
        tw1, _ = image.string_size(hint1)
        canvas.draw_string((W - tw1) // 2, int(H * 0.76), hint1, image.Color.from_rgb(140, 165, 200))

        url = "https://wiki.sipeed.com/rvclaw"
        url_lines, _ = _wrap(url, max_lines=2, max_w=max(1, W - 2 * max(6, int(W * 0.03))))
        for i, line in enumerate(url_lines):
            tw2, _ = image.string_size(line)
            canvas.draw_string((W - tw2) // 2, int(H * 0.87) + i * max(14, int(H * 0.05)),
                               line, image.Color.from_rgb(105, 130, 170))

        _draw_exit_button(canvas)
        _mic_btn_rect = (cx - r_outer, cy - r_outer, r_outer * 2, r_outer * 2)
        _home_cache[key] = canvas
    disp.show(canvas)


def show_install_prompt(disp, pressed: bool = False) -> None:
    key = ("INSTALL PicoClaw", "install_pressed" if pressed else "install")
    canvas = _home_cache.get(key)
    if canvas is None:
        canvas = _build_splash("INSTALL PicoClaw", (40, 110, 200), (130, 200, 255),
                               button=True, pressed=pressed)
        _home_cache[key] = canvas
    disp.show(canvas)


async def animate_installing(disp, status_text: str = "Installing PicoClaw..."):
    """Indeterminate progress animation while picoclaw is being installed."""
    W, H = config.DISP_W, config.DISP_H
    cx, cy = W // 2, int(H * 0.42)
    bar_w = int(W * 0.6)
    bar_h = max(8, int(H * 0.018))
    bar_x = (W - bar_w) // 2
    bar_y = int(H * 0.55)
    seg_w = max(40, int(bar_w * 0.28))
    y_title = int(H * 0.66)
    y_sub = int(H * 0.74)

    BG = (8, 12, 22)
    TRACK = (28, 36, 60)
    HEAD = (110, 200, 255)
    TITLE = (220, 230, 255)
    SUB = (120, 130, 160)

    PERIOD = 70
    frame = 0
    while True:
        img = image.Image(W, H, image.Format.FMT_RGB888)
        img.draw_rect(0, 0, W, H, _rgb(BG), thickness=-1)

        # Pulsing dot above the bar
        breath = (math.sin(frame * 0.18) + 1) * 0.5
        img.draw_circle(cx, cy, max(8, int(min(W, H) * 0.045)),
                        _rgb(_mix(BG, HEAD, 0.25 + 0.5 * breath)), thickness=-1)

        # Track + sliding segment
        img.draw_rect(bar_x, bar_y, bar_w, bar_h, _rgb(TRACK), thickness=-1)
        phase = (frame % PERIOD) / PERIOD
        eased = _smoothstep(phase)
        seg_x = bar_x - seg_w + int((bar_w + seg_w) * eased)
        # clip into bar bounds
        sx = max(bar_x, seg_x)
        sw = min(bar_x + bar_w, seg_x + seg_w) - sx
        if sw > 0:
            img.draw_rect(sx, bar_y, sw, bar_h, _rgb(HEAD), thickness=-1)

        _draw_centered_text(img, status_text, y_title, TITLE, W)
        _draw_centered_text(img, "Please wait", y_sub, SUB, W)

        disp.show(img)
        frame += 1
        await asyncio.sleep(0.02)


async def show_no_speech(disp, duration: float = 2.0):
    W, H = config.DISP_W, config.DISP_H
    cx, cy = W // 2, int(H * 0.375)
    r = max(8, int(min(W, H) * 0.117))
    y_title = int(H * 0.583)
    y_sub = int(H * 0.687)

    img = image.Image(W, H, image.Format.FMT_RGB888)
    img.draw_rect(0, 0, W, H, image.Color.from_rgb(20, 10, 10), thickness=-1)
    img.draw_circle(cx, cy, r, image.Color.from_rgb(60, 30, 0), thickness=-1)
    img.draw_circle(cx, cy, r, image.Color.from_rgb(255, 160, 30), thickness=3)
    tw, _ = image.string_size("No speech detected")
    img.draw_string((W - tw) // 2, y_title,
                    "No speech detected", image.Color.from_rgb(255, 160, 30))
    tw2, _ = image.string_size("Please try again")
    img.draw_string((W - tw2) // 2, y_sub,
                    "Please try again", image.Color.from_rgb(120, 120, 150))
    disp.show(img)
    await asyncio.sleep(duration)


async def show_error(disp, message: str = "No response", duration: float = 2.0):
    W, H = config.DISP_W, config.DISP_H
    cx, cy = W // 2, int(H * 0.375)
    r = max(8, int(min(W, H) * 0.117))
    d = max(4, int(r * 0.43))
    y_title = int(H * 0.583)
    y_sub = int(H * 0.687)

    img = image.Image(W, H, image.Format.FMT_RGB888)
    img.draw_rect(0, 0, W, H, image.Color.from_rgb(15, 5, 5), thickness=-1)
    img.draw_circle(cx, cy, r, image.Color.from_rgb(60, 10, 10), thickness=-1)
    img.draw_circle(cx, cy, r, image.Color.from_rgb(220, 60, 60), thickness=3)
    img.draw_line(cx - d, cy - d, cx + d, cy + d, image.Color.from_rgb(220, 60, 60), thickness=3)
    img.draw_line(cx + d, cy - d, cx - d, cy + d, image.Color.from_rgb(220, 60, 60), thickness=3)
    tw, _ = image.string_size(message)
    img.draw_string((W - tw) // 2, y_title,
                    message, image.Color.from_rgb(220, 60, 60))
    tw2, _ = image.string_size("Please try again")
    img.draw_string((W - tw2) // 2, y_sub,
                    "Please try again", image.Color.from_rgb(120, 120, 150))
    disp.show(img)
    await asyncio.sleep(duration)


# ---------------------------------------------------------------------------
# Animation helpers
# ---------------------------------------------------------------------------
def _clamp(x, lo=0, hi=255):
    return max(lo, min(hi, int(x)))


def _mix(c1, c2, t):
    """Linear blend between two RGB tuples."""
    t = max(0.0, min(1.0, t))
    return (_clamp(c1[0] + (c2[0] - c1[0]) * t),
            _clamp(c1[1] + (c2[1] - c1[1]) * t),
            _clamp(c1[2] + (c2[2] - c1[2]) * t))


def _rgb(c):
    return image.Color.from_rgb(c[0], c[1], c[2])


def _smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _draw_centered_text(img, text, y, color, W):
    tw, _ = image.string_size(text)
    img.draw_string((W - tw) // 2, y, text, _rgb(color))


def _draw_comet(img, cx, cy, orbit, angle, head_r, head_color, bg,
                tail_len=12, step=0.16):
    """Rotating comet with a fading tail."""
    for i in range(tail_len):
        t = 1.0 - i / tail_len  # head=1.0, tail→0
        a = angle - i * step
        dx = int(orbit * math.cos(a))
        dy = int(orbit * math.sin(a))
        r = max(2, int(head_r * (0.45 + 0.55 * t)))
        col = _mix(bg, head_color, t ** 1.4)
        img.draw_circle(cx + dx, cy + dy, r, _rgb(col), thickness=-1)


async def animate_speak_now(disp):
    """Sonar-like ripples expanding from a pulsing core."""
    W, H = config.DISP_W, config.DISP_H
    cx, cy = W // 2, int(H * 0.375)
    core_r = max(6, int(min(W, H) * 0.06))
    max_r = max(core_r * 4, int(min(W, H) * 0.22))
    y_title = int(H * 0.583)
    y_sub = int(H * 0.687)

    BG = (8, 10, 26)
    ACCENT = (255, 90, 110)
    ACCENT_DIM = (90, 30, 50)
    CORE = (255, 200, 200)
    TITLE = (240, 240, 240)
    SUB = (120, 120, 150)

    NUM_RIPPLES = 3
    PERIOD = 50  # frames per ripple lifecycle
    frame = 0
    while True:
        img = image.Image(W, H, image.Format.FMT_RGB888)
        img.draw_rect(0, 0, W, H, _rgb(BG), thickness=-1)

        # Expanding sonar rings, staggered in phase, fading as they grow
        for i in range(NUM_RIPPLES):
            phase = ((frame / PERIOD) + i / NUM_RIPPLES) % 1.0
            eased = _smoothstep(phase)
            r = int(core_r + (max_r - core_r) * eased)
            alpha = (1.0 - phase) ** 1.4
            ring_color = _mix(BG, ACCENT, alpha * 0.85)
            img.draw_circle(cx, cy, r, _rgb(ring_color), thickness=2)

        # Pulsing core
        breath = (math.sin(frame * 0.18) + 1) * 0.5  # 0..1
        rr = int(core_r + 3 * breath)
        img.draw_circle(cx, cy, rr + 4, _rgb(_mix(BG, ACCENT_DIM, 0.9)), thickness=-1)
        img.draw_circle(cx, cy, rr, _rgb(_mix(ACCENT, CORE, breath)), thickness=-1)

        _draw_centered_text(img, "Listening...", y_title, TITLE, W)
        _draw_centered_text(img, "Please speak now", y_sub, SUB, W)

        disp.show(img)
        frame += 1
        await asyncio.sleep(0.02)


async def animate_transcribing(disp):
    """Single rotating comet on a faint guide ring (green)."""
    W, H = config.DISP_W, config.DISP_H
    cx, cy = W // 2, int(H * 0.375)
    orbit = max(12, int(min(W, H) * 0.13))
    head_r = max(4, int(orbit * 0.32))
    y_title = int(H * 0.583)
    y_sub = int(H * 0.687)

    BG = (8, 18, 14)
    RING = (24, 64, 38)
    HEAD = (110, 255, 170)
    TITLE = (90, 230, 140)
    SUB = (110, 130, 120)

    frame = 0
    while True:
        angle = frame * 0.18
        img = image.Image(W, H, image.Format.FMT_RGB888)
        img.draw_rect(0, 0, W, H, _rgb(BG), thickness=-1)
        img.draw_circle(cx, cy, orbit, _rgb(RING), thickness=2)
        _draw_comet(img, cx, cy, orbit, angle, head_r, HEAD, BG,
                    tail_len=14, step=0.16)

        _draw_centered_text(img, "Transcribing...", y_title, TITLE, W)
        _draw_centered_text(img, "Recognizing speech", y_sub, SUB, W)

        disp.show(img)
        frame += 1
        await asyncio.sleep(0.02)


async def animate_thinking(disp, tool_names: list | None = None):
    """Two counter-rotating comets on concentric rings (blue/purple)."""
    W, H = config.DISP_W, config.DISP_H
    cx, cy = W // 2, int(H * 0.375)
    orbit_o = max(14, int(min(W, H) * 0.15))
    orbit_i = max(8, int(orbit_o * 0.62))
    head_o = max(4, int(orbit_o * 0.28))
    head_i = max(3, int(orbit_i * 0.40))
    y_title = int(H * 0.583)
    y_sub = int(H * 0.687)

    BG = (10, 12, 30)
    RING_O = (40, 50, 100)
    RING_I = (60, 40, 110)
    HEAD_O = (110, 180, 255)
    HEAD_I = (190, 140, 255)
    TITLE = (130, 180, 255)
    SUB = (120, 120, 150)
    TOOL = (180, 160, 255)

    frame = 0
    while True:
        angle_o = frame * 0.14
        angle_i = -frame * 0.22 + math.pi / 3
        img = image.Image(W, H, image.Format.FMT_RGB888)
        img.draw_rect(0, 0, W, H, _rgb(BG), thickness=-1)
        img.draw_circle(cx, cy, orbit_o, _rgb(RING_O), thickness=2)
        img.draw_circle(cx, cy, orbit_i, _rgb(RING_I), thickness=2)
        _draw_comet(img, cx, cy, orbit_o, angle_o, head_o, HEAD_O, BG,
                    tail_len=14, step=0.13)
        _draw_comet(img, cx, cy, orbit_i, angle_i, head_i, HEAD_I, BG,
                    tail_len=10, step=0.18)

        _draw_centered_text(img, "Thinking...", y_title, TITLE, W)
        if tool_names:
            _draw_centered_text(img, f"> {tool_names[-1]}", y_sub, TOOL, W)
        else:
            _draw_centered_text(img, "Please wait a moment", y_sub, SUB, W)

        disp.show(img)
        frame += 1
        await asyncio.sleep(0.02)


def _strip_emoji(text: str) -> str:
    return "".join(c for c in text if ord(c) <= 0xFFFF and not (0x2600 <= ord(c) <= 0x27BF))


def _wrap(text: str, max_lines: int = 0, max_w: int | None = None) -> list:
    max_w = config.MAX_TEXT_W if max_w is None else max_w
    lines = []
    for para in text.split("\n"):
        if not para:
            continue  # Skip empty lines
        while para and (max_lines == 0 or len(lines) < max_lines):
            lo, hi = 1, len(para)
            while lo < hi:
                mid = (lo + hi + 1) // 2
                w, _ = image.string_size(para[:mid])
                if w <= max_w:
                    lo = mid
                else:
                    hi = mid - 1
            lines.append(para[:lo])
            para = para[lo:]
        if max_lines != 0 and len(lines) >= max_lines:
            break
    return lines, bool(text)


def _draw_line_h(img, x: int, y: int, text: str, color) -> int:
    img.draw_string(x, y, text, color)
    _, h = image.string_size(text)
    return max(h + 6, config.LINE_H)


def _render_frame(question: str, window: list, tool_names: list | None = None) -> image.Image:
    img = image.Image(config.DISP_W, config.DISP_H, image.Format.FMT_RGB888)
    img.draw_rect(0, 0, config.DISP_W, config.DISP_H, image.Color.from_rgb(8, 8, 24), thickness=-1)

    bx, by, bw, bh = get_exit_btn_rect()
    content_x = max(TEXT_MARGIN, bx + bw + max(6, int(config.DISP_W * 0.02)))
    content_max_w = max(1, config.DISP_W - TEXT_MARGIN - content_x)

    y = 6
    y += _draw_line_h(img, content_x, y, "You:", image.Color.from_rgb(120, 180, 255))

    q_lines, _ = _wrap(question, 2, content_max_w)
    for line in q_lines:
        y += _draw_line_h(img, content_x, y, line, image.Color.from_rgb(200, 200, 200))

    y += 3
    img.draw_line(content_x, y, config.DISP_W - TEXT_MARGIN, y, image.Color.from_rgb(50, 50, 80), thickness=1)
    y += 8

    y += _draw_line_h(img, content_x, y, "PicoClaw:", image.Color.from_rgb(80, 200, 100))

    for line in window:
        if y + config.LINE_H > config.DISP_H:
            break
        y += _draw_line_h(img, content_x, y, line, image.Color.from_rgb(220, 220, 190))

    _draw_exit_button(img)

    return img


def render_streaming_frame(disp, question: str, answer: str, tool_names: list | None = None):
    ans = _strip_emoji(answer) if answer else ""
    bx, by, bw, bh = get_exit_btn_rect()
    content_x = max(TEXT_MARGIN, bx + bw + max(6, int(config.DISP_W * 0.02)))
    content_max_w = max(1, config.DISP_W - TEXT_MARGIN - content_x)
    q_lines, _ = _wrap(question, 2, content_max_w)
    y_est = 6 + config.LINE_H + len(q_lines) * config.LINE_H + 3 + 1 + 8 + config.LINE_H
    max_visible = max(1, (config.DISP_H - y_est - 4) // config.LINE_H)
    all_lines, _ = _wrap(ans, max_w=content_max_w) if ans else ([], False)
    window = all_lines[-max_visible:] if all_lines else []
    disp.show(_render_frame(question, window, tool_names))


class StreamingRenderer:
    def __init__(self, disp, question: str, line_delay: float = 0.8):
        self.disp = disp
        self.question = question
        self.line_delay = line_delay
        self._revealed = 0  # number of answer lines already shown
        self._last_lines: list[str] = []
        self._last_tools: list[str] | None = None
        bx, by, bw, bh = get_exit_btn_rect()
        self._content_x = max(TEXT_MARGIN, bx + bw + max(6, int(config.DISP_W * 0.02)))
        self._content_max_w = max(1, config.DISP_W - TEXT_MARGIN - self._content_x)
        q_lines, _ = _wrap(question, 2, self._content_max_w)
        y_est = 6 + config.LINE_H + len(q_lines) * config.LINE_H + 3 + 1 + 8 + config.LINE_H
        self._max_visible = max(1, (config.DISP_H - y_est - 4) // config.LINE_H)

    def _window(self, count: int) -> list[str]:
        end = min(count, len(self._last_lines))
        start = max(0, end - self._max_visible)
        return self._last_lines[start:end]

    def _draw(self, count: int, tool_names: list | None):
        frame = _render_frame(self.question, self._window(count), tool_names)
        self.disp.show(frame)

    async def update(self, answer: str, tool_names: list | None = None):
        ans = _strip_emoji(answer) if answer else ""
        all_lines, _ = _wrap(ans, max_w=self._content_max_w) if ans else ([], False)
        self._last_lines = all_lines
        self._last_tools = tool_names

        total = len(all_lines)
        if total == 0:
            self._revealed = 0
            self._draw(0, tool_names)
            return

        complete = total - 1

        while self._revealed < complete:
            self._revealed += 1
            self._draw(self._revealed + 1, tool_names)
            await asyncio.sleep(self.line_delay)

        self._draw(self._revealed + 1, tool_names)

    async def finalize(self, tool_names: list | None = None):
        if self._last_lines:
            self._revealed = len(self._last_lines)
        self._draw(self._revealed, tool_names if tool_names is not None else self._last_tools)
