#!/usr/bin/env bash
# Compile gate + optional DOCX export for paper-writer drafts.
#
#   build_paper.sh compile [paper/main.tex]            # gate: must produce a PDF
#   build_paper.sh docx    [paper/main.tex] [out.docx] # LaTeX -> DOCX (co-authors)
#
# `compile` exits non-zero if the draft does not build — use it as the gate
# before declaring a draft done. `docx` is lossy (math/figures); for review only.
set -euo pipefail

cmd="${1:-compile}"
tex="${2:-paper/main.tex}"
dir="$(dirname "$tex")"
base="$(basename "${tex%.tex}")"

case "$cmd" in
  compile)
    if command -v latexmk >/dev/null 2>&1; then
      latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir="$dir" "$tex"
    elif command -v tectonic >/dev/null 2>&1; then
      tectonic "$tex"
    elif command -v pdflatex >/dev/null 2>&1; then
      ( cd "$dir" \
        && pdflatex -interaction=nonstopmode -halt-on-error "$base.tex" \
        && (bibtex "$base" || true) \
        && pdflatex -interaction=nonstopmode "$base.tex" \
        && pdflatex -interaction=nonstopmode "$base.tex" )
    else
      echo "no LaTeX engine (latexmk/tectonic/pdflatex) found" >&2; exit 1
    fi
    echo "OK: $dir/$base.pdf"
    ;;
  docx)
    out="${3:-$dir/$base.docx}"
    command -v pandoc >/dev/null 2>&1 || { echo "pandoc not found" >&2; exit 1; }
    bib="$(grep -oE '\\bibliography\{[^}]+\}' "$tex" | sed -E 's/.*\{([^}]+)\}.*/\1/' | head -1 || true)"
    args=(--from latex --to docx -o "$out")
    if [ -n "$bib" ] && [ -f "$dir/$bib.bib" ]; then
      args+=(--citeproc --bibliography "$dir/$bib.bib")
    fi
    pandoc "${args[@]}" "$tex"
    echo "OK: $out  (LaTeX->DOCX is lossy: verify math + figures)"
    ;;
  *)
    echo "usage: build_paper.sh {compile|docx} <main.tex> [out.docx]" >&2; exit 2
    ;;
esac
