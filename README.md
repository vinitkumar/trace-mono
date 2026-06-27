# Trace Mono

Trace Mono is an original monospace font family designed for consoles,
terminals, and long log-reading sessions.

The first cut focuses on the text that shows up constantly in logs:
timestamps, paths, JSON, stack traces, shell output, UUIDs, HTTP status codes,
and dense punctuation. It is intentionally plain, sharp, and functional.

## Design Goals

- Clear distinction between `0 O o`, `1 l I |`, `5 S`, `2 Z`, and `8 B`.
- Calm rhythm for timestamp-heavy text such as `2026-06-27T10:42:01.932Z`.
- Strong bracket and punctuation shapes for JSON, tracebacks, and shell logs.
- Original generated outlines, not a derivative of another font family.
- Reproducible source build using `fontTools`.

## Families

- `Trace Mono Console`: default terminal cut.
- `Trace Mono Inspect`: slightly roomier log-inspection cut.

## Build

```sh
python3 -m pip install -r requirements.txt
python3 tools/build.py
python3 tools/validate.py
python3 tools/render_terminal_screenshots.py
```

Generated fonts are written to `fonts/ttf/`.

## Terminal Screenshots

### Ghostty

![Trace Mono in Ghostty](images/ghostty-trace-mono.png)

Use the example config in `examples/ghostty.config`:

```ini
font-family = "Trace Mono Console"
font-size = 16
```

### Kitty

![Trace Mono in Kitty](images/kitty-trace-mono.png)

Use the example config in `examples/kitty.conf`:

```conf
font_family Trace Mono Console
font_size 16
```

The terminal sample text is in `tools/log-demo.sh`; the checked-in PNGs are
generated from the built TTF via `tools/render_terminal_screenshots.py`.

## Install Locally On macOS

```sh
cp fonts/ttf/*.ttf ~/Library/Fonts/
```

Then choose `Trace Mono Console` or `Trace Mono Inspect` in your terminal.

## Specimen

Open `specimen/index.html` after building. It uses the generated TTF files and
shows terminal/log-oriented samples.

## License

SIL Open Font License 1.1. See `OFL.txt`.
