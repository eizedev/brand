# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools>=4.50", "pillow>=10"]
# ///
"""Icon, header and social preview of ha-synology-srm-router, the Home Assistant integration.

It uses the network mark of aiosynologysrm, the library it is built on, so both read as one
family; the lettering names the integration instead.

Run: uv run ha-synology-srm-router/build.py   (writes to ha-synology-srm-router/out/)
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from PIL import Image  # noqa: E402

from brand import DARK, LIGHT, Palette, text, write_png, write_svg  # noqa: E402

_spec = importlib.util.spec_from_file_location("library_mark", ROOT / "aiosynologysrm" / "build.py")
assert _spec and _spec.loader
_library = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_library)
network, icon = _library.network, _library.icon

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
NAME = "Synology SRM Router"
SUBTITLE = "for Home Assistant"
TAGLINE = ("Trackers, WAN, DHCP, firewall and USB", "of routers and access points, read only")


def header(c: Palette, size: int = 64) -> tuple[str, int, int]:
    """Icon mark, name and subtitle for the README header (transparent background)."""
    height = int(size * 2.2)
    mark_size = size * 2.0
    mark = (
        f'<g transform="translate(0 {(height - mark_size) / 2:.1f}) scale({mark_size / 400:.4f})">'
        f"{network(c)}</g>"
    )
    x = size * 2.0
    name, width = text(NAME, x, height / 2 + size * 0.05, size, c.text)
    sub, _ = text(SUBTITLE, x + 4, height / 2 + size * 0.75, size * 0.5, c.sub)
    return mark + name + sub, int(x + width + 12), height


def social(c: Palette) -> str:
    """GitHub social preview, 1280x640."""
    body = f'<rect width="1280" height="640" fill="{c.bg}"/>'
    body += f'<g transform="translate(110 150) scale(0.85)">{network(c)}</g>'
    body += text(NAME, 460, 300, 62, c.text)[0]
    body += text(SUBTITLE, 464, 356, 34, c.blue)[0]
    body += text(TAGLINE[0], 464, 430, 28, c.sub)[0]
    body += text(TAGLINE[1], 464, 470, 28, c.sub)[0]
    return body


def main() -> None:
    """Write every file and a review sheet."""
    full = write_svg(OUT / "icon.svg", 400, 400, icon(DARK))
    # Home Assistant shows brand/icon.png (256 px) and brand/icon@2x.png (512 px).
    write_png(full, OUT / "icon.png", 256)
    write_png(full, OUT / "icon@2x.png", 512)
    for variant, palette in (("dark", DARK), ("light", LIGHT)):
        body, w, h = header(palette)
        svg = write_svg(OUT / f"header-{variant}.svg", w, h, body)
        write_png(svg, OUT / f"header-{variant}@2x.png", w * 2, h * 2)
    preview = write_svg(OUT / "social-preview.svg", 1280, 640, social(DARK))
    write_png(preview, OUT / "social-preview.png", 1280, 640)

    sheet = Image.new("RGB", (1360, 900), "#d9dce3")
    big = Image.open(OUT / "icon@2x.png").resize((300, 300))
    sheet.paste(big, (40, 40), big)
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
