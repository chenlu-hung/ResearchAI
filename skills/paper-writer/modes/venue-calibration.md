# Mode: venue-calibration

**Purpose**: add a new venue's knowledge, or re-verify an existing venue
against current official sources. This is plugin maintenance, not paper
work — the only mode allowed to edit `shared/venue_profiles.md` and
`style/`. No research-state file is required or touched.

## Inputs

- Venue name (required); target year/cycle (optional); official URLs
  (optional — skips the search step)
- Web access (WebFetch/WebSearch). Without it the run still works but
  every policy field lands in `unverified:`.

## Procedure

Follow `shared/prompts/venue_calibration.md` end-to-end: resolve key →
gather official sources → extract policy fields with quotes+URLs → map to
`must_include` tokens (new ones get `must_include_patterns` regexes) →
one-question grill for insider knowledge → draft the four artifacts →
user confirms → persist → `check_venues.py` clean → wire-up sweep.

## Output

- Updated `shared/venue_profiles.md` (prose section + Defaults entry) and
  `skills/paper-writer/style/<key>.md`
- For re-verify: a drift table (`field: old → new (source)`)
- Pasted `check_venues.py` result line

## Exit checklist

The protocol's Exit checklist **is** this mode's checklist
(`shared/prompts/venue_calibration.md`; `execution_discipline.md` rule 2
applies — walk it before emitting).
