#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import newTable


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "fonts" / "ttf"
UPM = 1000
ASCENT = 840
DESCENT = -240
CAP = 720
X_HEIGHT = 500
BASE = 0


@dataclass(frozen=True)
class Cut:
    family: str
    filename: str
    width: int
    side: int
    stroke: int


CUTS = [
    Cut("Trace Mono Console", "TraceMonoConsole-Regular.ttf", 600, 76, 72),
    Cut("Trace Mono Inspect", "TraceMonoInspect-Regular.ttf", 640, 92, 70),
]


ASCII = [chr(code) for code in range(32, 127)]
EXTRAS = ["\u00a0", "\u2190", "\u2191", "\u2192", "\u2193", "\u2500", "\u2502", "\u2514", "\u251c", "\u2518", "\ufffd"]


def glyph_name(ch: str) -> str:
    names = {
        " ": "space",
        "\u00a0": "nbsp",
        "\ufffd": "uniFFFD",
    }
    if ch in names:
        return names[ch]
    code = ord(ch)
    if ch.isalnum():
        return ch if ch.isupper() else f"{ch}.lower"
    if code < 128:
        return {
            "!": "exclam",
            '"': "quotedbl",
            "#": "numbersign",
            "$": "dollar",
            "%": "percent",
            "&": "ampersand",
            "'": "quotesingle",
            "(": "parenleft",
            ")": "parenright",
            "*": "asterisk",
            "+": "plus",
            ",": "comma",
            "-": "hyphen",
            ".": "period",
            "/": "slash",
            ":": "colon",
            ";": "semicolon",
            "<": "less",
            "=": "equal",
            ">": "greater",
            "?": "question",
            "@": "at",
            "[": "bracketleft",
            "\\": "backslash",
            "]": "bracketright",
            "^": "asciicircum",
            "_": "underscore",
            "`": "grave",
            "{": "braceleft",
            "|": "bar",
            "}": "braceright",
            "~": "asciitilde",
        }[ch]
    return f"uni{code:04X}"


def empty_glyph():
    return TTGlyphPen(None).glyph()


def close_path(pen: TTGlyphPen, points: list[tuple[float, float]]) -> None:
    pen.moveTo(points[0])
    for point in points[1:]:
        pen.lineTo(point)
    pen.closePath()


def rect(pen: TTGlyphPen, x: float, y: float, w: float, h: float) -> None:
    close_path(pen, [(x, y), (x + w, y), (x + w, y + h), (x, y + h)])


def stroke(pen: TTGlyphPen, x1: float, y1: float, x2: float, y2: float, width: float) -> None:
    dx = x2 - x1
    dy = y2 - y1
    length = hypot(dx, dy) or 1
    ox = -dy / length * width / 2
    oy = dx / length * width / 2
    close_path(pen, [(x1 + ox, y1 + oy), (x2 + ox, y2 + oy), (x2 - ox, y2 - oy), (x1 - ox, y1 - oy)])


def dot(pen: TTGlyphPen, cx: float, cy: float, size: float) -> None:
    rect(pen, cx - size / 2, cy - size / 2, size, size)


def draw_segments(pen: TTGlyphPen, cut: Cut, segments: str, lower: bool = False) -> None:
    x0 = cut.side
    x1 = cut.width - cut.side
    y0 = BASE + (20 if lower else 0)
    y3 = X_HEIGHT if lower else CAP
    y1 = y0 + (y3 - y0) / 2
    s = cut.stroke
    inset = s * 0.4
    coords = {
        "A": (x0 + inset, y3, x1 - inset, y3),
        "B": (x1, y3 - inset, x1, y1 + inset),
        "C": (x1, y1 - inset, x1, y0 + inset),
        "D": (x0 + inset, y0, x1 - inset, y0),
        "E": (x0, y1 - inset, x0, y0 + inset),
        "F": (x0, y3 - inset, x0, y1 + inset),
        "G": (x0 + inset, y1, x1 - inset, y1),
        "H": (x0 + s * 0.25, y3 - s * 0.4, x1 - s * 0.25, y0 + s * 0.4),
        "I": (x1 - s * 0.25, y3 - s * 0.4, x0 + s * 0.25, y0 + s * 0.4),
        "J": (x0 + s * 0.2, y3 - s * 0.3, x1 - s * 0.2, y0 + s * 0.3),
    }
    for name in segments:
        stroke(pen, *coords[name], s)


