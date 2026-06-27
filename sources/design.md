# Trace Mono Design Notes

Trace Mono starts from log text instead of prose.

## Metrics

- Units per em: 1000
- Console advance width: 600
- Inspect advance width: 640
- Cap height: 720
- x-height: 500
- Ascender: 840
- Descender: -240

## Shape Language

- Pixel-outline construction for crisp terminal rendering.
- Squared counters for repeatable terminal rhythm.
- Large punctuation with consistent optical centers.
- Uppercase and lowercase share a compact scan-friendly rhythm.
- Digits are tall, open, and intentionally distinct.

## First Character Set

The initial build covers ASCII plus the most common terminal symbols:

- Basic Latin printable range.
- Tabular digits and punctuation for logs.
- Arrows used by shells and stack traces.
- Box-drawing primitives used by terminal UIs.
- Replacement glyph and non-breaking space.
