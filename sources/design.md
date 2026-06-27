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

- Squared counters for repeatable terminal rhythm.
- Short angular terminals to keep small sizes crisp.
- Large punctuation with consistent optical centers.
- Narrow but unmistakable uppercase to keep severity labels readable.
- Digits are tall, open, and intentionally non-humanist.

## First Character Set

The initial build covers ASCII plus the most common terminal symbols:

- Basic Latin printable range.
- Tabular digits and punctuation for logs.
- Arrows used by shells and stack traces.
- Box-drawing primitives used by terminal UIs.
- Replacement glyph and non-breaking space.
