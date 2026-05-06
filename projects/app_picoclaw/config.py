import logging
import os

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL = os.environ.get("LOG_LEVEL", "ERROR").upper()


def setup_logging() -> None:
    level = getattr(logging, LOG_LEVEL, logging.DEBUG)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
        force=True,  # override any handlers installed by maix at import time
    )
    logging.getLogger().setLevel(level)


# ---------------------------------------------------------------------------
# Default config
# ---------------------------------------------------------------------------
DISP_W = 0   # set at runtime via init_display()
DISP_H = 0   # set at runtime via init_display()
ICON_PATH = "img/logo.png"

# Baseline display width used when picking the default font sizes below.
# UI elements scale relative to this in init_display().
BASE_DISP_W = 240
# Extra multiplier on top of resolution-based scaling. Lower this to shrink fonts.
FONT_SCALE = 0.75


def init_display(disp) -> None:
    """Populate display-dependent module globals from a maix display.Display."""
    global DISP_W, DISP_H, MAX_TEXT_W
    global FONT_SIZE, FONT_SIZE_LARGE, LINE_H
    DISP_W = disp.width()
    DISP_H = disp.height()
    MAX_TEXT_W = DISP_W - TEXT_MARGIN * 2

    scale = max(1.0, DISP_W / BASE_DISP_W) * FONT_SCALE
    FONT_SIZE = int(round(FONT_SIZE * scale))
    FONT_SIZE_LARGE = int(round(FONT_SIZE_LARGE * scale))
    LINE_H = int(round(LINE_H * scale))

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
FONT_PATH = "/maixapp/share/font/SourceHanSansCN-Regular.otf"
FONT_NAME = "sourcehansans"
FONT_SIZE = 17               # scaled at runtime by init_display()
FONT_NAME_LARGE = "sourcehansans20"
FONT_SIZE_LARGE = 20         # scaled at runtime by init_display()

# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------
SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
RECORDER_VOLUME = 100

# ---------------------------------------------------------------------------
# Picoclaw release
# ---------------------------------------------------------------------------
PICOCLAW_VERSION = "v0.2.8"

# ---------------------------------------------------------------------------
# UI layout
# ---------------------------------------------------------------------------
LINE_H = 24        # Line height
TEXT_MARGIN = 8     # Left/right text margin
MAX_TEXT_W = 0     # set at runtime via init_display()
