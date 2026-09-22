#!/usr/bin/env python3
"""Render every mockup in src/ to a 2x PNG with headless Chrome.

Usage: python3 mockups/render.py [name ...]
"""
import os
import re
import subprocess
import sys
import time
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

names = sys.argv[1:] or sorted(f[:-5] for f in os.listdir(SRC) if f.endswith(".html"))
for name in names:
    out = os.path.join(HERE, name + ".png")
    if os.path.exists(out):
        os.remove(out)
    html = open(os.path.join(SRC, name + ".html")).read()
    shot = re.search(r'<meta name="shot" content="(\d+)x(\d+)">', html)
    size_arg = "--window-size=%s,%s" % (shot.groups() if shot else ("1440", "900"))
    url = "file://" + urllib.parse.quote(os.path.join(SRC, name + ".html"))
    proc = subprocess.Popen(
        [CHROME, "--headless", "--hide-scrollbars", "--force-device-scale-factor=2",
         size_arg, "--screenshot=" + out, url],
        start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Headless Chrome exits by itself once the file is written and then removes
    # the code-signature clone it made in $TMPDIR/../X. Killing it early leaves
    # that 1 GB clone behind, so only fall back to terminate on a real hang.
    try:
        proc.wait(timeout=90)
    except subprocess.TimeoutExpired:
        proc.terminate()
        proc.wait()
    last = os.path.getsize(out) if os.path.exists(out) else -1
    print(name, last)
