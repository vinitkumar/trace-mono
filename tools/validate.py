#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
FONTS = [
    ROOT / "fonts" / "ttf" / "TraceMonoConsole-Regular.ttf",
    ROOT / "fonts" / "ttf" / "TraceMonoInspect-Regular.ttf",
]
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
    if len(widths) != 1:
        raise SystemExit(f"{path.name} is not monospace: widths={sorted(widths)}")

    family = font["name"].getDebugName(1)
    full_name = font["name"].getDebugName(4)
    if not family or not full_name:
        raise SystemExit(f"{path.name} missing name table entries")

    print(f"ok {path.name}: {family}, {len(mapping)} mapped glyphs, width={widths.pop()}")


def main() -> None:
    for path in FONTS:
        validate_font(path)


if __name__ == "__main__":
    main()
