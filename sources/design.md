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

- Conventional monoline construction, closer to the expectations set by
  well-known terminal fonts such as Menlo, SF Mono, JetBrains Mono, Berkeley
  Mono, and Iosevka.
- High x-height and open counters so lowercase words remain readable in dense
  logs.
- Wide, centered punctuation for timestamps, JSON, paths, and stack traces.
- Tabular digits with explicit differentiation between `0 O o`, `1 l I |`,
  `5 S`, `2 Z`, and `8 B`.
- Personality should come from small terminal-focused decisions, not novelty
  shapes.

## First Character Set

The initial build covers ASCII plus the most common terminal symbols:

- Basic Latin printable range.
- Tabular digits and punctuation for logs.
- Arrows used by shells and stack traces.
- Box-drawing primitives used by terminal UIs.
- Replacement glyph and non-breaking space.
