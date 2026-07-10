# Mode: grant-nstc

**Purpose**: draft or revise an NSTC (國科會) 專題研究計畫 — the CM03
研究計畫內容. A proposal is not a paper: it sells **vision + feasibility**,
not completed results, and 30% of the score never touches the text (PI's
representative works). No research-state file required; if one exists,
reuse its `algorithm_card`, `refs/<slug>.bib`, and survey — a proposal
grounded in `literature-explorer` output beats one written cold.

## Inputs

- Research idea or existing draft (path); 一年期 or 多年期; 個別型 or 整合型
- The PI's 處/學門 — page caps and review forms vary by 處. **Default for
  this user: 工程處智慧運算學門.**
- A `CM03.tex` template from the PI (expected; e.g. the `nstc-proposal`
  class with `\ProposalBackground` / `\ProposalMethod` / `\ProposalPlan`
  slots, or the PI's own). Fill the template's slots; **never touch its
  preamble, class options, or page geometry** — the template governs
  format. No template → emit Markdown under the three headings.
- Optional: current-year 徵求公告 URL, prior-project progress (連續性計畫)

## Ground truth

Provenance: NSTC official forms fetched 2026-07 — CM03 template
(overleaf.com/latex/templates/…cm03), 工程處 page cap (NSTC 線上申請說明,
secondary), 工程司學門審查注意事項 score anchors, 人文處(新進)初審意見表
(2022.7.27) for the weight shape. **Step 1 re-verifies the current cycle's
figures** — per-處 rules drift year to year.

**CM03 structure** — the three top-level headings are fixed; keep them verbatim:

1. **一、研究計畫之背景** — 所要探討或解決的問題、研究原創性、重要性、
   預期影響性、國內外研究情況、重要參考文獻之評述；連續性計畫應說明
   上年度研究進度。
2. **二、研究方法、進行步驟及執行進度** — 研究方法與原因及其創新性；
   預計可能遭遇之困難及解決途徑；重要儀器之配合使用情形；赴國外或
   大陸地區研究之必要性及預期效益（如有）。
3. **三、預期完成之工作項目及成果** — 預期完成之工作項目；參與人員
   預期可獲之訓練；預期研究成果（期刊論文、軟體、專利…）；學術研究、
   國家發展及其他應用方面預期之貢獻。

**Format — 工程處** (secondary source; step 1 confirms): 表 CM03 至多
**25 頁，其中參考文獻至多 5 頁**（含圖表）。字體/行距/邊界由 PI 的
CM03.tex template 決定，不要動。**超出頁數的部分直接不予審查** —
結論放在頁尾等於沒寫。(對照: 人文處個別型一年期 ≤30 頁、多年期 ≤45 頁。)

**Review scoring** (工程處配分無公開版本 — 審查面向為計畫之價值與意義、
計畫之可行性; weight shape below is the 人文處新進初審表 2022 exemplar):

- 計畫書內容 70% = 主題重要性/原創性/學術應用價值 (40%) +
  國內外文獻掌握及評述 (20%) + 研究方法與執行步驟之可行性及創新性 (10%)
- 研究成果 30% = 主持人代表性研究成果（另表，非 CM03 文字能救）
- 工程司學門 score anchors: 92 ≈ 前 5%、88 ≈ 前 15%、**81 ≈ 通過門檻**
  (約前 54–55%) — 目標是把每個審查面向都推過「推薦」線，而不是單點做深。
- 審查人**另外逐項**判斷: 多年期每一年的必要性（可只推薦較短年期）、
  每位共同主持人的必要性、每條經費的合理性、最近一期成果報告品質。

**Editing-effort allocation** (follows from the weights): 背景 carries
40% + most of the 20% — it gets the most drafting and revision passes.
方法 is only 10% of the score but is where feasibility dies: one
unaddressed difficulty outweighs polished prose elsewhere.

## Procedure

1. **Re-verify ground truth** for the PI's 處 and cycle: current 徵求公告,
   CM03 page cap, review-form weights (WebFetch/WebSearch if available;
   otherwise mark `unverified:` and use the 人文處 figures as fallback).
2. **Read state** (if any): algorithm card, survey, bib. New claims cite
   only keys present in `refs/<slug>.bib` (hard-discipline rule 3 applies).
3. **Ingest the template**: read the PI's `CM03.tex`, identify its section
   slots (e.g. `\ProposalBackground`/`\ProposalMethod`/`\ProposalPlan`) and
   how it compiles (XeLaTeX for CJK fonts is typical). Confirm it builds
   empty before writing into it.
4. **Skeleton before prose**: map content to the three fixed headings; for
   多年期, one milestone table per year with standalone deliverables.
5. **Draft 背景 first, hardest**: open with the specific problem and the
   gap — never 「近年來，隨著…的蓬勃發展」. State originality relative to
   named prior work (the 20% literature score is earned here, with 評述 —
   critique, not enumeration). Expected impact must be concrete: what
   changes in the field/application if the aims succeed.
6. **Aims, not methods; parallel, not dominoed**: each aim is a question
   or deliverable, not a technique. No aim may exist only to feed a later
   aim — the reviewer explicitly picks the fundable duration, so a
   dominoed year 3 gets cut. Every year must deliver something citable.
7. **Feasibility evidence**: pair every ambitious claim with preliminary
   results, the PI's prior work, classical foundations, or a named
   collaborator. 困難及解決途徑 is mandatory content — name ≥1 real
   technical risk per aim and its fallback; a proposal with no admitted
   difficulty reads as unserious.
8. **成果 section**: enumerate deliverables with venue class (e.g. 「投稿
   JMLR / NeurIPS 等級期刊會議論文 2 篇」), software artifacts, and 人才
   培育 (what the assistants actually learn). Tie 貢獻 to the impact
   claimed in 背景.
9. **Budget cross-check** (if drafting 經費 justifications): every line
   (研究人力費、耗材、設備、差旅…) ties to a named work item and year.
10. **Prose pass** (register below); compile the template and take the
    page count from the PDF, not an estimate; then Exit checklist.

## Proposal register (deltas vs. `prose_hygiene.md`)

`prose_hygiene.md` still applies, with these proposal-specific changes:

- **Vision language is allowed when evidence-backed**: 「開創」「突破」
  are legitimate — the form literally asks for 原創性 and 預期影響性 —
  but each such word must sit in the same paragraph as its evidence
  (preliminary result, prior paper, theorem). Unbacked hype is still cut.
- **§F waivers**: the three fixed CM03 headings and per-year milestone
  tables/Gantt are conventional slots; 工作項目 enumerations are expected.
  Prose paragraphs still argue 背景 and 方法.
- **Chinese AI-tells** (check_prose.py is English-only — screen these by
  eye in Chinese drafts): 「近年來，隨著…的快速/蓬勃發展」開場、
  「值得注意的是」「綜上所述」「不僅…更…」堆疊、每段等長、
  full-width em-dash 濫用、條列取代論證。
- English drafts: run `check_prose.py` per section as usual.

## AI-use disclosure

行政院《使用生成式 AI 參考指引》(2023.8, applies to NSTC): substantive
generative-AI assistance in research or output should be disclosed per
academic conventions. Remind the PI; the disclosure decision is theirs.
This mode never fabricates preliminary results, citations, or track-record
claims — an invented 代表作 or pilot result is misconduct, not drafting.

## Output

- The PI's `CM03.tex` filled in (preamble untouched) + compiled PDF;
  fallback without a template: `proposal/cm03-<slug>.md` under the three
  fixed headings
- 多年期: per-year milestone table; budget-justification stubs if requested
- A gap list: every place marked `[PI INPUT NEEDED]` (preliminary data,
  代表作 narrative, equipment, collaborator letters)

## State update

None required (proposal work is out-of-band for the paper stage machine).
If a research state exists, append the proposal path under `notes:`.

## Exit checklist

Verify each item before emitting; fix violations first
(`shared/prompts/execution_discipline.md` rule 2):

- [ ] Step 1 ran: 處-specific page cap + weights verified for the current
      cycle, or explicitly marked `unverified:` with the fallback named.
- [ ] The three CM03 headings appear verbatim; content under each matches
      the official prompts (背景/方法/成果).
- [ ] 背景 opens with the specific problem, not a formulaic ramp; named
      prior work is critiqued (評述), not listed.
- [ ] Every aim is parallel and question/deliverable-shaped; no aim exists
      solely to feed a later one; each year has standalone deliverables.
- [ ] Every vision word (開創/突破/首創…) has same-paragraph evidence;
      every aim has ≥1 admitted difficulty + fallback.
- [ ] No fabricated preliminary results, citations (`refs/` keys only, or
      `[BIBKEY MISSING — verify]`), or track-record claims; PI gaps are
      marked `[PI INPUT NEEDED]`, not filled in.
- [ ] Template preamble/geometry untouched; document compiles; page count
      **from the compiled PDF** ≤ cap (工程處: 25 頁, 參考文獻 ≤5 頁) and
      references within their sub-cap; prose pass ran (English:
      `check_prose.py` result line pasted; Chinese: AI-tell list screened
      by eye).
- [ ] AI-use disclosure reminder delivered to the PI.
