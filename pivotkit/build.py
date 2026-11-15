# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools>=4.50", "pillow>=10", "uharfbuzz>=0.39"]
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

from brand import DARK, LIGHT, Palette, sans_text, text, write_png, write_svg  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
NAME = "pivotkit"
# The social preview reads as a flow: data in, a pivot view, a report out. Every word on it is in
# the pivotkit README or documentation: "Excel's PivotTable" is the README's first line; the ways to
# use it are its package table; the sources are docs/reference/sources.md; the report formats are
# docs/reference/report.md and the links docs/reference/delivery.md.
VALUE = "Excel's PivotTable, for the web"
SOURCES = ("File", "HTTP", "Code")
WAYS = ("Browser · CLI", "REST · MCP")
REPORTS = ("Excel", "HTML", "CSV", "Link")


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


def placed(
    s: str,
    x: float,
    baseline: float,
    size: float,
    fill: str,
    weight: str = "medium",
    align: str = "left",
) -> tuple[str, float]:
    """Inter text aligned left, centre or right on ``x``; returns the SVG and its width."""
    _, width = sans_text(s, 0, 0, size, fill, weight)
    shift = {"left": 0, "centre": width / 2, "right": width}[align]
    return sans_text(s, x - shift, baseline, size, fill, weight)[0], width


def chip_width(label: str, size: float) -> float:
    """Outer width of a chip with ``label``."""
    return sans_text(label, 0, 0, size, "none")[1] + 1.6 * size


def chip(label: str, x: float, y: float, colour: str, c: Palette, size: float) -> str:
    """A rounded label with a coloured outline, top left at (x, y), 1.9 x ``size`` high."""
    height = size * 1.9
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{chip_width(label, size):.1f}" '
        f'height="{height:.1f}" rx="{height / 2:.1f}" fill="none" stroke="{colour}" '
        f'stroke-width="5"/>'
    ) + sans_text(label, x + 0.8 * size, y + height / 2 + size * 0.36, size, c.text)[0]


def column(labels: tuple[str, ...], x: float, centre: float, colour: str, c: Palette) -> str:
    """Chips stacked around the vertical ``centre``."""
    size, gap = 40, 14
    height = size * 1.9
    top = centre - (len(labels) * height + (len(labels) - 1) * gap) / 2
    return "".join(
        chip(label, x, top + i * (height + gap), colour, c, size) for i, label in enumerate(labels)
    )


def arrow(x1: float, x2: float, y: float, colour: str) -> str:
    """A horizontal arrow from x1 to x2."""
    head = 22
    return (
        f'<path d="M{x1:.1f} {y} H{x2 - head:.1f}" stroke="{colour}" stroke-width="9" '
        f'stroke-linecap="round"/>'
        f'<path d="M{x2:.1f} {y} L{x2 - head - 6:.1f} {y - head} L{x2 - head - 6:.1f} {y + head} Z" '
        f'fill="{colour}"/>'
    )


def social(c: Palette) -> str:
    """GitHub social preview, 1280x640: data in, a pivot view, a report out.

    It is also the link card in chat and social apps, shown 400 to 600 px wide and sometimes cropped
    to 1.91:1, so the text is large and everything keeps 56 px or more from every edge. The
    lettering is Inter, the closest bundled match to the system sans-serif the documentation site
    (pivotkit.eize.dev) shows, with its heading weight and tracking (800, -0.03em).
    """
    margin, right = 80, 1200
    body = f'<rect width="1280" height="640" fill="{c.bg}"/>'
    body += f'<g transform="translate({margin} 56) scale(0.3)">{table(c)}</g>'
    body += sans_text(NAME, 224, 150, 84, c.text, "extrabold", tracking=-0.03)[0]
    body += placed(VALUE, right, 144, 42, c.sub, align="right")[0]
    # Sources on the left edge, reports on the right edge, the view centred, arrows in the gaps.
    centre, gap, size = 404, 26, 40
    sources_end = margin + max(chip_width(s, size) for s in SOURCES)
    reports_x = right - max(chip_width(s, size) for s in REPORTS)
    box_left, box_right = 640 - 220, 640 + 220
    body += column(SOURCES, margin, centre, c.green, c)
    body += arrow(sources_end + gap, box_left - gap, centre, c.sub)
    body += (
        f'<rect x="{box_left}" y="{centre - 125}" width="{box_right - box_left}" height="250" '
        f'rx="28" fill="none" stroke="{c.blue}" stroke-width="5"/>'
    )
    body += placed("Pivot view", 640, centre - 40, 54, c.text, "extrabold", "centre")[0]
    for i, line in enumerate(WAYS):
        body += placed(line, 640, centre + 30 + i * 52, 40, c.sub, align="centre")[0]
    body += arrow(box_right + gap, reports_x - gap, centre, c.sub)
    body += column(REPORTS, reports_x, centre, c.yellow, c)
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
