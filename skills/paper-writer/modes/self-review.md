# Mode: self-review

**Purpose**: simulate one venue reviewer reading the *drafted manuscript* and
produce actionable comments. This is distinct from `algo-brainstorm`'s
`red-team`:

- `red-team` attacks whether the **method/claims are valid**.
- `self-review` attacks whether the **manuscript persuades this venue** —
  completeness, positioning, evidence, clarity. It assumes the method is sound.

Single pass, single reviewer persona **by default**. A real multi-reviewer panel is
available opt-in via `--council` (see "Council panel" below).

## Inputs

- Draft (`paper/main.tex` or section files) — required
- `venue_target` — required (sets the reviewer persona)
- Current method/protocol/result/evidence-audit/results-red-team gate artifacts
  and hashes (or valid audited theory-only N/A gates)

## Procedure

0. Follow `shared/prompts/research_lifecycle.md`. Recompute the draft hash and
   validate every upstream gate/artifact it claims against. Refuse a style-only
   review when method/result evidence is stale or missing.
1. Read the full draft and the venue's profile in `shared/venue_profiles.md`
   (reviewer profile + red-flag list) plus the matching `style/<venue>.md`.
   If research state has `reviewer_intel:`
   (`shared/prompts/reviewer_intel.md`), read the dossier too — its
   observed objections sharpen the persona and the red-flag walk.
2. Adopt the venue's **dominant** reviewer persona (e.g. NeurIPS → empirical
   reviewer; AoS → pure statistician).

   **Focus audit — do this before reading the rest of the paper.** Read *only*
   the abstract and introduction, then write, in one sentence and in your own
   words, what this paper's main contribution is. Only then open `spine:` in
   state and compare with the primary claim. A mismatch is a **major comment**:
   the paper argues something other than what it froze, which is the failure
   reviewers describe as "unclear contribution". Record both sentences verbatim
   side by side so the gap is visible; do not paraphrase them into agreement.
   Reading the whole paper first destroys this test — the ordering is the test.

3. Produce a review with these parts:
   - **Summary** (3–4 sentences, as a reviewer would write it): what the paper
     claims and does.
   - **Focus audit**: the one-sentence contribution read off abstract+intro, the
     spine's primary claim, and whether they match. Mismatch → major comment.
   - **Headline-term audit**: for each key term in the title and abstract (e.g.
     "operator", "cross-resolution", "invariance", "scalable"), list what a
     hostile reviewer takes it to *promise* — the formal content `formalize`
     recorded for it — and verify each promise is demonstrated or explicitly
     delimited in the paper. An undelivered promise is a major comment: an
     unearned headline term reads as overclaiming, and it is the cheapest
     objection for a reviewer to write. Ties into the focus audit above.
   - **Recommendation**: map to the venue scale (e.g. accept / weak accept /
     borderline / reject) with a one-line reason.
   - **Major comments**: substantive — unsupported claim, missing recent
     baseline, assumption not discussed, theory–experiment mismatch, novelty
     not delimited. Each tied to a section.
   - **Scientific integrity check**: bind every key method/theory/experiment
     claim to the method freeze, literature passage, audited result/proof
     artifact, and protocol decision rule. Check negative/failed runs, deviations,
     post-hoc analyses, uncertainty, and whether claim scope exceeds evidence.
   - **Minor comments**: clarity, notation, figure/table issues.
   - **AI-tell scan**: read as a reviewer alert to machine-written prose.
     Gather the mechanical evidence first — run `python3
     "$PLUGIN_ROOT/skills/paper-writer/scripts/check_prose.py" paper/main.tex`
     and fold
     its findings in (rule 4 of `execution_discipline.md`; paste the result
     line). Then flag any structural tells from
     `shared/prompts/prose_hygiene.md` §B (binary contrasts, false agency
     like "the data reveals", vague declaratives, dramatic fragmentation),
     §A filler, and §F format tells (bullet-shaped sections, pseudo-list
     `\paragraph` runs, outline residue), tied to a section/line. "Reads as
     LLM-generated" is a credibility hit reviewers act on — surface it so
     `revision` can fix it. Respect the academic exceptions (§E) and the §F
     allowed slots: do not flag conventional passive voice, technical
     adverbs, three-item lists, or Intro contribution bullets.
   - **Red-flag check**: go down the venue's `Common reviewer red flags` list
     and mark each present / absent / N/A.

## Council panel (opt-in)

The procedure above is one reviewer. When invoked with `--council`, convene a **real
panel**: each model plays an independent venue reviewer, then you chair a meta-review.
Follow `shared/prompts/council_panel.md`.

- **Panel prompt**: the full draft + the venue reviewer profile and red-flag list from
  `shared/venue_profiles.md`, asking each member for a review in the Step-3 format (summary,
  recommendation on the venue scale, major comments tied to sections, minor comments,
  red-flag check). Each member adopts the venue's dominant persona.
- **Cross-review (optional)**: have members react to the anonymized set of reviews to expose
  where reviewers disagree on severity.
- **Synthesis → meta-review**: merge into one review. Dedup overlapping comments and note
  agreement ("3/4 reviewers flag the missing baseline" → a major weakness); keep genuine
  disagreement explicit (split decision). Apply the Anti-sycophancy rule below to the
  *merged* review, and record each reviewer's recommendation alongside the aggregate.

## Anti-sycophancy

- Surface **≥3 concrete weaknesses**. "Strong paper, minor polish" is not a
  valid output for a draft.
- Every comment cites a section/line. No generic praise.
- Do not invent flaws either — if the draft genuinely covers a red flag, say so.

## Output

Write `.research-state/<slug>-scientific-review-<date>.md`, including draft,
method, protocol, result-manifest, evidence-audit, packet, and red-team hashes.
For backward compatibility, the body/state may also reference the legacy
`<slug>-selfreview-<date>.md` name. Feed findings into `revision`.

## State update

No legacy stage change. Set `research_phase: scientific_review` and the
scientific-review lifecycle gate to `conditional` (or `fail` on blocking
findings), bound to the current draft/upstream hashes. `citation-audit` must pass
before this gate becomes `pass`.

## Exit checklist

Verify each item before emitting; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] Full draft, venue profile, and `style/<venue>.md` read *this session*
      — not recalled from earlier context; `reviewer_intel:` dossier read
      if present.
- [ ] All report parts present: summary, focus audit, headline-term audit,
      recommendation + one-line reason, major comments, scientific integrity
      check, minor comments, AI-tell scan, red-flag check.
- [ ] Focus audit done in the right order — contribution sentence written from
      abstract+intro **before** reading further and **before** opening `spine:`;
      both sentences recorded verbatim; any mismatch raised as a major comment.
- [ ] Every title/abstract headline term has its promises listed and each
      marked demonstrated or explicitly delimited.
- [ ] ≥3 concrete weaknesses, each tied to a section/line; none invented.
- [ ] Every venue red flag marked present / absent / N-A — the list was
      walked to the end.
- [ ] AI-tell scan ran `check_prose.py` (result line pasted, findings folded
      in) and respects the §E academic exceptions and §F allowed slots.
- [ ] Scientific-review artifact written with current draft/upstream hashes;
      lifecycle gate is conditional/fail pending citation audit; no stage change.