UPPER_SEGMENTS = {
    "A": "ABCEFG",
    "B": "ABCDEFG",
    "C": "AFED",
    "D": "ABCDEF",
    "E": "AFGED",
    "F": "AFGE",
    "G": "AFEDCG",
    "H": "BCEFG",
    "I": "ADJ",
    "J": "BCDE",
    "K": "FEGI",
    "L": "FED",
    "M": "FBECH",
    "N": "FBECH",
    "O": "ABCDEF",
    "P": "ABEFG",
    "Q": "ABCDEFI",
    "R": "ABEFGI",
    "S": "AFGCD",
    "T": "AJ",
    "U": "BCDEF",
    "V": "FEH",
    "W": "FCEBJ",
    "X": "HI",
    "Y": "HIG",
    "Z": "AID",
}

DIGIT_SEGMENTS = {
    "0": "ABCDEF",
    "1": "BC",
    "2": "ABGED",
    "3": "ABGCD",
    "4": "FBGC",
    "5": "AFGCD",
    "6": "AFGECD",
    "7": "ABC",
    "8": "ABCDEFG",
    "9": "ABFGCD",
}


def draw_ascii_glyph(ch: str, cut: Cut):
    pen = TTGlyphPen(None)
    w = cut.width
    s = cut.stroke
    left = cut.side
    right = w - cut.side
    mid = w / 2

    if ch in (" ", "\u00a0"):
        return empty_glyph()
    if ch.isdigit():
        draw_segments(pen, cut, DIGIT_SEGMENTS[ch])
        if ch == "0":
            stroke(pen, left + 70, 100, right - 70, CAP - 100, s * 0.52)
        if ch == "1":
            stroke(pen, mid - 70, CAP - 60, mid, CAP, s * 0.55)
            stroke(pen, mid - 115, 0, mid + 115, 0, s * 0.62)
        return pen.glyph()
    if "A" <= ch <= "Z":
        draw_segments(pen, cut, UPPER_SEGMENTS[ch])
        return pen.glyph()
    if "a" <= ch <= "z":
        upper = ch.upper()
        if ch == "i":
            stroke(pen, mid, 0, mid, X_HEIGHT - 90, s * 0.66)
            dot(pen, mid, CAP - 75, s * 0.72)
        elif ch == "j":
            stroke(pen, mid + 50, X_HEIGHT - 90, mid + 50, -170, s * 0.66)
            stroke(pen, mid + 45, -170, mid - 115, -120, s * 0.66)
            dot(pen, mid + 50, CAP - 75, s * 0.72)
        elif ch == "l":
            stroke(pen, mid, 0, mid, CAP, s * 0.55)
            stroke(pen, mid - 74, 0, mid + 74, 0, s * 0.5)
        elif ch == "m":
            stroke(pen, left, 0, left, X_HEIGHT, s * 0.64)
            stroke(pen, left, X_HEIGHT, mid, 250, s * 0.64)
            stroke(pen, mid, 250, right, X_HEIGHT, s * 0.64)
            stroke(pen, right, X_HEIGHT, right, 0, s * 0.64)
        elif ch == "n":
            stroke(pen, left, 0, left, X_HEIGHT, s * 0.66)
            stroke(pen, left, X_HEIGHT, right, 0, s * 0.66)
            stroke(pen, right, X_HEIGHT, right, 0, s * 0.66)
        else:
            draw_segments(pen, cut, UPPER_SEGMENTS.get(upper, "ABCDEFG"), lower=True)
        return pen.glyph()

    if ch == ".":
        dot(pen, mid, 34, s * 0.78)
    elif ch == ",":
        dot(pen, mid, 52, s * 0.78)
        stroke(pen, mid + 12, 22, mid - 42, -110, s * 0.4)
    elif ch == ":":
        dot(pen, mid, 170, s * 0.72)
        dot(pen, mid, 470, s * 0.72)
    elif ch == ";":
        dot(pen, mid, 470, s * 0.72)
        dot(pen, mid, 170, s * 0.72)
        stroke(pen, mid + 12, 140, mid - 42, 8, s * 0.4)
    elif ch in "'`":
        stroke(pen, mid - (30 if ch == "`" else -30), CAP, mid + (15 if ch == "`" else -15), CAP - 170, s * 0.45)
    elif ch == '"':
        stroke(pen, mid - 80, CAP, mid - 100, CAP - 170, s * 0.4)
        stroke(pen, mid + 100, CAP, mid + 80, CAP - 170, s * 0.4)
    elif ch == "-":
        stroke(pen, left + 70, 330, right - 70, 330, s * 0.58)
    elif ch == "_":
        stroke(pen, left, -70, right, -70, s * 0.55)
    elif ch == "=":
        stroke(pen, left + 55, 420, right - 55, 420, s * 0.48)
        stroke(pen, left + 55, 240, right - 55, 240, s * 0.48)
    elif ch == "+":
        stroke(pen, left + 60, 330, right - 60, 330, s * 0.5)
        stroke(pen, mid, 120, mid, 540, s * 0.5)
    elif ch == "*":
        stroke(pen, left + 95, 180, right - 95, 560, s * 0.42)
        stroke(pen, left + 95, 560, right - 95, 180, s * 0.42)
        stroke(pen, mid, 120, mid, 620, s * 0.38)
    elif ch == "/":
        stroke(pen, left + 18, -80, right - 18, CAP + 60, s * 0.5)
    elif ch == "\\":
        stroke(pen, left + 18, CAP + 60, right - 18, -80, s * 0.5)
    elif ch == "|":
        stroke(pen, mid, -120, mid, CAP + 120, s * 0.48)
    elif ch in "()[]{}<>":
        opening = ch in "([{<"
        x_outer = left + 65 if opening else right - 65
        x_inner = right - 80 if opening else left + 80
        if ch in "()":
            stroke(pen, x_inner, CAP, x_outer, CAP - 90, s * 0.5)
            stroke(pen, x_outer, CAP - 90, x_outer, 90, s * 0.5)
            stroke(pen, x_outer, 90, x_inner, 0, s * 0.5)
        elif ch in "[]":
            stroke(pen, x_outer, 0, x_outer, CAP, s * 0.52)
            stroke(pen, x_outer, CAP, x_inner, CAP, s * 0.52)
            stroke(pen, x_outer, 0, x_inner, 0, s * 0.52)
        elif ch in "{}":
            stroke(pen, x_inner, CAP, x_outer, CAP - 110, s * 0.48)
            stroke(pen, x_outer, CAP - 110, x_outer, 390, s * 0.48)
            stroke(pen, x_outer, 390, x_inner, 330, s * 0.48)
            stroke(pen, x_inner, 330, x_outer, 270, s * 0.48)
            stroke(pen, x_outer, 270, x_outer, 110, s * 0.48)
            stroke(pen, x_outer, 110, x_inner, 0, s * 0.48)
        else:
            stroke(pen, x_inner, CAP, x_outer, 330, s * 0.52)
            stroke(pen, x_outer, 330, x_inner, 0, s * 0.52)
    elif ch == "!":
        stroke(pen, mid, 170, mid, CAP, s * 0.58)
        dot(pen, mid, 34, s * 0.76)
    elif ch == "?":
        stroke(pen, left + 100, CAP - 80, mid, CAP, s * 0.55)
        stroke(pen, mid, CAP, right - 92, CAP - 110, s * 0.55)
        stroke(pen, right - 92, CAP - 110, mid + 10, 360, s * 0.55)
        stroke(pen, mid + 10, 360, mid + 10, 220, s * 0.5)
        dot(pen, mid + 10, 34, s * 0.76)
    elif ch == "#":
        stroke(pen, left + 70, 470, right - 70, 470, s * 0.42)
        stroke(pen, left + 60, 250, right - 60, 250, s * 0.42)
        stroke(pen, mid - 90, 70, mid - 34, CAP - 40, s * 0.42)
        stroke(pen, mid + 34, 70, mid + 90, CAP - 40, s * 0.42)
    elif ch == "$":
        draw_segments(pen, cut, "AFGCD")
        stroke(pen, mid, -50, mid, CAP + 50, s * 0.38)
    elif ch == "%":
        dot(pen, left + 110, CAP - 115, s * 0.74)
        dot(pen, right - 110, 115, s * 0.74)
        stroke(pen, left + 80, 10, right - 80, CAP - 10, s * 0.42)
    elif ch == "&":
        draw_segments(pen, cut, "AFGED")
        stroke(pen, mid - 20, 360, right - 70, 0, s * 0.52)
    elif ch == "@":
        draw_segments(pen, cut, "ABCDEF")
        stroke(pen, mid - 40, 230, right - 120, 230, s * 0.45)
        stroke(pen, right - 120, 230, right - 120, 500, s * 0.45)
        stroke(pen, right - 120, 500, mid - 70, 500, s * 0.45)
    elif ch == "^":
        stroke(pen, left + 130, 420, mid, CAP, s * 0.44)
        stroke(pen, mid, CAP, right - 130, 420, s * 0.44)
    elif ch == "~":
        stroke(pen, left + 65, 300, mid - 30, 390, s * 0.42)
        stroke(pen, mid - 30, 390, mid + 30, 270, s * 0.42)
        stroke(pen, mid + 30, 270, right - 65, 360, s * 0.42)
    else:
        rect(pen, left, 0, right - left, CAP)
    return pen.glyph()


