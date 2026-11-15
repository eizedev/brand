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
TAGLINE = "Pivot reports for the web and the command line"
# What pivotkit ships, one line each in the social preview: the front ends, then the services.
FEATURES = (
    "React · Web component · CLI · Excel export",
    "REST API · MCP server · Container image",
)


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
    """GitHub social preview, 1280x640.

    The lettering is Inter, the closest bundled match to the system sans-serif the documentation
    site (pivotkit.eize.dev) shows, with its heading weight and tracking (800, -0.03em).
    """
    body = f'<rect width="1280" height="640" fill="{c.bg}"/>'
    body += f'<g transform="translate(96 190) scale(0.65)">{table(c)}</g>'
    # The text block (name cap height to the last feature line) is centred on the 260 px mark.
    left, line = 400, 50
    body += sans_text(NAME, left, 265, 96, c.text, "extrabold", tracking=-0.03)[0]
    body += sans_text(TAGLINE, left + 4, 337, 34, c.text)[0]
    for i, feature in enumerate(FEATURES):
        body += sans_text(feature, left + 4, 387 + i * line, 34, c.sub)[0]
    return body


# Candidates for a new social preview (social-preview-<id>); the owner picks one, which then
# replaces social(). Every claim on them is in the pivotkit README or documentation:
# - Excel's PivotTable: the README's first line;
# - Browser (React, web component), CLI, REST, MCP: the README's package table;
# - Excel, HTML, CSV and expiring links: docs/reference/report.md, docs/reference/delivery.md;
# - files, HTTP and code sources: docs/reference/sources.md;
# - the model writes the view, pivotkit reads the data: docs/reference/mcp.md, docs/model-data.md.
VALUE = "Excel's PivotTable, for the web"
FRONTS = ("Browser", "CLI", "REST", "MCP")
MODEL = "MCP: the model writes the view, pivotkit reads the data"


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


def chip(
    label: str, x: float, y: float, colour: str, c: Palette, size: int = 34
) -> tuple[str, float]:
    """A rounded label with a coloured outline, top left at (x, y); returns the SVG and width."""
    _, text_width = sans_text(label, 0, 0, size, c.text)
    pad, height = size * 0.8, size * 1.9
    width = text_width + 2 * pad
    svg = (
        f'<rect x="{x}" y="{y}" width="{width:.1f}" height="{height:.1f}" rx="{height / 2:.1f}" '
        f'fill="none" stroke="{colour}" stroke-width="4"/>'
    )
    svg += sans_text(label, x + pad, y + height / 2 + size * 0.36, size, c.text)[0]
    return svg, width


def chips(labels: tuple[str, ...], x: float, y: float, c: Palette, size: int = 34) -> str:
    """A row of chips in the icon's colours, blue, green, yellow, then blue again."""
    colours = (c.blue, c.green, c.yellow)
    svg = ""
    for i, label in enumerate(labels):
        part, width = chip(label, x, y, colours[i % len(colours)], c, size)
        svg += part
        x += width + size * 0.6
    return svg


def arrow(x1: float, x2: float, y: float, colour: str) -> str:
    """A horizontal arrow from x1 to x2."""
    head = 16
    return (
        f'<path d="M{x1} {y} H{x2 - head}" stroke="{colour}" stroke-width="6" '
        f'stroke-linecap="round"/>'
        f'<path d="M{x2} {y} L{x2 - head - 4} {y - head} L{x2 - head - 4} {y + head} Z" '
        f'fill="{colour}"/>'
    )


def social_chips(c: Palette) -> str:
    """Candidate A: icon, name, value line, the four ways to use it, what comes out."""
    body = f'<rect width="1280" height="640" fill="{c.bg}"/>'
    body += f'<g transform="translate(96 180) scale(0.65)">{table(c)}</g>'
    left = 400
    body += sans_text(NAME, left, 248, 96, c.text, "extrabold", tracking=-0.03)[0]
    body += sans_text(VALUE, left + 4, 320, 40, c.text)[0]
    body += chips(FRONTS, left + 4, 358, c)
    body += sans_text("Reports as Excel, HTML, CSV or a link", left + 4, 478, 32, c.sub)[0]
    return body


# A small pivot table for candidate B: sales by region and quarter. The totals add up.
QUARTERS = ("Q1", "Q2")
SALES = {"North": (120, 80), "South": (95, 130)}


