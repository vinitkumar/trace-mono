# Trace Mono 1.0.1

Corrected stable release of Trace Mono.

This release supersedes `v1.0.0`. The `v1.0.0` TTFs were generated from a
hand-rolled outline script and did not meet the quality bar for a real terminal
font. `v1.0.1` rebuilds Trace Mono as an Iosevka-derived custom family using
the checked-in build plan in `sources/iosevka-private-build-plans.toml`.

Do not use `v1.0.0`.

## Included Fonts

- Trace Mono Console Regular
- Trace Mono Console Bold
- Trace Mono Inspect Regular
- Trace Mono Inspect Bold

## Install

macOS and Linux:

```sh
./install.sh
```

Windows PowerShell:

```powershell
.\install.ps1
```

## Verification

This release was built and checked with:

```sh
python3 tools/validate.py
```
