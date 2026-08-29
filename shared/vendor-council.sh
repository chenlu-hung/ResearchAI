#!/bin/sh
# Re-vendor shared/council.py from its upstream in the my-skills repo.
#
# The plugin has to ship this engine rather than link it: it is installed to a
# machine where my-skills does not exist. That makes it a vendored copy, and a
# vendored copy that gets edited in place is how this file fell nine months
# behind upstream once already. So: change council.py upstream, run this, commit
# the result. Never edit shared/council.py directly.
#
# Plugin-specific usage lives in shared/prompts/council_panel.md and README.md,
# not in the vendored file, so that this stays a byte-for-byte copy plus a header.
set -eu

UPSTREAM="${COUNCIL_UPSTREAM:-$HOME/Documents/Projects/my-skills/llm-council/council.py}"
HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="$HERE/council.py"

if [ ! -f "$UPSTREAM" ]; then
    echo "upstream not found: $UPSTREAM" >&2
    echo "set COUNCIL_UPSTREAM to the my-skills checkout" >&2
    exit 1
fi

# The schema ships with the engine: structured output is on by default and the
# script refuses to start when its default schema file is missing.
UPSTREAM_SCHEMA="$(dirname "$UPSTREAM")/schema/answer.schema.json"
if [ ! -f "$UPSTREAM_SCHEMA" ]; then
    echo "upstream schema not found: $UPSTREAM_SCHEMA" >&2
    exit 1
fi
mkdir -p "$HERE/schema"
cp "$UPSTREAM_SCHEMA" "$HERE/schema/answer.schema.json"

{
    head -n 1 "$UPSTREAM"   # shebang has to stay first
    cat <<'HEADER'
# VENDORED — do not edit here. Upstream: my-skills/llm-council/council.py
# Re-sync with: shared/vendor-council.sh   Plugin usage: shared/prompts/council_panel.md
HEADER
    tail -n +2 "$UPSTREAM"
} > "$DEST"

chmod +x "$DEST"
echo "vendored $(wc -l < "$DEST" | tr -d ' ') lines + schema/answer.schema.json <- $UPSTREAM"
