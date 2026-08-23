# Firm Rules — canonical wording

Some rules have to appear **inline** in many files. An agent that loads
`skills/paper-writer/SKILL.md` will not follow a rule stated only in
`commands/write.md`, so a by-reference pointer does not work for them:
duplication is the correct implementation.

Duplication is also how wording drifts. Nothing stops one of thirteen copies
being reworded while the rest keep the old text, and the result is a repo that
asserts two different rules with equal authority — with no way to tell which
one is current.

This file is the canonical wording. `scripts/check_firm_rules.py` fails CI when
a mirror stops carrying it. The check is **containment after whitespace
normalization**: re-wrapping a Markdown paragraph is not drift, changing a word
is. Mirrors may add surrounding text; they may not alter a pinned fragment.

**To change a rule**: edit the canonical block here first, then every mirror,
in one commit. The lint tells you which mirrors you missed.

## Rule index

| ID | Governs | Kind | Mirrors |
|---|---|---|---|
| `R-ROOT-1` | Plugin-root resolution in slash-command wrappers | wording pin | 5 |
| `R-ROOT-2` | Plugin-root resolution in workflow skills | wording pin | 5 |
| `R-ROOT-3` | Plugin-root inheritance in shared prompts | wording pin | 3 |
| `R-EV-1` | Verbatim quote behind every passage record | wording pin | 2 |
| `R-EV-2` | Corpus hits are alarm evidence only | presence pin | 9 |

**Wording pin** = every mirror must contain the fragments verbatim (modulo
whitespace). **Presence pin** = the canonical text lives in one file and the
mirrors reference it by name; the lint only asserts the qualifier has not been
dropped, because the surrounding prose is deliberately different in each.

---

## R-ROOT-1 — plugin-root resolution in `commands/*.md`

A slash-command wrapper is the entry point: if it resolves the plugin root from
the user's working directory, every path below it is wrong, and the failure is
silent when the user happens to be sitting in the plugin directory.

