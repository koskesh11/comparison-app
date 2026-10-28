# 025 The repo goes public

- Date: 2026-10-28
- Decided by: owner ("make this repo public, so he can have a look at the entire project"; history clean-up first)
- Status: accepted
- Scope: the GitHub repo koskesh11/comparison-app (renamed from pob-autobuilder on 2026-10-28, owner)

## Context
Decision 005 left going public to the owner, with three steps planned before it: GitHub checks, history clean-up and a
cold review. Decision 003 keeps the working files private and says the history is cleaned once before going public.
The owner wants a friend without Claude to see the project and the damage chain mockup (decision 009).

## Decision
- The history was cleaned before the repo went public: `tasks/`, `.claude/`, `tools/hooks/`, `docs/history/` and
  `CLAUDE.md` were removed from every commit (git filter-repo, 2026-10-28); main's files were unchanged. The first
  project's nine branches are deleted from GitHub. No secret and no personal e-mail was found in any commit (scanned
  2026-10-28; commits carry GitHub's noreply address). A backup bundle of the history before the clean-up stays on the
  owner's machine.
- The mockup is published as an exported copy, `docs/mockup/damage-chain.html`, served by GitHub Pages (`.nojekyll`:
  files are served as they are).
- The GitHub checks and the cold review (decision 005) are not done yet; they stay planned (card 114 is the cold
  review of milestone 1).

## Consequences
- Every commit id changed with the clean-up; old ids in notes (for example 4caf626 in decision 003) name the history
  before it.
- Commits that were removed may stay reachable on GitHub by their old id until GitHub cleans them up (GitHub's
  behaviour, unverified here).
