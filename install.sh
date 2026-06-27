#!/usr/bin/env sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
font_dir="$repo_dir/fonts/ttf"

if [ ! -d "$font_dir" ]; then
  echo "Trace Mono fonts not found at: $font_dir" >&2
  exit 1
fi

case "$(uname -s)" in
  Darwin)
    os_name="macos"
    target_dir="${HOME}/Library/Fonts"
    ;;
  Linux)
    os_name="linux"
    target_dir="${XDG_DATA_HOME:-${HOME}/.local/share}/fonts/trace-mono"
    ;;
  *)
    echo "Unsupported OS for install.sh. Use install.ps1 on Windows." >&2
    exit 1
    ;;
esac

mkdir -p "$target_dir"

count=0
for font in "$font_dir"/*.ttf; do
  [ -e "$font" ] || continue
  cp "$font" "$target_dir/"
  count=$((count + 1))
  echo "Installed $(basename "$font") -> $target_dir"
done

if [ "$count" -eq 0 ]; then
  echo "No .ttf files found in: $font_dir" >&2
  exit 1
fi

if [ "$os_name" = "linux" ] && command -v fc-cache >/dev/null 2>&1; then
  fc-cache -f "$target_dir" >/dev/null
  echo "Refreshed fontconfig cache."
fi

echo "Trace Mono installed. Select 'Trace Mono Console' or 'Trace Mono Inspect' in your terminal."
