#!/usr/bin/env python3
"""One-time script: downloads all third-party assets into vendor/.

Licenses:
  Leaflet 1.9.4       — BSD 2-Clause
  Font Awesome 6.5.1  — MIT (CSS), SIL OFL 1.1 (fonts), CC BY 4.0 (icons)
  Google Fonts        — SIL OFL 1.1 (Fraunces, Caveat, Lora)
"""

import re
import time
import urllib.request
from pathlib import Path

VENDOR = Path("vendor")


def fetch(url: str, headers: dict | None = None) -> bytes:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()


def save(path: Path, data: bytes | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        path.write_text(data, encoding="utf-8")
    else:
        path.write_bytes(data)
    print(f"  {path}")


# ── Leaflet 1.9.4 (BSD-2-Clause) ──────────────────────────────────────────────
LEAFLET = "1.9.4"
LEAFLET_BASE = f"https://unpkg.com/leaflet@{LEAFLET}/dist"
print("Leaflet...")
save(VENDOR / "leaflet/leaflet.css", fetch(f"{LEAFLET_BASE}/leaflet.css"))
save(VENDOR / "leaflet/leaflet.js",  fetch(f"{LEAFLET_BASE}/leaflet.js"))
for img in ["layers.png", "layers-2x.png", "marker-icon.png",
            "marker-icon-2x.png", "marker-shadow.png"]:
    save(VENDOR / f"leaflet/images/{img}", fetch(f"{LEAFLET_BASE}/images/{img}"))

# ── Font Awesome 6.5.1 Free (MIT/SIL OFL/CC BY 4.0) ──────────────────────────
FA = "6.5.1"
FA_BASE = f"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/{FA}"
print("Font Awesome...")
css = fetch(f"{FA_BASE}/css/all.min.css").decode()
css = css.replace("../webfonts/", "webfonts/")
save(VENDOR / "fontawesome/all.min.css", css)
# We only use fa-solid-* icons, so only this webfont is needed.
save(VENDOR / "fontawesome/webfonts/fa-solid-900.woff2",
     fetch(f"{FA_BASE}/webfonts/fa-solid-900.woff2"))

# ── Google Fonts: Fraunces, Caveat, Lora (SIL OFL 1.1) ───────────────────────
print("Google Fonts...")
GFONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Fraunces:ital,opsz,wght@"
    "0,9..144,400;0,9..144,700;0,9..144,900;"
    "1,9..144,400;1,9..144,700;1,9..144,900"
    "&family=Caveat:wght@500;700"
    "&family=Lora:ital,wght@0,400;1,400"
    "&display=swap"
)
MODERN_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
css = fetch(GFONTS_URL, headers={"User-Agent": MODERN_UA}).decode()
for url in re.findall(r"url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)", css):
    fname = url.split("/")[-1]
    css = css.replace(url, fname)
    save(VENDOR / f"fonts/{fname}", fetch(url))
    time.sleep(0.05)
save(VENDOR / "fonts/fonts.css", css)

print("\nDone. Commit vendor/ to git.")
