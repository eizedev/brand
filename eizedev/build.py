# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools>=4.50", "pillow>=10"]
# ///
"""The personal ❯e_ logo: a shell prompt, the "e" of eizedev and a cursor.

Writes every variant (avatar, icons, marks, wordmarks, social preview, favicons) to eizedev/svg,
eizedev/png and eizedev/favicon, plus the contact sheet eizedev/overview.png.

Run: uv run eizedev/build.py
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from PIL import Image, ImageDraw  # noqa: E402

from brand import DARK, LIGHT, Palette, glyph, text, text_width, write_png, write_svg  # noqa: E402

HERE = Path(__file__).resolve().parent
SVG, PNG, FAV = HERE / "svg", HERE / "png", HERE / "favicon"
TAGLINE = "Automation, self-hosting & PowerShell"


def mark(c: Palette | None, mono: str | None = None, scale: float = 1.0) -> str:
    """The ❯e_ mark in a 400x400 box, optically centred."""
    chev, e, cur = (mono,) * 3 if mono else (c.green, c.blue, c.yellow)  # type: ignore[union-attr]
    epath = glyph("e", 150, 262, 190)
    # chevron stroke width 26 gives a visual extent of 65..136; the cursor spans 272..320
    dx, dy = 200 - (65 + 320) / 2, 200 - (137 + 263) / 2
    return (
        f'<g transform="translate(200 200) scale({scale}) translate(-200 -200) translate({dx:.1f} {dy:.1f})">'
        f'<path d="M78 150 L123 200 L78 250" fill="none" stroke="{chev}" stroke-width="26" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="{epath}" fill="{e}"/>'
        f'<rect x="272" y="232" width="48" height="24" rx="4" fill="{cur}"/></g>'
    )


def wordmark_body(c: Palette, size: float, ox: float, base: float) -> tuple[str, float]:
    """❯ eizedev_ with the chevron and cursor scaled to the text size."""
    k = size / 190
    chev = (
        f'<path d="M{ox} {base - size * 0.58:.1f} L{ox + 45 * k:.1f} {base - size * 0.32:.1f} '
        f'L{ox} {base - size * 0.06:.1f}" fill="none" stroke="{c.green}" stroke-width="{26 * k:.1f}" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
    )
    txt, width = text("eizedev", ox + 80 * k, base, size, c.blue)
    cx = ox + 80 * k + width + 8 * k
    cursor = (
        f'<rect x="{cx:.1f}" y="{base - 30 * k:.1f}" width="{48 * k:.1f}" height="{24 * k:.1f}" '
        f'rx="{4 * k:.1f}" fill="{c.yellow}"/>'
    )
    return chev + txt + cursor, cx + 48 * k - ox


def build() -> dict[str, Path]:
    """Write every SVG, PNG and favicon; return the SVG paths by name."""
    square = {
        "avatar": f'<rect width="400" height="400" fill="{DARK.bg}"/>' + mark(DARK, scale=0.86),
        "icon-rounded": f'<rect width="400" height="400" rx="88" fill="{DARK.bg}"/>' + mark(DARK, scale=0.86),
        "icon-light": f'<rect width="400" height="400" rx="88" fill="{LIGHT.bg}"/>' + mark(LIGHT, scale=0.86),
        "mark-on-dark": mark(DARK),
        "mark-on-light": mark(LIGHT),
        "mark-mono-dark": mark(None, mono=DARK.bg),
        "mark-mono-white": mark(None, mono="#ffffff"),
    }
    paths = {name: write_svg(SVG / f"{name}.svg", 400, 400, body) for name, body in square.items()}

    for variant, c in (("dark", DARK), ("light", LIGHT)):
        size = 120
        body, width = wordmark_body(c, size, 20, int(size * 1.08))
        w, h = int(width + 40), int(size * 1.5)
        svg = write_svg(SVG / f"wordmark-on-{variant}.svg", w, h, body)
        write_png(svg, PNG / f"wordmark-on-{variant}@2x.png", w * 2, h * 2)

    _, width = wordmark_body(DARK, 150, 0, 0)
    wordmark, _ = wordmark_body(DARK, 150, (1280 - width) / 2, 330)
    tagline, _ = text(TAGLINE, (1280 - text_width(TAGLINE, 34)) / 2, 420, 34, DARK.sub)
    paths["social-preview"] = write_svg(
        SVG / "social-preview.svg", 1280, 640, f'<rect width="1280" height="640" fill="{DARK.bg}"/>' + wordmark + tagline
    )

    for px in (500, 1000):
        write_png(paths["avatar"], PNG / f"avatar-{px}.png", px)
    for px in (512, 1024):
        write_png(paths["icon-rounded"], PNG / f"icon-rounded-{px}.png", px)
    for px in (256, 512, 1024):
        write_png(paths["mark-on-dark"], PNG / f"mark-on-dark-{px}.png", px)
        write_png(paths["mark-on-light"], PNG / f"mark-on-light-{px}.png", px)
    write_png(paths["social-preview"], PNG / "social-preview-1280x640.png", 1280, 640)

    FAV.mkdir(parents=True, exist_ok=True)
    shutil.copy(paths["icon-rounded"], FAV / "favicon.svg")
    write_png(paths["avatar"], FAV / "apple-touch-icon.png", 180)  # iOS rounds the corners itself
    for px in (192, 512):
        write_png(paths["icon-rounded"], FAV / f"icon-{px}.png", px)
    with tempfile.TemporaryDirectory() as tmp:
        ico = write_png(paths["icon-rounded"], Path(tmp) / "ico.png", 256)
        Image.open(ico).save(FAV / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    manifest = {
        "name": "eizedev",
        "short_name": "eizedev",
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
        "theme_color": DARK.bg,
        "background_color": DARK.bg,
        "display": "standalone",
    }
    (FAV / "site.webmanifest").write_text(json.dumps(manifest, indent=2) + "\n")
    return paths


def overview(paths: dict[str, Path]) -> None:
    """Contact sheet of every variant, including round crops on light and dark."""
    sheet = Image.new("RGB", (1600, 1500), "#f3f4f6")
    draw = ImageDraw.Draw(sheet)
    draw.rectangle([800, 0, 1600, 560], fill="#0d1117")

    def put(path: Path, x: int, y: int, w: int, h: int | None = None, circle: bool = False) -> None:
        img = Image.open(path).convert("RGBA").resize((w, h or w), Image.LANCZOS)
        if circle:
            mask = Image.new("L", img.size, 0)
            ImageDraw.Draw(mask).ellipse([0, 0, img.size[0] - 1, img.size[1] - 1], fill=255)
            img.putalpha(mask)
        sheet.paste(img, (x, y), img)

    def label(s: str, x: int, y: int, colour: str = "#333") -> None:
        draw.text((x, y), s, fill=colour)

    for x0, colour, caption in ((30, "#333", "avatar (GitHub crop) 240/96/40/20"), (830, "#ccc", "same on GitHub dark")):
        x = x0
        for s in (240, 96, 40, 20):
            put(PNG / "avatar-1000.png", x, 60 + (240 - s) // 2, s, circle=True)
            x += s + 30
        label(caption, x0, 320, colour)

    with tempfile.TemporaryDirectory() as tmp:
        put(PNG / "icon-rounded-512.png", 30, 360, 170)
        label("icon-rounded", 30, 535)
        put(write_png(paths["icon-light"], Path(tmp) / "il.png", 170), 230, 360, 170)
        label("icon-light", 230, 535)
        put(PNG / "mark-on-light-512.png", 430, 360, 170)
        label("mark-on-light", 430, 535)
        put(write_png(paths["mark-mono-dark"], Path(tmp) / "md.png", 170), 610, 360, 170)
        label("mono-dark", 610, 535)
        put(PNG / "mark-on-dark-512.png", 830, 360, 170)
        label("mark-on-dark", 830, 535, "#ccc")
        put(write_png(paths["mark-mono-white"], Path(tmp) / "mw.png", 170), 1030, 360, 170)
        label("mono-white", 1030, 535, "#ccc")
    for x, y, s in ((1240, 400, 64), (1320, 420, 32), (1370, 428, 16)):
        put(FAV / "icon-192.png", x, y, s)
    label("favicon 64/32/16", 1240, 535, "#ccc")

    draw.rectangle([0, 570, 1600, 700], fill=DARK.bg)
    dark = Image.open(PNG / "wordmark-on-dark@2x.png")
    ratio = 110 / dark.size[1]
    put(PNG / "wordmark-on-dark@2x.png", 30, 580, int(dark.size[0] * ratio), 110)
    light = Image.open(PNG / "wordmark-on-light@2x.png")
    put(PNG / "wordmark-on-light@2x.png", 30, 720, int(light.size[0] * ratio), 110)
    label("wordmark on dark / on light", 700, 620, "#ccc")
    put(PNG / "social-preview-1280x640.png", 30, 860, 1100, 550)
    label("social-preview 1280x640", 1150, 860)
    sheet.save(HERE / "overview.png")


if __name__ == "__main__":
    overview(build())
    print(f"written to {HERE}")
