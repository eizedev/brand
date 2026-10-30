# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools>=4.50", "pillow>=10"]
# ///
"""Icon, header and social preview of aiosnmpswitch.

The icon shows a switch front panel with four ports; three of them are linked to devices above
(blue, green, yellow, the colours of the SRM marks), the fourth port is empty. From 32 px down the
devices are dropped and the panel fills the icon, because the thin links blur.

Run: uv run aiosnmpswitch/build.py   (writes to aiosnmpswitch/out/)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from PIL import Image  # noqa: E402

from brand import DARK, LIGHT, Palette, text, write_png, write_svg  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
NAME = "aiosnmpswitch"
TAGLINE = ("Async, read-only Python client", "for managed network switches (SNMP)")


def switch(c: Palette, small: bool = False) -> str:
    """Switch front panel with linked devices, in a 400x400 box."""
    left, width, body_y, body_h = (24, 352, 120, 160) if small else (52, 296, 238, 104)
    body = (
        f'<rect x="{left}" y="{body_y}" width="{width}" height="{body_h}" rx="22" fill="none" '
        f'stroke="{c.line}" stroke-width="{24 if small else 14}"/>'
    )
    colours = (c.blue, c.green, c.yellow, None)
    ports = ""
    links = ""
    devices = ""
    size, step = (70, 82) if small else (44, 64)
    for i, colour in enumerate(colours):
        cx = 200 + (i - 1.5) * step
        top = body_y + (body_h - size) / 2
        if colour is None:
            ports += (
                f'<rect x="{cx - size / 2}" y="{top}" width="{size}" height="{size}" rx="8" '
                f'fill="none" stroke="{c.line}" stroke-width="{12 if small else 8}"/>'
            )
            continue
        ports += f'<rect x="{cx - size / 2}" y="{top}" width="{size}" height="{size}" rx="8" fill="{colour}"/>'
        if small:
            continue
        dx = (200 - cx) * -0.35
        dev = (cx + dx, 104 if i == 1 else 128)
        links += (
            f'<path d="M{cx} {top} L{dev[0]:.0f} {dev[1]}" stroke="{c.line}" stroke-width="10" '
            'stroke-linecap="round" fill="none"/>'
        )
        devices += f'<circle cx="{dev[0]:.0f}" cy="{dev[1]}" r="26" fill="{colour}"/>'
    return links + body + ports + devices


def icon(c: Palette, small: bool = False) -> str:
    """Rounded square app icon (400x400)."""
    return (
        f'<rect width="400" height="400" rx="88" fill="{c.bg}"/>'
        f'<g transform="translate(200 200) scale(0.92) translate(-200 -200)">{switch(c, small)}</g>'
    )


def header(c: Palette, size: int = 72) -> tuple[str, int, int]:
    """Icon mark plus name for the README header (transparent background)."""
    height = int(size * 1.8)
    mark_size = size * 1.75
    mark = (
        f'<g transform="translate(0 {(height - mark_size) / 2:.1f}) scale({mark_size / 400:.4f})">'
        f"{switch(c)}</g>"
    )
    name, width = text(NAME, size * 1.75, height / 2 + size * 0.36, size, c.text)
    return mark + name, int(size * 1.75 + width + 12), height


def social(c: Palette) -> str:
    """GitHub social preview, 1280x640."""
    body = f'<rect width="1280" height="640" fill="{c.bg}"/>'
    body += f'<g transform="translate(130 150) scale(0.85)">{switch(c)}</g>'
    body += text(NAME, 480, 330, 74, c.text)[0]
    body += text(TAGLINE[0], 484, 400, 30, c.sub)[0]
    body += text(TAGLINE[1], 484, 444, 30, c.sub)[0]
    return body


def main() -> None:
    """Write every file and a review sheet."""
    full = write_svg(OUT / "icon.svg", 400, 400, icon(DARK))
    small = write_svg(OUT / "icon-small.svg", 400, 400, icon(DARK, small=True))
    for px in (1024, 512, 256, 128, 64):
        write_png(full, OUT / f"icon-{px}.png", px)
    for px in (32, 16):
        write_png(small, OUT / f"icon-{px}.png", px)
    for variant, palette in (("dark", DARK), ("light", LIGHT)):
        body, w, h = header(palette)
        svg = write_svg(OUT / f"header-{variant}.svg", w, h, body)
        write_png(svg, OUT / f"header-{variant}@2x.png", w * 2, h * 2)
    preview = write_svg(OUT / "social-preview.svg", 1280, 640, social(DARK))
    write_png(preview, OUT / "social-preview.png", 1280, 640)

    sheet = Image.new("RGB", (1360, 1060), "#d9dce3")
    big = Image.open(OUT / "icon-512.png").resize((380, 380))
    sheet.paste(big, (40, 40), big)
    x = 460
    for px in (128, 64, 32, 16):
        img = Image.open(OUT / f"icon-{px}.png")
        sheet.paste(img, (x, 40 + (128 - px) // 2), img)
        x += px + 40
    for i, variant in enumerate(("dark", "light")):
        img = Image.open(OUT / f"header-{variant}@2x.png")
        img.thumbnail((620, 200))
        tile = Image.new("RGB", (640, 170), DARK.bg if variant == "dark" else "#ffffff")
        tile.paste(img, (10, (170 - img.height) // 2), img)
        sheet.paste(tile, (40 + i * 680, 450))
    preview_img = Image.open(OUT / "social-preview.png")
    preview_img.thumbnail((640, 320))
    sheet.paste(preview_img, (40, 680))
    sheet.save(HERE / "overview.png")
    print(f"written to {OUT}")


if __name__ == "__main__":
    main()
