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
    Cut("Trace Mono Console", "TraceMonoConsole-Regular.ttf", 600, 52, 84),
    Cut("Trace Mono Inspect", "TraceMonoInspect-Regular.ttf", 640, 70, 82),
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


def draw_trace_glyph(ch: str, cut: Cut):
    pen = TTGlyphPen(None)
    w = cut.width
    s = cut.stroke * 0.74
    left = cut.side
    right = w - cut.side
    mid = w / 2
    cap_top = CAP
    lower_top = X_HEIGHT + 10

    def sx(x: float) -> float:
        return left + (right - left) * x / 10

    def sy(y: float, lower: bool) -> float:
        top = lower_top if lower else cap_top
        return BASE + top * y / 14

    def line(x1: float, y1: float, x2: float, y2: float, lower: bool = False, width: float | None = None) -> None:
        stroke(pen, sx(x1), sy(y1, lower), sx(x2), sy(y2, lower), width or s)

    def bowl(x0: float, y0: float, x1: float, y1: float, lower: bool = False, open_left: bool = False, open_right: bool = False) -> None:
        if not open_left:
            line(x0, y0 + 1, x0, y1 - 1, lower)
        if not open_right:
            line(x1, y0 + 1, x1, y1 - 1, lower)
        line(x0 + 1, y1, x1 - 1, y1, lower)
        line(x0 + 1, y0, x1 - 1, y0, lower)

    uppercase = {
        "A": [(0, 0, 0, 11), (10, 0, 10, 11), (1, 12, 5, 14), (9, 12, 5, 14), (0, 7, 10, 7)],
        "B": [(0, 0, 0, 14), (0, 14, 7, 14), (7, 14, 10, 12), (10, 12, 10, 8), (10, 8, 7, 7), (0, 7, 7, 7), (7, 7, 10, 5), (10, 5, 10, 2), (10, 2, 7, 0), (0, 0, 7, 0)],
        "C": [(10, 13, 8, 14), (8, 14, 2, 14), (2, 14, 0, 12), (0, 12, 0, 2), (0, 2, 2, 0), (2, 0, 8, 0), (8, 0, 10, 1)],
        "D": [(0, 0, 0, 14), (0, 14, 7, 14), (7, 14, 10, 11), (10, 11, 10, 3), (10, 3, 7, 0), (0, 0, 7, 0)],
        "E": [(0, 0, 0, 14), (0, 14, 10, 14), (0, 7, 8, 7), (0, 0, 10, 0)],
        "F": [(0, 0, 0, 14), (0, 14, 10, 14), (0, 7, 8, 7)],
        "G": [(10, 13, 8, 14), (8, 14, 2, 14), (2, 14, 0, 12), (0, 12, 0, 2), (0, 2, 2, 0), (2, 0, 8, 0), (8, 0, 10, 2), (10, 2, 10, 6), (6, 6, 10, 6)],
        "H": [(0, 0, 0, 14), (10, 0, 10, 14), (0, 7, 10, 7)],
        "I": [(0, 14, 10, 14), (5, 14, 5, 0), (0, 0, 10, 0)],
        "J": [(1, 14, 10, 14), (8, 14, 8, 2), (8, 2, 6, 0), (6, 0, 2, 0), (2, 0, 0, 2)],
        "K": [(0, 0, 0, 14), (10, 14, 0, 6), (2, 7, 10, 0)],
        "L": [(0, 14, 0, 0), (0, 0, 10, 0)],
        "M": [(0, 0, 0, 14), (0, 14, 5, 8), (5, 8, 10, 14), (10, 14, 10, 0)],
        "N": [(0, 0, 0, 14), (0, 14, 10, 0), (10, 0, 10, 14)],
        "O": [(2, 0, 8, 0), (8, 0, 10, 2), (10, 2, 10, 12), (10, 12, 8, 14), (8, 14, 2, 14), (2, 14, 0, 12), (0, 12, 0, 2), (0, 2, 2, 0)],
        "P": [(0, 0, 0, 14), (0, 14, 8, 14), (8, 14, 10, 12), (10, 12, 10, 8), (10, 8, 8, 6), (0, 6, 8, 6)],
        "Q": [(2, 0, 8, 0), (8, 0, 10, 2), (10, 2, 10, 12), (10, 12, 8, 14), (8, 14, 2, 14), (2, 14, 0, 12), (0, 12, 0, 2), (0, 2, 2, 0), (6, 3, 10, -1)],
        "R": [(0, 0, 0, 14), (0, 14, 8, 14), (8, 14, 10, 12), (10, 12, 10, 8), (10, 8, 8, 6), (0, 6, 8, 6), (6, 6, 10, 0)],
        "S": [(10, 13, 8, 14), (8, 14, 2, 14), (2, 14, 0, 12), (0, 12, 0, 8), (0, 8, 2, 7), (2, 7, 8, 7), (8, 7, 10, 6), (10, 6, 10, 2), (10, 2, 8, 0), (8, 0, 2, 0), (2, 0, 0, 1)],
        "T": [(0, 14, 10, 14), (5, 14, 5, 0)],
        "U": [(0, 14, 0, 2), (0, 2, 2, 0), (2, 0, 8, 0), (8, 0, 10, 2), (10, 2, 10, 14)],
        "V": [(0, 14, 4, 0), (10, 14, 6, 0), (4, 0, 6, 0)],
        "W": [(0, 14, 1, 0), (1, 0, 5, 5), (5, 5, 9, 0), (9, 0, 10, 14)],
        "X": [(0, 14, 10, 0), (10, 14, 0, 0)],
        "Y": [(0, 14, 5, 7), (10, 14, 5, 7), (5, 7, 5, 0)],
        "Z": [(0, 14, 10, 14), (10, 14, 0, 0), (0, 0, 10, 0)],
    }

    lowercase = {
        "a": [(2, 10, 8, 10), (8, 10, 10, 8), (10, 8, 10, 0), (10, 5, 2, 5), (2, 5, 0, 3), (0, 3, 0, 2), (0, 2, 2, 0), (2, 0, 10, 0)],
        "b": [(0, 0, 0, 14), (0, 9, 2, 10), (2, 10, 8, 10), (8, 10, 10, 8), (10, 8, 10, 2), (10, 2, 8, 0), (8, 0, 2, 0), (2, 0, 0, 1)],
        "c": [(10, 9, 8, 10), (8, 10, 2, 10), (2, 10, 0, 8), (0, 8, 0, 2), (0, 2, 2, 0), (2, 0, 8, 0), (8, 0, 10, 1)],
        "d": [(10, 0, 10, 14), (10, 9, 8, 10), (8, 10, 2, 10), (2, 10, 0, 8), (0, 8, 0, 2), (0, 2, 2, 0), (2, 0, 8, 0), (8, 0, 10, 1)],
        "e": [(0, 5, 10, 5), (10, 5, 10, 8), (10, 8, 8, 10), (8, 10, 2, 10), (2, 10, 0, 8), (0, 8, 0, 2), (0, 2, 2, 0), (2, 0, 9, 0)],
        "f": [(8, 14, 6, 14), (6, 14, 4, 12), (4, 12, 4, 0), (1, 9, 8, 9)],
        "g": [(10, 10, 10, -3), (10, -3, 8, -5), (8, -5, 2, -5), (2, -5, 0, -3), (2, 10, 8, 10), (8, 10, 10, 8), (10, 8, 10, 2), (10, 2, 8, 0), (8, 0, 2, 0), (2, 0, 0, 2), (0, 2, 0, 8), (0, 8, 2, 10)],
        "h": [(0, 0, 0, 14), (0, 8, 2, 10), (2, 10, 8, 10), (8, 10, 10, 8), (10, 8, 10, 0)],
        "i": [(5, 10, 5, 0)],
        "j": [(6, 10, 6, -3), (6, -3, 4, -5), (4, -5, 1, -5)],
        "k": [(0, 0, 0, 14), (9, 10, 0, 4), (3, 5, 10, 0)],
        "l": [(4, 14, 4, 1), (4, 1, 6, 0)],
        "m": [(0, 0, 0, 10), (0, 8, 2, 10), (2, 10, 5, 8), (5, 8, 5, 0), (5, 8, 7, 10), (7, 10, 10, 8), (10, 8, 10, 0)],
        "n": [(0, 0, 0, 10), (0, 8, 2, 10), (2, 10, 8, 10), (8, 10, 10, 8), (10, 8, 10, 0)],
        "o": [(2, 0, 8, 0), (8, 0, 10, 2), (10, 2, 10, 8), (10, 8, 8, 10), (8, 10, 2, 10), (2, 10, 0, 8), (0, 8, 0, 2), (0, 2, 2, 0)],
        "p": [(0, -5, 0, 10), (0, 9, 2, 10), (2, 10, 8, 10), (8, 10, 10, 8), (10, 8, 10, 2), (10, 2, 8, 0), (8, 0, 2, 0), (2, 0, 0, 1)],
        "q": [(10, -5, 10, 10), (10, 9, 8, 10), (8, 10, 2, 10), (2, 10, 0, 8), (0, 8, 0, 2), (0, 2, 2, 0), (2, 0, 8, 0), (8, 0, 10, 1)],
        "r": [(0, 0, 0, 10), (0, 7, 3, 10), (3, 10, 9, 10)],
        "s": [(10, 9, 8, 10), (8, 10, 2, 10), (2, 10, 0, 8), (0, 8, 2, 6), (2, 6, 8, 4), (8, 4, 10, 2), (10, 2, 8, 0), (8, 0, 1, 0)],
        "t": [(4, 13, 4, 2), (4, 2, 6, 0), (6, 0, 9, 0), (1, 9, 8, 9)],
        "u": [(0, 10, 0, 2), (0, 2, 2, 0), (2, 0, 8, 0), (8, 0, 10, 2), (10, 10, 10, 0)],
        "v": [(0, 10, 4, 0), (10, 10, 6, 0), (4, 0, 6, 0)],
        "w": [(0, 10, 1, 0), (1, 0, 5, 4), (5, 4, 9, 0), (9, 0, 10, 10)],
        "x": [(0, 10, 10, 0), (10, 10, 0, 0)],
        "y": [(0, 10, 5, 0), (10, 10, 5, 0), (5, 0, 2, -5)],
        "z": [(0, 10, 10, 10), (10, 10, 0, 0), (0, 0, 10, 0)],
    }

    digits = {
        "0": uppercase["O"] + [(3, 3, 7, 11)],
        "1": [(5, 14, 5, 0), (3, 12, 5, 14), (2, 0, 8, 0)],
        "2": uppercase["Z"][:-1] + [(0, 0, 10, 0), (0, 11, 2, 14), (2, 14, 8, 14), (8, 14, 10, 12)],
        "3": [(0, 14, 9, 14), (9, 14, 10, 12), (10, 12, 10, 8), (10, 8, 8, 7), (4, 7, 9, 7), (9, 7, 10, 5), (10, 5, 10, 2), (10, 2, 8, 0), (8, 0, 0, 0)],
        "4": [(8, 0, 8, 14), (0, 5, 10, 5), (0, 5, 8, 14)],
        "5": uppercase["S"][:],
        "6": [(10, 13, 8, 14), (8, 14, 2, 14), (2, 14, 0, 11), (0, 11, 0, 2), (0, 2, 2, 0), (2, 0, 8, 0), (8, 0, 10, 2), (10, 2, 10, 5), (10, 5, 8, 7), (8, 7, 0, 7)],
        "7": [(0, 14, 10, 14), (10, 14, 3, 0)],
        "8": uppercase["O"] + [(2, 7, 8, 7)],
        "9": [(10, 2, 8, 0), (8, 0, 2, 0), (2, 0, 0, 2), (0, 2, 0, 5), (0, 5, 2, 7), (2, 7, 10, 7), (10, 7, 10, 12), (10, 12, 8, 14), (8, 14, 2, 14), (2, 14, 0, 12)],
    }

    if ch in uppercase:
        for seg in uppercase[ch]:
            line(*seg)
        return pen.glyph()
    if ch in lowercase:
        for seg in lowercase[ch]:
            line(*seg, lower=True)
        if ch == "i":
            dot(pen, sx(5), sy(13, True), s * 0.82)
        elif ch == "j":
            dot(pen, sx(6), sy(13, True), s * 0.82)
        return pen.glyph()
    if ch in digits:
        for seg in digits[ch]:
            line(*seg)
        return pen.glyph()

    if ch == ".":
        dot(pen, mid, 34, s * 0.9)
    elif ch == ",":
        dot(pen, mid, 62, s * 0.9)
        stroke(pen, mid + 8, 28, mid - 32, -80, s * 0.5)
    elif ch == ":":
        dot(pen, mid, 180, s * 0.78)
        dot(pen, mid, 470, s * 0.78)
    elif ch == ";":
        dot(pen, mid, 470, s * 0.78)
        dot(pen, mid, 180, s * 0.78)
        stroke(pen, mid + 8, 146, mid - 32, 40, s * 0.5)
    elif ch == "-":
        stroke(pen, sx(1.5), sy(7, False), sx(8.5), sy(7, False), s)
    elif ch == "_":
        stroke(pen, sx(0), -70, sx(10), -70, s)
    elif ch == "=":
        stroke(pen, sx(1), sy(8, False), sx(9), sy(8, False), s * 0.85)
        stroke(pen, sx(1), sy(5, False), sx(9), sy(5, False), s * 0.85)
    elif ch == "+":
        stroke(pen, sx(1), sy(7, False), sx(9), sy(7, False), s * 0.85)
        stroke(pen, sx(5), sy(3, False), sx(5), sy(11, False), s * 0.85)
    elif ch == "/":
        line(10, 14, 0, 0)
    elif ch == "\\":
        line(0, 14, 10, 0)
    elif ch == "|":
        stroke(pen, mid, DESCENT * 0.35, mid, ASCENT * 0.9, s * 0.72)
    elif ch == "!":
        stroke(pen, mid, 170, mid, CAP, s)
        dot(pen, mid, 34, s * 0.9)
    elif ch == "?":
        for seg in [(1, 12, 3, 14), (3, 14, 7, 14), (7, 14, 9, 12), (9, 12, 9, 10), (9, 10, 5, 7), (5, 7, 5, 5)]:
            line(*seg)
        dot(pen, mid, 34, s * 0.9)
    elif ch in "()[]{}<>":
        pairs = {
            "(": [(7, 14, 3, 10), (3, 10, 3, 4), (3, 4, 7, 0)],
            ")": [(3, 14, 7, 10), (7, 10, 7, 4), (7, 4, 3, 0)],
            "[": [(7, 14, 3, 14), (3, 14, 3, 0), (3, 0, 7, 0)],
            "]": [(3, 14, 7, 14), (7, 14, 7, 0), (7, 0, 3, 0)],
            "{": [(7, 14, 4, 12), (4, 12, 4, 8), (4, 8, 2, 7), (2, 7, 4, 6), (4, 6, 4, 2), (4, 2, 7, 0)],
            "}": [(3, 14, 6, 12), (6, 12, 6, 8), (6, 8, 8, 7), (8, 7, 6, 6), (6, 6, 6, 2), (6, 2, 3, 0)],
            "<": [(8, 14, 2, 7), (2, 7, 8, 0)],
            ">": [(2, 14, 8, 7), (8, 7, 2, 0)],
        }
        for seg in pairs[ch]:
            line(*seg)
    elif ch in ('"', "'", "`"):
        if ch == '"':
            stroke(pen, sx(3), sy(14, False), sx(3), sy(11, False), s * 0.7)
            stroke(pen, sx(7), sy(14, False), sx(7), sy(11, False), s * 0.7)
        elif ch == "'":
            stroke(pen, mid, sy(14, False), mid, sy(11, False), s * 0.7)
        else:
            line(3, 14, 5, 12)
    elif ch == "#":
        for seg in [(3, 14, 2, 0), (8, 14, 7, 0), (0, 9, 10, 9), (0, 5, 10, 5)]:
            line(*seg, width=s * 0.75)
    elif ch == "$":
        for seg in uppercase["S"]:
            line(*seg, width=s * 0.85)
        stroke(pen, mid, -45, mid, CAP + 45, s * 0.6)
    elif ch == "%":
        bowl(0, 9, 4, 14)
        bowl(6, 0, 10, 5)
        line(10, 14, 0, 0, width=s * 0.75)
    elif ch == "&":
        for seg in [(7, 14, 3, 14), (3, 14, 1, 12), (1, 12, 1, 10), (1, 10, 10, 0), (3, 7, 0, 4), (0, 4, 0, 2), (0, 2, 2, 0), (2, 0, 7, 0), (7, 0, 10, 3)]:
            line(*seg)
    elif ch == "*":
        for seg in [(5, 12, 5, 2), (1, 10, 9, 4), (9, 10, 1, 4)]:
            line(*seg, width=s * 0.8)
    elif ch == "@":
        for seg in uppercase["O"]:
            line(*seg, width=s * 0.85)
        for seg in [(7, 3, 4, 3), (4, 3, 3, 5), (3, 5, 3, 8), (3, 8, 5, 10), (5, 10, 8, 10), (8, 10, 8, 3), (8, 3, 10, 3)]:
            line(*seg, width=s * 0.75)
    elif ch == "^":
        line(2, 9, 5, 14)
        line(5, 14, 8, 9)
    elif ch == "~":
        line(1, 6, 3, 8, width=s * 0.75)
        line(3, 8, 7, 6, width=s * 0.75)
        line(7, 6, 9, 8, width=s * 0.75)
    else:
        return None
    return pen.glyph()


def draw_ascii_glyph(ch: str, cut: Cut):
    pen = TTGlyphPen(None)
    w = cut.width
    s = cut.stroke
    left = cut.side
    right = w - cut.side
    mid = w / 2

    if ch in (" ", "\u00a0"):
        return empty_glyph()
    trace_glyph = draw_trace_glyph(ch, cut)
    if trace_glyph is not None:
        return trace_glyph
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
