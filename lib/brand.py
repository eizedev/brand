"""Shared building blocks: palette, font outlines, SVG and PNG output.

All lettering is turned into paths, so the SVGs look the same everywhere and the build runs on any
system with rsvg-convert. Marks and wordmarks use DejaVu Sans Mono Bold (``text``); lettering that
should match a documentation site, which shows the system sans-serif, uses Inter (``sans_text``).
Both are bundled in ../fonts. ``sans_text`` shapes with HarfBuzz (kerning), so a script that calls
it declares ``uharfbuzz`` among its dependencies.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "fonts" / "DejaVuSansMono-Bold.ttf"


@dataclass(frozen=True)
class Palette:
    """One Dark colours; the light variant follows One Light."""

    bg: str
    green: str
    blue: str
    yellow: str
    text: str
    sub: str
    line: str


DARK = Palette("#272e3d", "#98c379", "#61afef", "#e5c07b", "#e6e9ef", "#9aa3b2", "#4b5568")
LIGHT = Palette("#ffffff", "#50a14f", "#4078f2", "#c18401", "#1f2430", "#5c6370", "#c8ccd4")

_font = TTFont(FONT)
_glyphs = _font.getGlyphSet()
_cmap = _font.getBestCmap()
_upm = _font["head"].unitsPerEm
_advance = _font["hmtx"].metrics[_cmap[ord("e")]][0]


def glyph(ch: str, x: float, baseline: float, size: float) -> str:
    """SVG path data of one character, baseline at ``baseline``."""
    pen = SVGPathPen(_glyphs)
    k = size / _upm
    _glyphs[_cmap[ord(ch)]].draw(TransformPen(pen, (k, 0, 0, -k, x, baseline)))
    return pen.getCommands()


def text(s: str, x: float, baseline: float, size: float, fill: str) -> tuple[str, float]:
    """Monospaced text as paths; returns the SVG and its width."""
    step = _advance * size / _upm
    paths = "".join(
        f'<path d="{glyph(ch, x + i * step, baseline, size)}" fill="{fill}"/>'
        for i, ch in enumerate(s)
        if ch != " "
    )
    return paths, len(s) * step


# Inter weights in ../fonts; the docs sites set headings at 800 (ExtraBold).
SANS = {
    "extrabold": ROOT / "fonts" / "Inter-ExtraBold.ttf",
    "medium": ROOT / "fonts" / "Inter-Medium.ttf",
}


def sans_text(
    s: str,
    x: float,
    baseline: float,
    size: float,
    fill: str,
    weight: str = "medium",
    tracking: float = 0,
) -> tuple[str, float]:
    """Proportional Inter text as paths, kerned by HarfBuzz; returns the SVG and its width.

    ``tracking`` is extra space per character in em, like CSS ``letter-spacing``.
    """
    import uharfbuzz as hb  # only the scripts that call this need it

    path = SANS[weight]
    font = TTFont(path)
    glyphs, order, upm = font.getGlyphSet(), font.getGlyphOrder(), font["head"].unitsPerEm
    buf = hb.Buffer()
    buf.add_str(s)
    buf.guess_segment_properties()
    hb.shape(hb.Font(hb.Face(hb.Blob.from_file_path(str(path)))), buf, {"kern": True, "liga": True})
    k = size / upm
    pen_x, paths = x, ""
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions, strict=True):
        pen = SVGPathPen(glyphs)
        glyphs[order[info.codepoint]].draw(
            TransformPen(pen, (k, 0, 0, -k, pen_x + pos.x_offset * k, baseline - pos.y_offset * k))
        )
        if commands := pen.getCommands():
            paths += f'<path d="{commands}" fill="{fill}"/>'
        pen_x += pos.x_advance * k + tracking * size
    width = pen_x - x - (tracking * size if s else 0)
    return paths, width


def text_width(s: str, size: float) -> float:
    """Width of monospaced text at ``size``."""
    return len(s) * _advance * size / _upm


def write_svg(path: Path, width: float, height: float, body: str) -> Path:
    """Write a standalone SVG file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}">{body}</svg>\n'
    )
    return path


def write_png(svg: Path, path: Path, width: int, height: int | None = None) -> Path:
    """Render an SVG to PNG with rsvg-convert."""
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["rsvg-convert", "-w", str(width), "-h", str(height or width), str(svg), "-o", str(path)],
        check=True,
    )
    return path
