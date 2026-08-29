#!/bin/sh
# Re-vendor shared/council.py from the llm-council skill upstream.
#
# The plugin ships this engine rather than linking it: it installs onto machines
# where the upstream checkout does not exist. That makes it a vendored copy, and
# a vendored copy that gets edited in place is how this file fell to 221 lines
# against upstream's 568 once already. So: change council.py upstream, run this,
# commit the result. Never edit shared/council.py directly.
#
# Upstream is identified by URL, not by a path on anyone's disk -- where a
# contributor keeps their own checkout is not this script's business. Set
# COUNCIL_UPSTREAM to a local council.py to vendor uncommitted work instead.
#
#   ./vendor-council.sh                          # from the default branch
#   COUNCIL_REF=some-branch ./vendor-council.sh  # from another ref
#   COUNCIL_UPSTREAM=~/src/my-skills/llm-council/council.py ./vendor-council.sh
#
# Plugin-specific usage lives in shared/prompts/council_panel.md and README.md,
# not in the vendored file, so this stays a byte-for-byte copy plus a header.
set -eu

REPO="${COUNCIL_REPO:-chenlu-hung/my-skills}"
REF="${COUNCIL_REF:-main}"
BASE="https://raw.githubusercontent.com/$REPO/$REF/llm-council"

HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="$HERE/council.py"
SCHEMA_DEST="$HERE/schema/answer.schema.json"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# fetch <path relative to llm-council/> <dest>. COUNCIL_UPSTREAM points at a
# local council.py, so its directory is the same relative root as the URL base.
fetch() {
    if [ -n "${COUNCIL_UPSTREAM:-}" ]; then
        src="$(dirname "$COUNCIL_UPSTREAM")/$1"
        [ -f "$src" ] || { echo "not found: $src" >&2; exit 1; }
        cp "$src" "$2"
    else
        curl -fsSL "$BASE/$1" -o "$2" || { echo "could not fetch $BASE/$1" >&2; exit 1; }
    fi
}

fetch "council.py" "$TMP/council.py"
# The schema ships with the engine: structured output is on by default and the
# script refuses to start when its default schema file is missing.
fetch "schema/answer.schema.json" "$TMP/answer.schema.json"

# sanity-check before overwriting anything
head -n 1 "$TMP/council.py" | grep -q '^#!' || { echo "fetched file is not a script" >&2; exit 1; }
grep -q "^RUNNERS = " "$TMP/council.py" || { echo "fetched file has no RUNNERS table" >&2; exit 1; }
python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$TMP/answer.schema.json"

{
    head -n 1 "$TMP/council.py"   # shebang has to stay first
    if [ -n "${COUNCIL_UPSTREAM:-}" ]; then
        echo "# VENDORED — do not edit here. Upstream: llm-council/council.py (local checkout)"
    else
        echo "# VENDORED — do not edit here. Upstream: $REPO@$REF llm-council/council.py"
    fi
    echo "# Re-sync with: shared/vendor-council.sh   Plugin usage: shared/prompts/council_panel.md"
    tail -n +2 "$TMP/council.py"
} > "$DEST"

mkdir -p "$(dirname "$SCHEMA_DEST")"
cp "$TMP/answer.schema.json" "$SCHEMA_DEST"
chmod +x "$DEST"

echo "vendored $(wc -l < "$DEST" | tr -d ' ') lines + schema from ${COUNCIL_UPSTREAM:-$REPO@$REF}"
