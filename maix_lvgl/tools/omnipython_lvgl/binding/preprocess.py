# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Deterministic C preprocessing used by the binding generator."""

from __future__ import print_function

import os
import shlex
import subprocess


def _preprocessor_command(args):
    compiler = shlex.split(os.environ.get("CPP", "gcc"))
    if "-E" not in compiler:
        compiler.append("-E")
    if "-P" not in compiler:
        compiler.append("-P")
    if not any(flag.startswith("-std=") for flag in compiler):
        compiler.append("-std=c99")
    compiler.append("-DPYCPARSER")
    for define in args.define or []:
        compiler.append("-D%s" % define)
    for include in args.include or []:
        compiler.extend(["-I", include])
    for input_file in args.input[1:]:
        compiler.extend(["-include", input_file])
    compiler.append(args.input[0])
    return compiler


def preprocess(args):
    """Return preprocessed source text and a description of how it was produced."""
    if not args.ep:
        command = _preprocessor_command(args)
        pp_cmd = " ".join(shlex.quote(part) for part in command)
        source = subprocess.check_output(command).decode("utf-8")
    else:
        pp_cmd = "Preprocessing was disabled."
        with open(args.ep, "r", encoding="utf-8") as f:
            source = f.read()
    return source, pp_cmd
