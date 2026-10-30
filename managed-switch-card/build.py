# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools>=4.50", "pillow>=10"]
# ///
"""Icon, header and social preview of managed-switch-card, the Home Assistant dashboard card.

It uses the switch mark of aiosnmpswitch, the library it is built on, so both read as one
family; the lettering names the integration instead.

Run: uv run managed-switch-card/build.py   (writes to managed-switch-card/out/)
"""

from __future__ import annotations

import dataclasses
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from PIL import Image  # noqa: E402

from brand import DARK, LIGHT, Palette, text, write_png, write_svg  # noqa: E402

_spec = importlib.util.spec_from_file_location("library_mark", ROOT / "aiosnmpswitch" / "build.py")
assert _spec and _spec.loader
_library = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_library)
switch, icon = _library.switch, _library.icon

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
NAME = "Managed Switch Card"
SUBTITLE = "for Home Assistant dashboards"
TAGLINE = ("The front panel of your switches:", "link, speed, PoE and devices per port")


def header(c: Palette, size: int = 64) -> tuple[str, int, int]:
    """Icon mark, name and subtitle for the README header (transparent background)."""
    height = int(size * 2.2)
    mark_size = size * 2.0
    mark = (
        f'<g transform="translate(0 {(height - mark_size) / 2:.1f}) scale({mark_size / 400:.4f})">'
        f"{switch(c)}</g>"
    )
    x = size * 2.0
    name, width = text(NAME, x, height / 2 + size * 0.05, size, c.text)
    sub, _ = text(SUBTITLE, x + 4, height / 2 + size * 0.75, size * 0.5, c.sub)
    return mark + name + sub, int(x + width + 12), height


def social(c: Palette) -> str:
    """GitHub social preview, 1280x640."""
    body = f'<rect width="1280" height="640" fill="{c.bg}"/>'
    body += f'<g transform="translate(110 150) scale(0.85)">{switch(c)}</g>'
    body += text(NAME, 460, 300, 62, c.text)[0]
    body += text(SUBTITLE, 464, 356, 34, c.blue)[0]
    body += text(TAGLINE[0], 464, 430, 28, c.sub)[0]
    body += text(TAGLINE[1], 464, 470, 28, c.sub)[0]
    return body


# On white the light palette's pale links would almost vanish; the mark uses a mid grey there.
ON_WHITE = dataclasses.replace(LIGHT, line="#9aa3b2")


def ha_icon(c: Palette, name: str) -> None:
    """Home Assistant brand icon: the mark alone on transparency, trimmed and square.

    Home Assistant's brand rules prefer transparent, trimmed images and an icon for a white
    background (icon.png), with dark_icon.png for dark themes.
    """
    svg = write_svg(OUT / f"{name}-mark.svg", 400, 400, switch(c))
    big = Image.open(write_png(svg, OUT / f"{name}-full.png", 1024)).convert("RGBA")
    mark = big.crop(big.getbbox())
    side = max(mark.size)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.paste(mark, ((side - mark.width) // 2, (side - mark.height) // 2))
    for size, suffix in ((256, ""), (512, "@2x")):
        square.resize((size, size), Image.LANCZOS).save(OUT / f"{name}{suffix}.png")
    (OUT / f"{name}-full.png").unlink()
    svg.unlink()


def main() -> None:
    """Write every file and a review sheet."""
    write_svg(OUT / "icon.svg", 400, 400, icon(DARK))  # the README's and docs' app icon
    # Home Assistant shows brand/icon.png and brand/dark_icon.png (256 px, @2x 512 px).
    ha_icon(ON_WHITE, "icon")
    ha_icon(DARK, "dark_icon")
    for variant, palette in (("dark", DARK), ("light", LIGHT)):
        body, w, h = header(palette)
        svg = write_svg(OUT / f"header-{variant}.svg", w, h, body)
        write_png(svg, OUT / f"header-{variant}@2x.png", w * 2, h * 2)
    preview = write_svg(OUT / "social-preview.svg", 1280, 640, social(DARK))
    write_png(preview, OUT / "social-preview.png", 1280, 640)

    sheet = Image.new("RGB", (1360, 900), "#d9dce3")
    for i, (name, bg) in enumerate((("icon", "#ffffff"), ("dark_icon", DARK.bg))):
        tile = Image.new("RGB", (300, 300), bg)
        big = Image.open(OUT / f"{name}@2x.png").resize((260, 260))
        tile.paste(big, (20, 20), big)
        sheet.paste(tile, (40 + i * 340, 40))
    for i, variant in enumerate(("dark", "light")):
        img = Image.open(OUT / f"header-{variant}@2x.png")
        img.thumbnail((620, 200))
        tile = Image.new("RGB", (640, 170), DARK.bg if variant == "dark" else "#ffffff")
        tile.paste(img, (10, (170 - img.height) // 2), img)
        sheet.paste(tile, (40 + i * 680, 370))
    preview_img = Image.open(OUT / "social-preview.png")
    preview_img.thumbnail((640, 320))
    sheet.paste(preview_img, (40, 570))
    sheet.save(HERE / "overview.png")
    print(f"written to {OUT}")


if __name__ == "__main__":
    main()
