# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools>=4.50", "pillow>=10"]
# ///
"""Icon, header and social preview of pivotkit.

The icon is a pivot table: a 3x3 grid whose top row (column headers) is blue, whose left column
(row headers) is green and whose bottom-right cell (the grand total) is yellow. The empty corner
cell holds a curved double arrow from the column headers to the row headers - the pivot. From 32 px
down the arrow is dropped and the cells grow onto whole pixels, because the thin arc blurs.

Run: uv run pivotkit/build.py   (writes to pivotkit/out/)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from PIL import Image  # noqa: E402

from brand import DARK, LIGHT, Palette, text, write_png, write_svg  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
NAME = "pivotkit"
TAGLINE = ("Pivot report builder for the web", "React, web component, PowerShell Universal")


def table(c: Palette, small: bool = False) -> str:
    """Pivot table grid with a pivot arrow in the corner cell, in a 400x400 box."""
    # The small grid sits on whole pixels at 16 and 32 px: cells of 4 (8) px, gaps of 1 (2) px.
    start, cell, gap, radius = (25, 100, 25, 12) if small else (40, 96, 16, 14)
    step = cell + gap
    cells = ""
    for row in range(3):
        for col in range(3):
            if row == 0 and col == 0:
                continue
            if row == 0:
                fill = c.blue
            elif col == 0:
                fill = c.green
            elif row == 2 and col == 2:
                fill = c.yellow
            else:
                fill = c.line
            cells += (
                f'<rect x="{start + col * step}" y="{start + row * step}" width="{cell}" '
                f'height="{cell}" rx="{radius}" fill="{fill}"/>'
            )
    if small:
        return cells
    # Quarter arc around the corner cell's bottom-right corner, bulging to the top left, with
    # arrowheads at both ends: one points right at the column headers, the other down at the row
    # headers - rows and columns swap.
    centre, r, head = start + cell - 12, 60, 18
    top = (centre, centre - r)
    left = (centre - r, centre)
    arc = (
        f'<path d="M{top[0] - 8} {top[1]} A{r} {r} 0 0 0 {left[0]} {left[1] - 8}" fill="none" '
        f'stroke="{c.text}" stroke-width="16" stroke-linecap="round"/>'
    )
    heads = (
        f'<path d="M{top[0] + head} {top[1]} L{top[0] - 6} {top[1] - head} L{top[0] - 6} {top[1] + head} Z" '
        f'fill="{c.text}" stroke="{c.text}" stroke-width="6" stroke-linejoin="round"/>'
        f'<path d="M{left[0]} {left[1] + head} L{left[0] - head} {left[1] - 6} L{left[0] + head} {left[1] - 6} Z" '
        f'fill="{c.text}" stroke="{c.text}" stroke-width="6" stroke-linejoin="round"/>'
    )
    return cells + arc + heads


def icon(c: Palette, small: bool = False) -> str:
    """Rounded square app icon (400x400)."""
    return (
        f'<rect width="400" height="400" rx="88" fill="{c.bg}"/>'
        f'<g transform="translate(200 200) scale({1 if small else 0.8}) translate(-200 -200)">'
        f"{table(c, small)}</g>"
    )


def header(c: Palette, size: int = 72) -> tuple[str, int, int]:
    """Icon mark plus name for the README header (transparent background)."""
    height = int(size * 1.8)
    mark_size = size * 1.5
    mark = (
        f'<g transform="translate(0 {(height - mark_size) / 2:.1f}) scale({mark_size / 400:.4f})">'
        f"{table(c)}</g>"
    )
    name, width = text(NAME, size * 1.75, height / 2 + size * 0.36, size, c.text)
    return mark + name, int(size * 1.75 + width + 12), height


def social(c: Palette) -> str:
    """GitHub social preview, 1280x640."""
    body = f'<rect width="1280" height="640" fill="{c.bg}"/>'
    body += f'<g transform="translate(130 150) scale(0.85)">{table(c)}</g>'
    body += text(NAME, 480, 330, 56, c.text)[0]
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
