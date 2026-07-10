# Venue Calibration

Builds or re-verifies one venue's knowledge so that **no field the pipeline
gates on rests on model recall**. Entry point: `/write venue-calibration
<venue>` (`skills/paper-writer/modes/venue-calibration.md`); also offered
whenever a skill hits a `venue_target` that has no profile. This protocol is
the only sanctioned way to edit `shared/venue_profiles.md` and `style/`.

## Evidence classes

- **Policy fields** — feed mechanical gates (`submission-check`,
  `check_tex.py`): `page_limit`, `bib_style`, `must_include` (+ patterns),
  anonymization, template/class name. Must come from an **official source
  fetched this run** (CFP, author/style guidelines, checklist page). No
  source reached → the field may still be written, but it goes in
  `unverified:`.
- **Norm fields** — prompt calibration, judgment: `theory_depth`,
  `ablation_required`, `seed_count_min`, reviewer persona, red flags.
  Recall + the user's insider experience allowed; stay listed in
  `unverified:` unless a source states them (rare).
- Never write a policy number from memory without listing it in
  `unverified:` — a silently recalled page limit is the exact failure this
  protocol exists to prevent.

## Procedure

1. **Resolve target**: venue name → canonical key (lowercase, snake_case;
   it names the Defaults entry and the `style/<key>.md` file). Existing
   profile → **re-verify**: same steps, but finish with a drift table
   (`field: old → new (source)`).
2. **Gather sources** (WebSearch/WebFetch): the venue's current CFP, author
   guidelines, formatting/checklist pages — prefer the cycle the user
   targets. Record every URL used. Unreachable/offline → say so and
   continue; everything then lands in `unverified:`.
3. **Extract the fixed field list**, quoting a short source line + URL per
   field: page limit (and what counts against it — refs? appendix?),
   double-blind?, required statements/sections, bib style, template/class,
   AI/LLM-use policy, compute-reporting and checklist requirements.
4. **Map requirements to `must_include` tokens**: reuse builtin tokens from
   `check_tex.py` `MUST_INCLUDE_PATTERNS` where they fit. A genuinely new
   requirement gets a new token + regex in the venue's
   `must_include_patterns:` (consumed via `check_tex.py --pattern
   token=regex`). Test any new regex against a phrase that should match
   before persisting.
5. **Grill (one question, skippable)**: ask the user what this venue's
   reviewers punish or reward in their experience — feeds persona and red
   flags; label it as their input.
6. **Draft the four artifacts and show them for confirmation** before
   writing anything:
   - `## <Venue>` prose section in `shared/venue_profiles.md` — persona,
     red flags; provenance footer (`*Sources: <urls> (as_of <date>);
     persona: recall/user experience.*`)
   - the `Defaults by venue` entry (schema below)
   - `skills/paper-writer/style/<key>.md` — section template, tone,
     dos/don'ts (include the no-bulleted-Related-Work/Discussion rule,
     `prose_hygiene.md` §F)
   - `must_include_patterns:` entries, if any new tokens
7. **Persist, then verify mechanically**: run
   `uv run python skills/paper-writer/scripts/check_venues.py`
   and paste its result line — must be clean
   (`execution_discipline.md` rule 4: scripts over recall).
8. **Wire-up sweep**: venue lists that are hardcoded in prose —
   `commands/write.md` argument-hint, `skills/paper-writer/SKILL.md`
   description. (Bootstrap options and peer-reviewer read
   `venue_profiles.md` dynamically — nothing to touch.)

## Defaults schema (per venue)

```yaml
<key>:
  as_of: <ISO date this verification ran>
  sources:
    - <official URL used>
  page_limit: <int | null>
  bib_style: numeric | author_year
  theory_depth: low | medium | high | maximum
  ablation_required: true | false | medium
  seed_count_min: <int>
  must_include: [<tokens>]
  must_include_patterns: {}   # only tokens not builtin in check_tex.py
  unverified: [<fields resting on recall or community norms>]
```

`unverified:` semantics downstream: `submission-check` may not FAIL the
gate on an item whose backing field is unverified — it reports **WARN**
with "field unverified — re-run venue-calibration". Verified fields gate
as usual. `check_venues.py` warns when `as_of` is older than a year.

## Exit checklist

Verify each item before declaring the venue calibrated; fix violations
first (`execution_discipline.md` rule 2):

- [ ] Official sources fetched *this run* and quoted per policy field;
      every policy field without a source is listed in `unverified:` —
      nothing silently recalled.
- [ ] Every `must_include` token resolves (builtin or venue pattern); any
      new regex was tested against a positive example, result shown.
- [ ] All four artifacts drafted, **confirmed by the user**, then written.
- [ ] `check_venues.py` ran clean — result line pasted.
- [ ] Wire-up sweep done (`commands/write.md` hint, SKILL.md venue list).
- [ ] Re-verify runs end with a drift table (old → new per changed field);
      "no drift" is stated explicitly if so.
