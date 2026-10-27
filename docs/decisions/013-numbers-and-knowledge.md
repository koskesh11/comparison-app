# 013 Every number is PoB's or a verified note's

- Date: 2026-10-26/27 (grilling rounds 2, 6, 7, 9-12, 14)
- Decided by: owner; the folder name by Claude (round 12)
- Status: accepted
- Scope: the analyzer's numbers, the mechanics notes, the glossary, the exam

## Context
PoB is the math. What PoB does not model (overlaps, uptime, interactions it cannot parse) has to come from somewhere
traceable. The owner wants a system that gets better with use: "If you don't learn from these mistakes and there's no
evolution in the app, there's no point in keeping it."

## Decision
- Every number comes from PoB or a mechanics note. The AI only explains and proposes.
- Only verified notes change numbers. A draft note is shown next to the number as "if this note is right: X".
- Claude drafts notes; the owner verifies them. The owner's answers are knowledge stored with their build context and
  reasoning, not universal rules; "PoE is full of niche cases."
- When sources conflict (wiki, poedb, PoB), ask the owner. PoB against the owner's word: case by case. When PoB's
  numbers do not add up with what the owner said, question him.
- Every correction is logged, so a repeated mistake can be detected. Self-learned findings are brought to the owner as
  questions.
- One agreed vocabulary: a glossary in the knowledge base; when the owner strays from a term, Claude says so. An exam
  makes learning measurable and keeps growing.
- The knowledge folder is named `mechanics/` (today `vault/`, 164 interaction notes as the start). Each note names the
  step of the damage or defence calculation it affects.
- Knowledge that no code reads is not done: research ships with the code that reads it (lesson from task 035).

## Consequences
- When the owner brings the 3.30 patch notes (league start 13 November 2026), every mechanics note, exam question and
  glossary term is checked against them, and results that rely on 3.29 rules are flagged until PoB updates.
