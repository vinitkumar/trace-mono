#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FONT_PATH = ROOT / "fonts" / "ttf" / "TraceMonoConsole-Regular.ttf"
OUT_DIR = ROOT / "images"

BG = "#111315"
PANEL = "#191c1f"
TITLE = "#c9d1d9"
MUTED = "#8b949e"
TEXT = "#e8ecef"
GREEN = "#55d6be"
YELLOW = "#f4c95d"
RED = "#ff6b6b"
BLUE = "#7aa2f7"


LINES = [
    [("INFO ", GREEN), (" 2026-06-27T10:42:01.932Z api.gateway request_id=8f14e45f-ea5d-4c12-9281-7a8f67", TEXT)],
    [("WARN ", YELLOW), (" 2026-06-27T10:42:02.104Z cache.miss key=user:1042 ttl=0ms path=/v1/users/1042", TEXT)],
    [("ERROR", RED), (" 2026-06-27T10:42:02.337Z db.pool timeout after 2500ms host=10.42.0.17 port=5432", TEXT)],
    [("      at connect(pool.py:184) -> acquire(pool.py:92) -> handle_request(app.py:61)", MUTED)],
    [('      payload={"status":503,"retry":true,"trace":"0O1lI|5S2Z8B"}', TEXT)],
    [("", TEXT)],
    [("Ambiguity check: ", BLUE), ("0 O o   1 l I |   5 S s   2 Z z   8 B b   rn m nn", TEXT)],
    [("JSON/path check: ", BLUE), ("{} [] () <>  /var/log/app.json  status=503  retry=true", TEXT)],
    [("Box drawing:     ", BLUE), ("├─ parser.decode_json -> storage.write_batch -> notifier.enqueue", TEXT)],
]


def rounded_rectangle(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill: str) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def draw_window(label: str, subtitle: str, out_path: Path) -> None:
    width = 1280
    height = 720
    chrome_h = 56
    pad = 28
    font = ImageFont.truetype(str(FONT_PATH), 24)
    small = ImageFont.truetype(str(FONT_PATH), 18)
    title_font = ImageFont.truetype(str(FONT_PATH), 20)

    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    rounded_rectangle(draw, (24, 24, width - 24, height - 24), 8, PANEL)
    draw.rectangle((24, 24 + chrome_h, width - 24, 24 + chrome_h + 1), fill="#31363b")

    for index, color in enumerate(("#ff6b6b", "#f4c95d", "#55d6be")):
        cx = 52 + index * 24
        draw.ellipse((cx, 45, cx + 12, 57), fill=color)

    draw.text((142, 38), label, font=title_font, fill=TITLE)
    draw.text((width - 430, 39), subtitle, font=small, fill=MUTED)

    x = 24 + pad
    y = 24 + chrome_h + 30
    line_h = 36

    draw.text((x, y), "$ tail -f /var/log/api.log", font=font, fill=GREEN)
    y += line_h * 2

    for line in LINES:
        cursor_x = x
        for text, color in line:
            draw.text((cursor_x, y), text, font=font, fill=color)
            cursor_x += int(draw.textlength(text, font=font))
        y += line_h

    image.save(out_path)
    print(out_path)


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    draw_window(
        "Ghostty - Trace Mono Console",
        'font-family = "Trace Mono Console"',
        OUT_DIR / "ghostty-trace-mono.png",
    )
    draw_window(
        "Kitty - Trace Mono Console",
        "font_family Trace Mono Console",
        OUT_DIR / "kitty-trace-mono.png",
    )


if __name__ == "__main__":
    main()
