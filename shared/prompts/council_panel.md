# Council Panel Protocol

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
by a chair, widens coverage cheaply. The chair (this session) stays in control — the
panel **suggests**, it never writes to research-state directly.

## Members and chair

| Member | CLI | Auth |
|---|---|---|
| Codex | `codex exec` | ChatGPT subscription |
| Gemini | `agy -p` | Antigravity sign-in |
| Claude | `claude -p` | Claude subscription (independent of the chair) |
| DeepSeek | `opencode run` | opencode (free DeepSeek V4 Flash) |

**This Claude Code session is the Chair.** It builds the panel prompt, runs the
dispatcher, and synthesizes the results into the calling mode's normal structured
output. It does not merely concatenate member answers.

## When to run

**Opt-in only.** Run the panel when **either**:

- the user invoked the mode with the `--council` flag (e.g. `/algo ideate --council`,
  `/write self-review --council`), or
- the mode offered a panel and the user accepted.

Run it **after** the calling mode has:

1. Read `.research-state/<slug>.md` on entry.
2. Passed its refuse-if-blank gating (e.g. `ideate` requires a `formalize` block;
   `outline` requires `algorithm_card`; `self-review` requires a draft).
3. Run any pre-flight grill the mode specifies.

Without `--council`, the mode runs exactly as before — **single-model, unchanged.**

## Dispatch

1. Write the panel prompt (mode-specific; see each mode file) to a temp file.
2. Fan out to all members in parallel:
   ```sh
   python3 shared/council.py --prompt-file <panel.txt>
   ```
   Subset with `--members codex,gemini,claude,opencode` (default: all four).
3. Parse the JSON (`members.<name>.answer`). For any member with `ok: false`, note the
   dropout (CLI absent / signed out / timeout) and proceed with whoever answered. A
   smaller panel is still valid.
4. **Cross-review (critique modes only — `outline`, `self-review`, `red-team`,
   `novelty-check`):** anonymize the member outputs as `Response A / B / …` (keep the
   label→member map private), then run a second `council.py` pass asking each member to
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
   `council.py --members <author>` call per contested author so each prompt is
   self-contained: it carries the author's position, the objection verbatim, and the
   instruction to **defend with concrete, checkable evidence or concede the specific
   point**. Do not feed rebuttals back for a second round.
3. **Evidence gate — the chair owns verification.** A panel member is **not** a source of
   truth; its attack is a *hypothesis*, not a finding. Before any attack changes the mode's
   output:
   - **`novelty-check`:** a member's "this is subsumed by / anticipated in <work>" only
     counts after **you verify it against the retrieved set** (and a citation-graph chase
     if needed). If the work exists and genuinely subsumes, flip the verdict and cite it
     from the verified bibliography. If it is unretrievable or doesn't actually subsume,
     **discard the attack** and note why in one line — never flip a verdict on a member's
     unverified say-so. Members debating novelty from parametric memory only agree on
     shared priors; that is exactly what the retrieval gate exists to stop.
   - **`red-team`:** an attack (edge case, statistical pitfall, missing baseline) counts
     only if it is concretely checkable against the work or the venue red-flag list. A
     defended-with-specifics position stands; a conceded one becomes an action item.
4. **Preserve real disagreement.** Where a dispute survives evidence-checking and stays
   genuinely open, present it as a fork for the user — do not pick a silent winner or
   average the positions into mush.

## Anti-hallucination guardrails — NON-NEGOTIABLE

The panel members do **not** share this plugin's verified bibliography, retrieval
tools, or `shared/prompts/anti_hallucination.md` discipline. Treat **everything they
return as unverified ideation/critique**, never as fact:

- **No citations enter state from the panel.** Strip every `\cite{...}`, bibkey,
  author-year, "as shown by X (2019)", DOI, or arXiv id a member emits. If the idea
  behind it is worth keeping, re-express it as a claim and mark it `[VERIFY]` with a
  search query — exactly as the mode's own Anti-sycophancy step requires. A panel
  member is **not** a source for prior-art or novelty claims.
- **No theorem names, no numbers.** Drop invented theorem/lemma names and any numeric
  result a member asserts. Conjectures pass through only as `[CONJECTURE — not yet
  proved]`.
- **Run merged output through the mode's existing gates** before it lands in
  research-state: `gap-analysis`/`ideate` Anti-sycophancy, `paper-writer` bibkey
  discipline (`refs/<slug>.bib`), and `shared/prompts/anti_hallucination.md`.
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
ideation only; citations/claims marked [VERIFY] pending the normal audit.
```

Do not add a frontmatter skip-block (unlike the grill) — the panel is re-run per
invocation when `--council` is passed; it is not a frozen interview.

## Cost note

Each `council.py` call is one parallel fan-out (~10–60s, paced by the slowest member);
a cross-review pass doubles that. Tell the user a `--council` run adds roughly a minute.
If a member's subscription is rate-limited, it drops out gracefully — the rest proceed.
