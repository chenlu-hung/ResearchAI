# Council Panel Protocol

Inherit the absolute `PLUGIN_ROOT` resolved from the invoking skill. If this
prompt is loaded directly, derive it from this file's absolute location
(`.../shared/prompts/../..`). Never derive it from the user's working directory;
project artifacts remain relative to that working directory.

Applied by modes that benefit from **multiple independent models** before they
commit to divergent output (`gap-analysis`, `ideate`) or critique (`outline`,
`self-review`, `red-team`, `novelty-check`). Modes reference this file rather than
duplicating the rules. Inspired by karpathy/llm-council; every member runs through
its **own subscription/sign-in CLI**, not an API key.

Two shapes of panel:

- **Divergence** (`gap-analysis`, `ideate`) — fan out, take the **union**, never rank.
- **Critique** (`outline`, `self-review`, `red-team`, `novelty-check`) — fan out, then
  optionally **cross-examine**: anonymized ranking, and for the adversarial modes a
  *conditional single rebuttal round* (see "Cross-examination" below).

## Purpose

A single model has blind spots: gaps it never lists, candidate families it never
proposes, reviewer objections it never raises. A panel of independent models, merged
by a chair, widens coverage cheaply. The invoking host session stays in control — the
panel **suggests**, it never writes to research-state directly.

## Members and chair

| Member | CLI | Auth |
|---|---|---|
| Codex | `codex exec` | ChatGPT subscription |
| Gemini | `agy -p` | Antigravity sign-in |
| Claude | `claude -p` | Claude subscription (independent of the chair) |
| DeepSeek | `opencode run` | opencode (free DeepSeek V4 Flash) |

**The invoking host session is the Chair.** Whether hosted by Codex, Claude
Code, or another compatible runner, it builds the same persisted panel prompt,
runs the dispatcher, and synthesizes the results into the calling mode's normal
structured output. No host-specific API is part of the evidence contract.

## When to run

**Opt-in only.** Run the panel when **either**:

- the user invoked the mode with the `--council` flag (for example, Claude Code
  `/research-assistant:algo ideate --council` or
  `/research-assistant:write self-review --council`), or
- the mode offered a panel and the user accepted.

Run it **after** the calling mode has:

1. Read `.research-state/<slug>.md` on entry.
2. Passed its refuse-if-blank gating (e.g. `ideate` requires a `formalize` block;
   `outline` requires `algorithm_card`; `self-review` requires a draft).
3. Run any pre-flight grill the mode specifies.
4. For evidence-dependent critique, load the **current candidate-specific
   evidence packet**. Give members that bounded packet, not unrestricted model
   memory or an unversioned bibliography.

Without `--council`, the mode remains single-model; all evidence gates still apply.

## Dispatch

1. Write the panel prompt (mode-specific; see each mode file) to a temp file.
2. Fan out to all members in parallel:
   ```sh
   python3 "$PLUGIN_ROOT/shared/council.py" --prompt-file <panel.txt>
   ```
   Subset with `--members codex,gemini,claude,opencode` (default: all four).
3. Parse the JSON (`members.<name>.answer`). For any member with `ok: false`, note the
   dropout (CLI absent / signed out / timeout) and proceed with whoever answered. A
   smaller panel is still valid.
4. **Cross-review (critique modes only — `outline`, `self-review`, `red-team`,
   `novelty-check`):** anonymize the member outputs as `Response A / B / …` (keep the
   label→member map private), then run a second
   `python3 "$PLUGIN_ROOT/shared/council.py"` pass asking each member to
   evaluate and rank the anonymized set. Skip this for pure-divergence modes
   (`gap-analysis`, `ideate`) where you want union, not ranking.
5. **Cross-examination (adversarial modes only — `red-team`, `novelty-check`):** when the
   cross-review surfaces a *substantive* dispute, run **one** rebuttal round. See the
   dedicated section below — it is conditional, single-round, and evidence-gated.

## Cross-examination (adversarial modes — conditional, single round)

For `red-team` and `novelty-check` the value of a panel is **adversarial pressure**:
heterogeneous models catch each other's blind spots better than one model self-critiques,
because their error distributions differ. But on these modes the failure mode is not
"too few ideas" — it is **confident fabrication** (an invented subsuming paper, a hand-wavy
attack, a fake counterexample). So cross-examination here is gated hard on *evidence*, and
it is **one round, only on real disagreement** — never a loop, never forced consensus.