def pivot_grid(c: Palette, x: float, y: float) -> str:
    """The sample pivot table with header cells, values, totals and a yellow grand total."""
    first, cell, height, gap, size = 170, 130, 82, 12, 36
    columns = (*QUARTERS, "Total")
    totals = [sum(v[i] for v in SALES.values()) for i in range(len(QUARTERS))]
    rows = [(name, (*values, sum(values))) for name, values in SALES.items()]
    rows.append(("Total", (*totals, sum(totals))))

    def box(col: int, row: int, fill: str, label: str, ink: str, weight: str = "medium") -> str:
        left = x if col == 0 else x + first + gap + (col - 1) * (cell + gap)
        width = first if col == 0 else cell
        top = y + row * (height + gap)
        svg = (
            f'<rect x="{left}" y="{top}" width="{width}" height="{height}" rx="12" fill="{fill}"/>'
        )
        baseline = top + height / 2 + size * 0.36
        if col == 0:
            svg += placed(label, left + 22, baseline, size, ink, weight)[0]
        else:
            svg += placed(label, left + width - 22, baseline, size, ink, weight, "right")[0]
        return svg

    svg = "".join(box(i + 1, 0, c.blue, name, c.bg, "extrabold") for i, name in enumerate(columns))
    for r, (name, values) in enumerate(rows, start=1):
        last_row = r == len(rows)
        svg += box(0, r, c.green, name, c.bg, "extrabold")
        for i, value in enumerate(values, start=1):
            grand = last_row and i == len(values)
            total = last_row or i == len(values)
            fill = c.yellow if grand else c.line
            ink = c.bg if grand else c.text
            svg += box(i, r, fill, str(value), ink, "extrabold" if total else "medium")
    return svg


def social_table(c: Palette) -> str:
    """Candidate B: name and value line beside a small pivot table with its grand total."""
    body = f'<rect width="1280" height="640" fill="{c.bg}"/>'
    left = 96
    body += sans_text(NAME, left, 262, 104, c.text, "extrabold", tracking=-0.03)[0]
    body += sans_text("Excel's PivotTable,", left + 4, 336, 40, c.text)[0]
    body += sans_text("for the web", left + 4, 388, 40, c.text)[0]
    body += sans_text(" · ".join(FRONTS), left + 4, 460, 34, c.sub)[0]
    body += pivot_grid(c, 624, 132)
    return body


def social_flow(c: Palette) -> str:
    """Candidate C: data in, pivot view, report out."""
    body = f'<rect width="1280" height="640" fill="{c.bg}"/>'
    body += f'<g transform="translate(96 76) scale(0.3)">{table(c)}</g>'
    body += sans_text(NAME, 236, 168, 80, c.text, "extrabold", tracking=-0.03)[0]
    body += placed(VALUE, 1184, 160, 36, c.sub, align="right")[0]
    # Three columns: the sources, the view, the reports.
    top, row = 248, 82
    sources = ("File", "HTTP", "Code")
    reports = ("Excel", "HTML", "CSV", "Link")
    body += placed("Data", 96, top + 2, 28, c.sub)[0]
    for i, label in enumerate(sources):
        body += chip(label, 96, top + 26 + i * row, c.green, c)[0]
    centre_y = top + 26 + row + 32
    body += arrow(300, 420, centre_y, c.sub)
    view = (
        f'<rect x="440" y="{centre_y - 90}" width="400" height="180" rx="24" fill="none" '
        f'stroke="{c.blue}" stroke-width="4"/>'
    )
    view += placed("Pivot view", 640, centre_y - 8, 44, c.text, "extrabold", "centre")[0]
    view += placed(" · ".join(FRONTS), 640, centre_y + 50, 30, c.sub, align="centre")[0]
    body += view
    body += arrow(860, 980, centre_y, c.sub)
    body += placed("Report", 1000, top + 2, 28, c.sub)[0]
    for i, label in enumerate(reports):
        part, _ = chip(label, 1000, top + 22 + i * 66, c.yellow, c, 30)
        body += part
    body += placed(MODEL, 640, 590, 30, c.sub, align="centre")[0]
    return body


CANDIDATES = {"a": social_chips, "b": social_table, "c": social_flow}


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
    for key, draw in CANDIDATES.items():
        svg = write_svg(OUT / f"social-preview-{key}.svg", 1280, 640, draw(DARK))
        write_png(svg, OUT / f"social-preview-{key}.png", 1280, 640)

    sheet = Image.new("RGB", (1360, 1420), "#d9dce3")
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
    # The candidates fill the grid after the current preview, left to right.
    for i, key in enumerate(CANDIDATES, start=1):
        img = Image.open(OUT / f"social-preview-{key}.png")
        img.thumbnail((640, 320))
        sheet.paste(img, (40 + (i % 2) * 680, 680 + (i // 2) * 360))
    sheet.save(HERE / "overview.png")
    print(f"written to {OUT}")


if __name__ == "__main__":
    main()