<!-- firm-rule: id=R-ROOT-1 mirrors=commands/*.md -->
> Resolve `PLUGIN_ROOT` from this loaded command file before loading anything:
> it is the absolute parent of the file's `commands/` directory.
>
> Never derive it
> from the user's working directory.
>
> Resolve every `skills/...`, `shared/...`, or
> other plugin resource below as `$PLUGIN_ROOT/<path>`.
>
> Dependency-bearing Python
> scripts use `uv run --project "$PLUGIN_ROOT" python "$PLUGIN_ROOT/<path>"`;
> stdlib-only scripts use `python3 "$PLUGIN_ROOT/<path>"`.
<!-- /firm-rule: R-ROOT-1 -->

---

## R-ROOT-2 — plugin-root resolution in workflow skills

Mirrors are enumerated rather than globbed: `skills/evidence-store/SKILL.md` is
a library skill with no plugin-root section by design, and a `skills/*/SKILL.md`
glob would demand one. The enumeration matches `WORKFLOW_SKILLS` in
`scripts/check_host_parity.py`; a new workflow skill has to be added to both.

Each mirror carries skill-specific text around these fragments — its own example
path, its own bare-path list, its own project-artifact list. That variation is
intended. The four fragments below are not.

<!-- firm-rule: id=R-ROOT-2 mirrors=skills/algo-brainstorm/SKILL.md;skills/literature-explorer/SKILL.md;skills/paper-writer/SKILL.md;skills/peer-reviewer/SKILL.md;skills/research-conductor/SKILL.md -->
> Resolve the absolute path of this already loaded `SKILL.md`, then set
> `PLUGIN_ROOT` to the directory two levels above its containing skill directory
>
> Never infer the plugin location from the
> user's working directory and do not `cd` into the plugin.
>
> Resolve `shared/...`
> and `skills/...` resources against `$PLUGIN_ROOT`
>
> Dependency-bearing Python scripts use
> `uv run --project "$PLUGIN_ROOT" python "$PLUGIN_ROOT/<path>"`; stdlib-only
> scripts use `python3 "$PLUGIN_ROOT/<path>"`
<!-- /firm-rule: R-ROOT-2 -->

---

## R-ROOT-3 — plugin-root inheritance in shared prompts

A shared prompt is normally loaded by a skill that has already resolved the
root, so it inherits rather than re-derives — but it must still work when read
directly.

`shared/prompts/model_dispatch.md` is a **documented exception**: it governs
briefs sent to spawned implementers, which cannot inherit a shell variable or
the caller's plugin context, so it states the stronger interpolation
requirement instead. It is deliberately not a mirror of this rule.

<!-- firm-rule: id=R-ROOT-3 mirrors=shared/prompts/council_panel.md;shared/prompts/reviewer_intel.md;shared/prompts/venue_calibration.md -->
> Inherit the absolute `PLUGIN_ROOT` resolved from the invoking skill. If this
> prompt is loaded directly, derive it from this file's absolute location
> (`.../shared/prompts/../..`).
>
> Never derive it from the user's working directory
<!-- /firm-rule: R-ROOT-3 -->

---

## R-EV-1 — a passage record is not evidence without its verbatim quote

This is the rule the evidence store cannot enforce on its own, which is why it
is pinned here.

`evidencectl passage add` requires `--paraphrase` and accepts `--excerpt`, but
`--excerpt` is documented as *"Hashed in memory; not stored verbatim"*. So the
vault records that **some** span hashing to a given value was inspected on a
given page. It does not record what that span said. The paraphrase is the only
readable account of the source in the store — and the paraphrase is precisely
the artifact that can be wrong. An audit trail built on it can prove a page was
opened; it cannot prove the page was read correctly.

<!-- firm-rule: id=R-EV-1 mirrors=shared/prompts/evidence_grounding.md;skills/evidence-store/SKILL.md -->
> A passage record's paraphrase is not the evidence; the inspected span is.
> `evidencectl passage add` stores a paraphrase and an excerpt hash — `--excerpt`
> is hashed in memory and never written — so the store can prove that some span
> hashing to a given value was inspected, but never that the paraphrase reports
> that span correctly. The paraphrase is the artifact that can be wrong.
>
> Capture the verbatim quote for every passage before calling `passage add`,
> in the source's own vault note and under the same locator, so the paraphrase
> stays checkable against it. A host-side reading skill may own that capture
> step; the requirement holds whether or not one is installed. Never mark a
> passage `verified`, `supports`, or `contradicts` for a substantive method,
> theorem, assumption, experiment, or novelty claim when no verbatim quote for
> it can be retrieved.
<!-- /firm-rule: R-EV-1 -->

---

## R-EV-2 — corpus hits are alarm evidence only

Canonical text: `shared/prompts/evidence_grounding.md` § *Two-fidelity rule
(corpus hits vs. grounded evidence)*. The mirrors reference it by name and each
says something different around it, so this is a **presence pin**: the lint
asserts the qualifier is still there, not that the sentence matches; `match=ci`
because some mirrors open a sentence with it. The failure
it guards against is a mirror that keeps discussing corpus hits after the
qualifier is edited away — at which point abstract-scope records quietly become
usable as proof.

<!-- firm-rule: id=R-EV-2 mirrors=shared/prompts/evidence_grounding.md;shared/prompts/research_lifecycle.md;skills/literature-explorer/SKILL.md;skills/literature-explorer/corpus-prefetch.md;skills/algo-brainstorm/SKILL.md;skills/algo-brainstorm/modes/gap-analysis.md;skills/algo-brainstorm/modes/ideate.md;skills/algo-brainstorm/modes/novelty-check.md;skills/research-conductor/routing.md match=ci -->
> alarm evidence
<!-- /firm-rule: R-EV-2 -->