1. **Gate.** Run the rebuttal round only when the cross-review shows a *substantive* dispute:
   members disagree on a verdict (`novel`/`incremental`/`subsumed`, or a red-flag's
   severity), or one member raises a specific attack another rejects. A stylistic or
   "I'd phrase it differently" split does **not** qualify — skip the round and say so.
2. **One round.** Send each contested position back to *its own author* with the strongest
   opposing objection (anonymized — the author never learns who objected). Dispatch one
   `python3 "$PLUGIN_ROOT/shared/council.py" --members <author>` call per
   contested author so each prompt is
   self-contained: it carries the author's position, the objection verbatim, and the
   instruction to **defend with concrete, checkable evidence or concede the specific
   point**. Do not feed rebuttals back for a second round.
3. **Evidence gate — the chair owns verification.** A panel member is **not** a source of
   truth; its attack is a *hypothesis*, not a finding. Before any attack changes the mode's
   output:
   - **`novelty-check`:** a member's "this is subsumed by / anticipated in <work>" becomes
     a persisted query. Query the vault first, retrieve externally only for the remaining
     gap, inspect the passage, add the atomic claim link, and freeze a replacement packet.
     Only then may it change the verdict. If it is unretrievable or does not actually
     subsume, retain the no-result/contrary evidence and discard the attack—never flip a
     verdict on a member's say-so. Agreement from parametric memory is still not evidence.
   - **`red-team`:** an attack (edge case, statistical pitfall, missing baseline) counts
     only if it is concretely checkable against the work or the venue red-flag list. A
     defended-with-specifics position stands; a conceded one becomes an action item.
4. **Preserve real disagreement.** Where a dispute survives evidence-checking and stays
   genuinely open, present it as a fork for the user — do not pick a silent winner or
   average the positions into mush.

## Anti-hallucination guardrails — NON-NEGOTIABLE

The panel members do **not** share this plugin's canonical evidence packet, retrieval
tools, or `shared/prompts/anti_hallucination.md` discipline. Treat **everything they
return as unverified ideation/critique**, never as fact:

- **No claims or citations enter evidence state from the panel.** Strip every `\cite{...}`, bibkey,
  author-year, "as shown by X (2019)", DOI, or arXiv id a member emits. If the idea
  behind it is worth keeping, re-express it as a hypothesis and persist a search query,
  then run `shared/prompts/evidence_grounding.md`. A panel member is **not** a source
  for prior-art or novelty claims.
- **No theorem names, no numbers.** Drop invented theorem/lemma names and any numeric
  result a member asserts. Conjectures pass through only as `[CONJECTURE — not yet
  proved]`.
- **Run merged output through the mode's existing gates** before it lands in
  research-state: `gap-analysis`/`ideate` prior-art pressure,
  `shared/prompts/evidence_grounding.md`, and
  `shared/prompts/anti_hallucination.md`. A generated BibTeX key is not a gate.
- **The chair owns correctness.** If a member's suggestion is wrong, stale, or
  out-of-scope, discard it and say why in one line. Do not launder a weak idea into
  the output just because two models agreed.

## Synthesis (chair)

De-anonymize privately, then fold the panel into the mode's normal output:

- **Union + dedup**: merge overlapping items; collapse near-duplicates into one,
  noting the convergence ("3/4 members").
- **Attribute provenance lightly**: tag panel-originated items so the user can see
  what came from outside (e.g. a `source:` of `codex+gemini` or `panel`), and keep
  chair-originated items distinguishable.
- **Surface real disagreement**: where members genuinely diverge on a substantive
  point, present it as a fork for the user, not a silently-picked winner.
- **Apply the mode's filters**: forbidden-candidate rules (`ideate`), thin/overflow
  flags (`outline`), red-flag checklist (`self-review`), `[VERIFY]` flagging — all
  still apply to panel-sourced material.
- **Don't favour any one member** — including the `claude` member — by default. The
  chair is a neutral aggregator.

## Persistence

When panel output is written to `.research-state/<slug>.md`, record provenance in the
mode's body block:

```markdown
**Council panel**: codex, gemini, claude, opencode — <date>. Panel items are
hypotheses/query seeds only; none entered the evidence packet without vault-first
retrieval and passage verification.
```

Do not add a frontmatter skip-block (unlike the grill) — the panel is re-run per
invocation when `--council` is passed; it is not a frozen interview.

## Cost note

Each `python3 "$PLUGIN_ROOT/shared/council.py"` call is one parallel fan-out
(~10–60s, paced by the slowest member);
a cross-review pass doubles that. Tell the user a `--council` run adds roughly a minute.
If a member's subscription is rate-limited, it drops out gracefully — the rest proceed.
