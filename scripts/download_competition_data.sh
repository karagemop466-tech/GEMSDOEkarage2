#!/usr/bin/env bash
# Competition data is authenticated on DrivenData. This script cannot log in,
# accept rules, or turn public owner mirrors into organizer-authenticated inputs.
# It will NEVER report download success when only a URL/instructions were printed.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON=python3
fi

case "${1:-}" in
  --research-mirror)
    if [[ $# -ne 1 ]]; then echo 'One flag only.' >&2; exit 2; fi
    echo 'Restoring SHA-pinned public OWNER MIRRORS into ignored .cache; not official files.'
    "$PYTHON" "$ROOT/scripts/restore_data.py" --group core \
      --target-dir "$ROOT/.cache/competition_data"
    "$PYTHON" "$ROOT/scripts/prepare_data.py" \
      --data-dir "$ROOT/.cache/competition_data" --core-only \
      --mirror-manifest "$ROOT/registry/core_data_manifest.json"
    echo 'Core research-byte checks passed. Submission authorization: NO.'
    ;;
  --validate-official)
    if [[ $# -ne 1 ]]; then echo 'One flag only.' >&2; exit 2; fi
    echo 'Checking data/ files only. This script cannot authenticate their origin.'
    "$PYTHON" "$ROOT/scripts/prepare_data.py" --data-dir "$ROOT/data"
    echo 'Schema checked. Organizer identity, scientific gates and portal acceptance remain unresolved.'
    ;;
  *)
    cat >&2 <<'EOF'
No anonymous DrivenData data download is available from this sandbox.
Data tab (participant authentication required):
  https://www.drivendata.org/competitions/306/competition-doe-gems/data/

For automatic, hash-verified RESEARCH-ONLY owner mirrors (not competition auth):
  bash scripts/download_competition_data.sh --research-mirror

For files already obtained from the organizer in data/:
  bash scripts/download_competition_data.sh --validate-official

Neither option trains a model, generates a submission, authenticates the file's
origin, clears the literal registry stop, or spends a weekly submission slot.
EOF
    exit 2
    ;;
esac
