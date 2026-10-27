#!/usr/bin/env bash
# Optional research mirror of the 19-band source, not organizer-authenticated.
# Large input is never committed. Requires curl, tar and sha256sum.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cache="${1:-$root/.cache/research}"
mkdir -p "$cache/inputs"
expected=4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5
out="$cache/inputs/training_features.tif"
if [[ -f "$out" ]] && echo "$expected  $out" | sha256sum -c --status; then
  echo "Verified feature mirror: $out"
  exit 0
fi
work="$(mktemp -d "$cache/inputs/.features.XXXXXXXX")"
trap 'rm -rf "$work"' EXIT
url="https://codeload.github.com/buffedlizard55-lab/GEMSDOE/tar.gz/c0c06ac82178f26b94fce3397036ef8f12a2f3a0"
curl --fail --location --silent --show-error --max-time 900 "$url" | \
  tar --extract --gzip --directory "$work" --strip-components=3 --no-same-owner --no-same-permissions \
      --wildcards '*/data/bridge/gems-geodawn-numerical-features.tif.part-*'
for part in 000 001 002 003 004; do
  test -f "$work/gems-geodawn-numerical-features.tif.part-$part"
done
cat "$work"/gems-geodawn-numerical-features.tif.part-{000,001,002,003,004} > "$work/training_features.tif"
echo "$expected  $work/training_features.tif" | sha256sum -c
mv -f "$work/training_features.tif" "$out"
echo "Research mirror ready at $out. It is not an authenticated competition download."