def draw_extra_glyph(ch: str, cut: Cut):
    pen = TTGlyphPen(None)
    w = cut.width
    s = cut.stroke
    mid = w / 2
    if ch == "\ufffd":
        rect(pen, cut.side, 0, w - 2 * cut.side, CAP)
        stroke(pen, cut.side + 80, 100, w - cut.side - 80, CAP - 100, s * 0.45)
        stroke(pen, cut.side + 80, CAP - 100, w - cut.side - 80, 100, s * 0.45)
    elif ch in "\u2190\u2192":
        y = 330
        stroke(pen, cut.side + 70, y, w - cut.side - 70, y, s * 0.52)
        if ch == "\u2190":
            stroke(pen, cut.side + 70, y, cut.side + 210, y + 130, s * 0.52)
            stroke(pen, cut.side + 70, y, cut.side + 210, y - 130, s * 0.52)
        else:
            stroke(pen, w - cut.side - 70, y, w - cut.side - 210, y + 130, s * 0.52)
            stroke(pen, w - cut.side - 70, y, w - cut.side - 210, y - 130, s * 0.52)
    elif ch in "\u2191\u2193":
        stroke(pen, mid, 60, mid, CAP - 60, s * 0.52)
        if ch == "\u2191":
            stroke(pen, mid, CAP - 60, mid - 120, CAP - 200, s * 0.52)
            stroke(pen, mid, CAP - 60, mid + 120, CAP - 200, s * 0.52)
        else:
            stroke(pen, mid, 60, mid - 120, 200, s * 0.52)
            stroke(pen, mid, 60, mid + 120, 200, s * 0.52)
    elif ch == "\u2500":
        stroke(pen, 0, 330, w, 330, s * 0.45)
    elif ch == "\u2502":
        stroke(pen, mid, DESCENT, mid, ASCENT, s * 0.45)
    elif ch == "\u2514":
        stroke(pen, mid, ASCENT, mid, 330, s * 0.45)
        stroke(pen, mid, 330, w, 330, s * 0.45)
    elif ch == "\u251c":
        stroke(pen, mid, DESCENT, mid, ASCENT, s * 0.45)
        stroke(pen, mid, 330, w, 330, s * 0.45)
    elif ch == "\u2518":
        stroke(pen, mid, ASCENT, mid, 330, s * 0.45)
        stroke(pen, 0, 330, mid, 330, s * 0.45)
    else:
        return draw_ascii_glyph(" ", cut)
    return pen.glyph()


