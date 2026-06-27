#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
FONTS = sorted((ROOT / "fonts" / "ttf").glob("TraceMono*.ttf"))
REQUIRED_TEXT = (
    "TRACE INFO WARN ERROR DEBUG "
    "2026-06-27T10:42:01.932Z "
    "0Oo 1lI| 5S 2Z 8B {}[]()<> /var/log/app.json "
    "GET POST status=503 -> retry"
)


def cmap(font: TTFont) -> dict[int, str]:
    merged: dict[int, str] = {}
    for table in font["cmap"].tables:
        merged.update(table.cmap)
    return merged


def validate_font(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"missing font: {path}")

    font = TTFont(path)
    mapping = cmap(font)
    missing = sorted({ch for ch in REQUIRED_TEXT if ord(ch) not in mapping})
    if missing:
        raise SystemExit(f"{path.name} missing glyphs for: {''.join(missing)}")

    widths = {font["hmtx"].metrics[name][0] for name in font.getGlyphOrder()}
    positive_widths = sorted(width for width in widths if width > 0)
    base_width = positive_widths[0]
    allowed_widths = {0, base_width, base_width * 2}
    unexpected_widths = sorted(widths - allowed_widths)
    if unexpected_widths:
        raise SystemExit(f"{path.name} has unexpected advances: {unexpected_widths}")

    family = font["name"].getDebugName(1)
    full_name = font["name"].getDebugName(4)
    if not family or not full_name:
        raise SystemExit(f"{path.name} missing name table entries")

    print(f"ok {path.name}: {family}, {len(mapping)} mapped glyphs, width={base_width}")


def main() -> None:
    if not FONTS:
        raise SystemExit("no Trace Mono TTF files found")
    for path in FONTS:
        validate_font(path)


if __name__ == "__main__":
    main()
