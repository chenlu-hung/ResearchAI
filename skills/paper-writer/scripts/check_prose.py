#!/usr/bin/env python3
"""Deterministic prose-format lint for paper sections — the mechanical subset
of shared/prompts/prose_hygiene.md (§A phrases, §C rhythm, §F list budget).

Per .tex/.md file it reports:

  BLOCKING (exit 1)
    * list environments over budget (§F: bullets only in conventional slots)
    * list-word ratio over budget (bullet-shaped section)
    * pseudo-list runs: ≥3 consecutive short \\paragraph{...} or bold-label blocks
    * heading fragmentation (subsection-level heads per 1000 words)
    * §A banned phrases ("delve", "crucial", "it is worth noting", ...)
    * em-dash rate over §A budget (≈2 per page)

  warnings (exit 0 — judgment calls for the LLM hygiene pass)
    * conditional §A words ("significantly", "leverage", "novel", ...)
    * §B structural patterns (binary contrast, false agency, rhetorical setups)
    * wrap-up closers ("In summary, ...")
    * §C rhythm: uniform paragraph lengths, punchy-ending runs, same-opener runs

Comments, math, and non-prose environments (equations, algorithms, tables,
figures, verbatim) are excluded. \\input/\\include are followed recursively.
This script cannot judge §F slot legitimacy (e.g. Intro contribution bullets)
or §E exceptions — the caller waives findings explicitly, naming the slot.

Usage:
    python3 check_prose.py paper/sections/03-method.tex [more files ...]
        [--max-lists 1] [--max-list-ratio 0.20] [--max-heading-density 5.0]
        [--max-emdash-rate 4.0] [--json]

Exit codes: 0 = clean, 1 = blocking findings, 2 = usage error. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

COMMENT_RE = re.compile(r"(?<!\\)%.*")
INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]*)\}")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’-]*")
HEAD_RE = re.compile(r"\\(section|subsection|subsubsection|paragraph)\*?\s*\{([^}]*)\}")
LIST_TOKEN_RE = re.compile(r"\\(begin|end)\{(itemize|enumerate|description)\}")
EMDASH_TEX_RE = re.compile(r"(?<!-)---(?!-)|—")
EMDASH_MD_RE = re.compile(r"—")
MD_LIST_LINE_RE = re.compile(r"^\s{0,3}(?:[-*+]|\d+[.)])\s+")
MD_HEAD_RE = re.compile(r"^(#{2,6})\s")

NONPROSE_ENVS = [
    "equation", "align", "gather", "multline", "eqnarray", "array",
    "displaymath", "algorithm", "algorithmic", "algorithm2e", "lstlisting",
    "verbatim", "Verbatim", "minted", "tabular", "tabularx", "table",
    "figure", "tikzpicture",
]

# §A phrases banned outright (no stated exception) — blocking.
BLOCKING_PHRASES = [
    ("it is worth noting", r"it\s+is\s+worth\s+not(?:ing|ed)"),
    ("it should be noted", r"it\s+should\s+be\s+noted"),
    ("it is important to note", r"it\s+is\s+important\s+to\s+(?:note|understand)"),
    ("in this section we will", r"in\s+this\s+section,?\s+we\s+(?:will|shall)"),
    ("delve", r"\bdelv(?:e|es|ed|ing)\b"),
    ("crucial", r"\bcrucial(?:ly)?\b"),
    ("pivotal", r"\bpivotal\b"),
    ("tapestry", r"\btapestry\b"),
    ("realm", r"\brealms?\b"),
    ("intricate", r"\bintricat(?:e|ely)\b|\bintricacies\b"),
    ("seamless", r"\bseamless(?:ly)?\b"),
    ("holistic", r"\bholistic(?:ally)?\b"),
    ("to the best of our knowledge", r"to\s+the\s+best\s+of\s+our\s+knowledge"),
    ("we believe/feel", r"\bwe\s+(?:believe|feel)\b"),
]

# §A/§D words with legitimate uses — warnings for the LLM pass to judge.
WARNING_PHRASES = [
    ("significantly (state test/CI or cut)", r"\bsignificantly\b"),
    ("substantially (give the number)", r"\bsubstantially\b"),
    ("notably", r"\bnotably\b"),
    ("importantly", r"\bimportantly\b"),
    ("interestingly", r"\binterestingly\b"),
    ("arguably", r"\barguably\b"),
    ("remarkably", r"\bremarkably\b"),
    ("highly/extremely", r"\b(?:highly|extremely)\b"),
    ("leverage (verb → use/exploit)", r"\bleverag(?:e|es|ed|ing)\b"),
    ("harness", r"\bharness(?:es|ed|ing)?\b"),
    ("showcase", r"\bshowcas(?:e|es|ed|ing)\b"),
    ("underscore", r"\bunderscor(?:e|es|ed|ing)\b"),
    ("robustly (unless a robustness claim)", r"\brobustly\b"),
    ("novel (scope it: relative to what?)", r"\bnovel\b"),
]

# §B structural patterns — regexable subset, warnings.
STRUCTURAL_PATTERNS = [
    ("binary contrast: not because X but because Y",
     r"\bnot\s+because\b[^.\n]{0,100}\bbut\s+because\b"),
    ("binary contrast: not just/only X but Y",
     r"\bnot\s+(?:just|only|merely|simply)\b[^.\n]{0,100}\bbut\b"),
    ("telegraphed reversal: is not X; it is Y",
     r"\bis\s+not\b[^.;\n]{0,80}[;.]\s*it\s+is\b"),
    ("false agency (name the actor + number)",
     r"\bthe\s+(?:data|results?|ablations?|numbers|experiments?|figures?|tables?)\s+"
     r"(?:reveal|tell|speak|paint)s?\b"),
    ("rhetorical setup",
     r"here'?s\s+the\s+key|the\s+key\s+insight\s+is|what\s+makes\s+this\s+work"
     r"|what\s+if\s+we\s+could"),
]

CLOSER_RE = re.compile(
    r"^(?:in\s+summary|in\s+conclusion|to\s+summarize|overall,|taken\s+together)",
    re.IGNORECASE)
BOLD_LABEL_RE = re.compile(r"^\s*(?:\\textbf\{[^}]{1,60}\}|\*\*[^*]{1,60}\*\*)\s*[:.]?\s")

ABBREVIATIONS = [
    "e.g.", "i.e.", "et al.", "cf.", "vs.", "resp.", "w.r.t.", "a.s.", "i.i.d.",
    "Fig.", "Eq.", "Sec.", "Tab.", "Thm.", "Cor.", "Lem.", "Prop.", "App.",
    "Alg.", "No.", "Ch.", "Def.",
]


def blank_keep_newlines(match: re.Match) -> str:
    return "\n" * match.group(0).count("\n")


def strip_comments(tex: str) -> str:
    return "\n".join(COMMENT_RE.sub("", line) for line in tex.splitlines())


def blank_envs(text: str) -> str:
    for env in NONPROSE_ENVS:
        pat = re.compile(
            r"\\begin\{" + env + r"\*?\}.*?\\end\{" + env + r"\*?\}", re.DOTALL)
        text = pat.sub(blank_keep_newlines, text)
    return text


def blank_math(text: str) -> str:
    def repl(m: re.Match) -> str:
        return " MATH " + "\n" * m.group(0).count("\n")
    text = re.sub(r"(?<!\\)\$\$.*?(?<!\\)\$\$", repl, text, flags=re.DOTALL)
    text = re.sub(r"(?<!\\)\$[^$]*?(?<!\\)\$", " MATH ", text)
    text = re.sub(r"\\\[.*?\\\]", repl, text, flags=re.DOTALL)
    text = re.sub(r"\\\(.*?\\\)", " MATH ", text, flags=re.DOTALL)
    return text


def strip_commands(s: str) -> str:
    s = re.sub(r"\\(?:no)?[cC]ite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{[^}]*\}", " CITEKEY ", s)
    s = re.sub(r"\\(?:[cC]ref|ref|eqref|autoref|pageref|vref)\*?\{[^}]*\}", " REFKEY ", s)
    s = re.sub(r"\\(?:label|url|href)\{[^}]*\}", " ", s)
    s = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?", " ", s)
    return s.replace("{", " ").replace("}", " ").replace("~", " ")


def count_words(s: str) -> int:
    return len(WORD_RE.findall(strip_commands(s)))


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def extract_list_spans(text: str) -> list[tuple[int, int]]:
    """Top-level itemize/enumerate/description spans (nested lists absorbed)."""
    spans, depth, start = [], 0, 0
    for m in LIST_TOKEN_RE.finditer(text):
        if m.group(1) == "begin":
            if depth == 0:
                start = m.start()
            depth += 1
        elif depth > 0:
            depth -= 1
            if depth == 0:
                spans.append((start, m.end()))
    if depth > 0:
        spans.append((start, len(text)))
    return spans


def blank_spans(text: str, spans: list[tuple[int, int]]) -> str:
    out = []
    last = 0
    for a, b in spans:
        out.append(text[last:a])
        out.append("\n" * text.count("\n", a, b))
        last = b
    out.append(text[last:])
    return "".join(out)


def build_paragraphs(text: str) -> list[tuple[int, str]]:
    paras: list[tuple[int, str]] = []
    cur: list[str] = []
    cur_start = 0
    for i, line in enumerate(text.splitlines(), 1):
        if line.strip():
            if not cur:
                cur_start = i
            cur.append(line.strip())
        elif cur:
            paras.append((cur_start, " ".join(cur)))
            cur = []
    if cur:
        paras.append((cur_start, " ".join(cur)))
    return paras


def split_sentences(s: str) -> list[str]:
    t = s
    for a in ABBREVIATIONS:
        t = t.replace(a, a.replace(".", "․"))
        t = t.replace(a.lower(), a.lower().replace(".", "․"))
    parts = re.split(r"(?<=[.!?])\s+", t)
    return [p.replace("․", ".") for p in parts if p.strip()]


def maximal_runs(flags: list[bool], min_len: int = 3) -> list[tuple[int, int]]:
    """(start_index, length) of maximal True-runs of length ≥ min_len."""
    runs, i = [], 0
    while i < len(flags):
        if flags[i]:
            j = i
            while j + 1 < len(flags) and flags[j + 1]:
                j += 1
            if j - i + 1 >= min_len:
                runs.append((i, j - i + 1))
            i = j + 1
        else:
            i += 1
    return runs


def uniform_length_runs(words: list[int], min_len: int = 3, tol: float = 0.15,
                        min_words: int = 40) -> list[tuple[int, int]]:
    runs, i, n = [], 0, len(words)
    while i <= n - min_len:
        best_end = -1
        for k in range(i + min_len - 1, n):
            window = words[i:k + 1]
            if any(w < min_words for w in window):
                break
            mean = sum(window) / len(window)
            if all(abs(w - mean) <= tol * mean for w in window):
                best_end = k
            else:
                break
        if best_end >= 0:
            runs.append((i, best_end - i + 1))
            i = best_end + 1
        else:
            i += 1
    return runs


def snippet(plain: str, match: re.Match, radius: int = 24) -> str:
    a = max(0, match.start() - radius)
    b = min(len(plain), match.end() + radius)
    return re.sub(r"\s+", " ", plain[a:b]).strip()


def scan_phrases(paras: list[tuple[int, str]]) -> tuple[list[dict], list[dict]]:
    blocking, warnings = [], []
    tables = [(BLOCKING_PHRASES, blocking), (WARNING_PHRASES, warnings),
              (STRUCTURAL_PATTERNS, warnings)]
    for start_line, raw in paras:
        plain = re.sub(r"\s+", " ", strip_commands(raw))
        for table, sink in tables:
            for label, pat in table:
                for m in re.finditer(pat, plain, re.IGNORECASE):
                    sink.append({"line": start_line, "tell": label,
                                 "context": snippet(plain, m)})
        if CLOSER_RE.match(plain):
            warnings.append({"line": start_line, "tell": "wrap-up closer",
                             "context": plain[:60]})
    return blocking, warnings


def paragraph_head_runs(text: str) -> list[dict]:
    """Runs of ≥3 \\paragraph heads with <90 prose words between consecutive heads."""
    heads = [(m.group(1), m.start()) for m in HEAD_RE.finditer(text)]
    runs, chain = [], []
    for idx, (kind, pos) in enumerate(heads):
        if kind != "paragraph":
            chain = []
            continue
        if chain:
            gap = count_words(text[chain[-1]:pos])
            if gap >= 90:
                chain = []
        chain.append(pos)
        nxt = heads[idx + 1][1] if idx + 1 < len(heads) else len(text)
        if len(chain) >= 3 and count_words(text[pos:nxt]) < 90:
            if not runs or runs[-1]["start_pos"] != chain[0]:
                runs.append({"start_pos": chain[0], "length": len(chain)})
            else:
                runs[-1]["length"] = len(chain)
    for r in runs:
        r["line"] = line_of(text, r.pop("start_pos"))
        r["kind"] = "\\paragraph run"
    return runs


def analyze_tex(text: str) -> dict:
    text = blank_math(blank_envs(strip_comments(text)))
    list_spans = extract_list_spans(text)
    list_words = sum(count_words(text[a:b]) for a, b in list_spans)
    list_lines = [line_of(text, a) for a, b in list_spans]

    pseudo_runs = paragraph_head_runs(text)
    subheads = [m for m in HEAD_RE.finditer(text)
                if m.group(1) in ("subsection", "subsubsection", "paragraph")]

    phrase_paras = build_paragraphs(text)
    prose_text = blank_spans(text, list_spans)
    prose_text = HEAD_RE.sub(blank_keep_newlines, prose_text)
    paras = [(ln, p) for ln, p in build_paragraphs(prose_text) if count_words(p) >= 5]
    emdashes = len(EMDASH_TEX_RE.findall(prose_text))
    return {
        "phrase_paras": phrase_paras, "paras": paras,
        "list_count": len(list_spans), "list_words": list_words,
        "list_lines": list_lines, "pseudo_runs": pseudo_runs,
        "subhead_count": len(subheads), "emdashes": emdashes,
    }


def analyze_md(text: str) -> dict:
    text = re.sub(r"```.*?```", blank_keep_newlines, text, flags=re.DOTALL)
    if text.startswith("---"):
        text = re.sub(r"\A---\n.*?\n---", blank_keep_newlines, text, flags=re.DOTALL)
    text = blank_math(text)

    lines = text.splitlines()
    list_count, list_words, list_lines, subhead_count = 0, 0, [], 0
    prose_lines: list[str] = []
    in_list = False
    for i, line in enumerate(lines, 1):
        if MD_LIST_LINE_RE.match(line) or (in_list and re.match(r"^\s{2,}\S", line)):
            if not in_list:
                list_count += 1
                list_lines.append(i)
            in_list = True
            list_words += len(WORD_RE.findall(line))
            prose_lines.append("")
        else:
            in_list = False
            if MD_HEAD_RE.match(line):
                subhead_count += 1
                prose_lines.append("")
            else:
                prose_lines.append(line)
    prose_text = "\n".join(prose_lines)
    phrase_paras = build_paragraphs(re.sub(r"^#{1,6}\s.*$", "", text, flags=re.MULTILINE))
    paras = [(ln, p) for ln, p in build_paragraphs(prose_text) if count_words(p) >= 5]
    return {
        "phrase_paras": phrase_paras, "paras": paras,
        "list_count": list_count, "list_words": list_words,
        "list_lines": list_lines, "pseudo_runs": [],
        "subhead_count": subhead_count,
        "emdashes": len(EMDASH_MD_RE.findall(prose_text)),
    }


def check_file(path: Path, args: argparse.Namespace) -> dict:
    raw = path.read_text(encoding="utf-8", errors="replace")
    a = analyze_md(raw) if path.suffix.lower() in (".md", ".markdown", ".txt") \
        else analyze_tex(raw)

    paras = a["paras"]
    prose_words = sum(count_words(p) for _, p in paras)
    total_words = prose_words + a["list_words"]
    report: dict = {"words": total_words, "blocking": {}, "warnings": {}}
    if total_words < 30:
        report["skipped"] = "under 30 words of prose"
        return report

    blocking, warnings = report["blocking"], report["warnings"]

    if a["list_count"] > args.max_lists:
        blocking["lists_over_budget"] = {
            "count": a["list_count"], "max": args.max_lists, "lines": a["list_lines"]}
    ratio = a["list_words"] / total_words if total_words else 0.0
    if total_words >= 120 and ratio > args.max_list_ratio:
        blocking["list_word_ratio"] = {
            "ratio": round(ratio, 2), "max": args.max_list_ratio}

    bold_flags = [bool(BOLD_LABEL_RE.match(p)) and count_words(p) < 90
                  for _, p in a["phrase_paras"]]
    pseudo = list(a["pseudo_runs"])
    pseudo += [{"line": a["phrase_paras"][i][0], "length": n, "kind": "bold-label run"}
               for i, n in maximal_runs(bold_flags)]
    if pseudo:
        blocking["pseudo_list_runs"] = pseudo

    if total_words >= 300:
        density = a["subhead_count"] * 1000.0 / total_words
        if density > args.max_heading_density:
            blocking["heading_fragmentation"] = {
                "per_1000_words": round(density, 1), "max": args.max_heading_density}

    if total_words >= 200 and a["emdashes"] >= 4:
        rate = a["emdashes"] * 1000.0 / total_words
        if rate > args.max_emdash_rate:
            blocking["emdash_rate"] = {
                "count": a["emdashes"], "per_1000_words": round(rate, 1),
                "max": args.max_emdash_rate}

    phrase_blocking, phrase_warnings = scan_phrases(a["phrase_paras"])
    if phrase_blocking:
        blocking["banned_phrases"] = phrase_blocking
    if phrase_warnings:
        warnings["phrases_and_patterns"] = phrase_warnings

    words = [count_words(p) for _, p in paras]
    runs = [{"line": paras[i][0], "paragraphs": n}
            for i, n in uniform_length_runs(words)]
    if runs:
        warnings["uniform_length_runs"] = runs

    punchy = [w >= 25 and len(WORD_RE.findall(split_sentences(strip_commands(p))[-1])) < 8
              for (_, p), w in zip(paras, words)]
    runs = [{"line": paras[i][0], "paragraphs": n} for i, n in maximal_runs(punchy)]
    if runs:
        warnings["punchy_ending_runs"] = runs

    openers = []
    for _, p in paras:
        m = WORD_RE.search(strip_commands(p))
        openers.append(m.group(0).lower() if m else "")
    same = [i > 0 and openers[i] and openers[i] not in ("citekey", "refkey", "math")
            and openers[i] == openers[i - 1] for i in range(len(openers))]
    runs = []
    for i, n in maximal_runs(same, min_len=2):  # n pairs = n+1 paragraphs
        runs.append({"line": paras[i - 1][0], "word": openers[i], "paragraphs": n + 1})
    if runs:
        warnings["same_opener_runs"] = runs

    return report


def gather_tex_files(seed: Path) -> list[Path]:
    """seed + recursively \\input/\\include'd .tex files."""
    files, stack, seen = [], [seed], set()
    while stack:
        f = stack.pop(0)
        key = str(f.resolve())
        if key in seen or not f.exists():
            continue
        seen.add(key)
        files.append(f)
        if f.suffix.lower() not in ("", ".tex"):
            continue
        text = strip_comments(f.read_text(encoding="utf-8", errors="replace"))
        for m in INPUT_RE.finditer(text):
            p = f.parent / m.group(1).strip()
            if p.suffix == "":
                p = p.with_suffix(".tex")
            stack.append(p)
    return files


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help=".tex (inputs followed) or .md files")
    ap.add_argument("--max-lists", type=int, default=1,
                    help="max list environments per file (default 1; §F slots)")
    ap.add_argument("--max-list-ratio", type=float, default=0.30,
                    help="max fraction of words inside lists (default 0.30; "
                         "a conventional intro-with-contributions sits ~0.2)")
    ap.add_argument("--max-heading-density", type=float, default=5.0,
                    help="max subsection-level heads per 1000 words (default 5)")
    ap.add_argument("--max-emdash-rate", type=float, default=4.0,
                    help="max em-dashes per 1000 words (default 4 ≈ 2/page)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    targets: list[Path] = []
    for name in args.files:
        p = Path(name)
        if not p.exists():
            print(f"error: {p} not found", file=sys.stderr)
            return 2
        if p.suffix.lower() in (".md", ".markdown", ".txt"):
            targets.append(p)
        else:
            targets.extend(gather_tex_files(p))
    unique: list[Path] = []
    seen: set[str] = set()
    for p in targets:
        if str(p.resolve()) not in seen:
            seen.add(str(p.resolve()))
            unique.append(p)

    results = {str(p): check_file(p, args) for p in unique}
    n_blocking = sum(len(r["blocking"]) for r in results.values())
    n_warnings = sum(len(r["warnings"]) for r in results.values())

    if args.json:
        print(json.dumps({"files": results, "blocking_findings": n_blocking,
                          "warning_kinds": n_warnings}, ensure_ascii=False, indent=2))
    else:
        for name, r in results.items():
            if "skipped" in r:
                print(f"== {name} — skipped ({r['skipped']})")
                continue
            print(f"== {name} ({r['words']} words)")
            for kind, findings in r["blocking"].items():
                print(f"  BLOCKING {kind}: {json.dumps(findings, ensure_ascii=False)}")
            for kind, findings in r["warnings"].items():
                print(f"  warning {kind}: {json.dumps(findings, ensure_ascii=False)}")
        tally = f"({n_blocking} blocking, {n_warnings} warning kinds, {len(results)} file(s))"
        print("RESULT: " + ("BLOCKING FINDINGS " + tally if n_blocking
                            else f"clean {tally}"))
    return 1 if n_blocking else 0


if __name__ == "__main__":
    sys.exit(main())