def build_cut(cut: Cut) -> None:
    chars = ASCII + EXTRAS
    glyph_order = [".notdef"] + [glyph_name(ch) for ch in chars]
    glyphs = {".notdef": draw_extra_glyph("\ufffd", cut)}
    cmap = {}

    for ch in chars:
        name = glyph_name(ch)
        glyphs[name] = draw_extra_glyph(ch, cut) if ord(ch) > 126 else draw_ascii_glyph(ch, cut)
        cmap[ord(ch)] = name

    metrics = {name: (cut.width, 0) for name in glyph_order}
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ASCENT, descent=DESCENT)
    fb.setupOS2(
        sTypoAscender=ASCENT,
        sTypoDescender=DESCENT,
        usWinAscent=ASCENT,
        usWinDescent=abs(DESCENT),
        sxHeight=X_HEIGHT,
        sCapHeight=CAP,
        panose={
            "bFamilyType": 2,
            "bSerifStyle": 11,
            "bWeight": 5,
            "bProportion": 9,
            "bContrast": 2,
            "bStrokeVariation": 2,
            "bArmStyle": 2,
            "bLetterForm": 2,
            "bMidline": 2,
            "bXHeight": 4,
        },
    )
    fb.setupPost()
    fb.setupNameTable(
        {
            "familyName": cut.family,
            "styleName": "Regular",
            "uniqueFontIdentifier": f"{cut.family} Regular 0.1.0",
            "fullName": f"{cut.family} Regular",
            "psName": cut.family.replace(" ", "") + "-Regular",
            "version": "Version 0.1.0",
            "manufacturer": "Vinit Kumar",
            "designer": "Vinit Kumar",
            "description": "Original terminal and log-reading monospace font.",
            "licenseDescription": "SIL Open Font License, Version 1.1",
            "licenseInfoURL": "https://openfontlicense.org",
        }
    )
    font = fb.font
    font["head"].macStyle = 0
    font["OS/2"].usWeightClass = 400
    font["OS/2"].usWidthClass = 5
    font["OS/2"].fsSelection = 0x40
    font["hhea"].lineGap = 0
    font["OS/2"].sTypoLineGap = 0
    font["gasp"] = newTable("gasp")
    font["gasp"].gaspRange = {65535: 10}

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    font.save(OUT_DIR / cut.filename)
    print(f"built {OUT_DIR / cut.filename}")


def main() -> None:
    for cut in CUTS:
        build_cut(cut)


if __name__ == "__main__":
    main()
