#!/usr/bin/env bash
# Force-regenerate binding/lvgl_python.c from MaixCDK's LVGL source.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/regenerate_binding.py --force
