# Review-ethics gate

Run this **before reading the manuscript**. Reviewing someone else's work
carries obligations that drafting your own does not. Three blocking checks; if
any is unresolved, ask the user and default to caution.

## 1. Confidentiality (blocking)

- An unpublished submission is **confidential**. Confirm the user is an assigned
  reviewer / AC, or the authors shared it for feedback. If provenance is unclear,
  ask before proceeding.
- Process the file **locally** (Read tool on the local PDF/tex). Do not upload it
  to external services as part of reviewing.
- Do **not** retain or repurpose the manuscript's ideas/results outside this
  review.
- `--council` transmits the manuscript text to other model CLIs (external
  services). Treat this as external transmission across a confidentiality
  boundary. Only consider it when check 3 permits LLM assistance **and** the user
  explicitly accepts it. **Even then, the Claude Code platform may hard-block the
  fan-out as data exfiltration — and user consent does not override a platform
  block.** For a real confidential submission, expect `--council` to be refused;
  **downgrade to a local single-model review** and tell the user. Never attempt
  to evade the block (chunking, obfuscation, etc.). The panel is realistically
  usable only for artifacts cleared for sharing (public preprint, camera-ready,
  the user's own paper, a mock review).

## 2. Conflict of interest (surface for the user to judge)

Flag obvious COIs from any author/affiliation info visible (often anonymized):

- Same institution, or recent (≈3-year) co-authorship.
- Advisor/advisee or close collaborator.
- Financial or competitive stake in the outcome.

You cannot always detect these (double-blind). Remind the user to apply the
venue's COI rules; they make the call.

## 3. Venue LLM-in-reviewing policy (blocking for `--council`; advisory otherwise)

Many venues restrict LLM use in reviewing and forbid uploading submissions to
LLMs. Known stances change yearly — **state what you know, then tell the user to
confirm the current policy for their venue/year**:

- Several major ML/NLP/vision venues (e.g. NeurIPS, ICML, ACL, CVPR) have, in
  recent years, prohibited or restricted submitting LLM-generated reviews and/or
  uploading submissions to non-privacy-preserving LLM services.
- Some venues permit LLM *assistance* (e.g. polishing the reviewer's own text)
  but not LLM-*authored* reviews.

**Operating rule regardless of venue**: the output of `/review` is a **draft to
inform the human reviewer's own reading and judgment**. The human reviewer reads
the paper themselves, verifies every claim the draft makes, and owns and signs
the final review. Never present the draft as a review to paste in verbatim.

## Pass condition

Checks 1 and 3 (LLM-authored-review caveat) acknowledged; `--council` additionally
requires explicit policy clearance. COI surfaced. Then — and only then — ingest
the manuscript.
