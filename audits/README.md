# Audits

## Why this directory exists

Checks only ever accumulate. Every gate, mode, checklist, and lint that ships
stays shipped, because nothing in the workflow forces anyone to ask whether it
still earns its cost — and each one costs maintenance, reading time, and
credibility. A gate that never fires teaches you to skim past gates; a gate
that only ever fires falsely teaches you to override them. Both make the
gates that matter cheaper to ignore.

This directory is where that question gets asked on a schedule, and where the
answer is written down.

## Cadence

Quarterly — 120 days. `scripts/check_audit_due.py` reads the newest dated
audit here and fails once it ages out; the scheduled `maintenance` workflow
runs it monthly, so an overdue review surfaces on its own rather than
depending on anyone remembering.

## Procedure

1. Generate the inventory:

   ```bash
   uv run --project . python3 scripts/gate_inventory.py \
       --output "audits/$(date +%F)-gate-inventory.md"
   ```

2. Rule on every row. `scripts/check_audit_due.py` counts blank `Verdict`
   cells and stays red until none are left, so a generated-but-unreviewed
   inventory does not satisfy the cadence.

3. Execute the retirements in a **separate** commit that references the audit
   file, so the review and the deletion are independently reviewable.

## Verdicts

| Verdict | Meaning |
|---|---|
| `keep` | Still load-bearing. No action. |
| `merge` | Real, but overlaps another check. Fold it in and retire the duplicate. |
| `retire` | Remove it. Record why below before deleting. |

## When to retire

Any one of these is enough to justify a `retire` verdict:

- It has not fired in real use since it shipped, and you can name the runs
  where it should have.
- The only times it fired, it was wrong.
- Another check now subsumes it, so both firing on the same input is noise.
- Its precondition no longer exists (the mode, host, or format it guards is
  gone).
- It duplicates wording that has since been single-sourced elsewhere, so the
  copy can now only drift.

## Retirement is recorded, not silent

Every `retire` verdict carries three lines in the audit file: what the check
was, why it is going, and **what would justify bringing it back**. A silent
deletion is why the next person re-adds the same check two quarters later.

## What this audit does not measure

This repo has no run telemetry. "Never fired" is not observable here — it is
the author's recollection plus git history, and it should be written down as
such. An audit that claims usage data it does not have is worse than one that
says "not observed, judged from recall": the second is a claim you can argue
with. Do not let the generated inventory's precision (line counts, ages) imply
that the verdicts rest on measurement.

Scope: the check surface only. This review never rules on research content,
findings, or the evidence vault.
