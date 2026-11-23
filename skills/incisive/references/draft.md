# Playbook: draft

Generate a complete first draft (or a targeted section) strictly from `BRIEF.md` and `VOICE.md`, while preserving the exploratory power of writing.

## Pre-Flight Check

1. Read `VOICE.md` (if present) and the piece's brief (`BRIEF.md`, or `<draft-stem>.brief.md` when the directory holds several pieces).
2. If no brief exists for this piece, pause and ask whether to run `shape` first or draft directly from the user's prompt with a quick 1-2 question alignment.

## Drafting Rules

1. **Use a Functional Draft Introduction**:
   - Do not waste effort polishing literary flourishes yet, and never open with dictionary definitions, grand clichés, or topic echo.
   - Anchor the draft intro with the core puzzle, key conceptual terms, and either the working main claim (`point-first`) or an anticipatory question using the claim's key terms (`point-last`).

2. **Prevent the Summary Trap**:
   - Never spend the first half of the draft narrating background or summarizing source material before the argument starts.
   - Introduce source details only when they serve as evidence for a specific section claim.

3. **Respect Section Architecture**:
   - Build 2-4 clear major sections matching `BRIEF.md`.
   - Give every section an unmistakable transition and a clear section-level claim sentence.
   - Unpack every quote, statistic, or case study in prose immediately before or after citing it.

4. **Leave Room for Discovery**:
   - If a sharper, more nuanced thesis emerges while writing the conclusion, do not flatten it back down to match the weaker draft introduction. Keep the stronger conclusion.

## Post-Draft Handoff

After writing the draft:

- Flag any **Emergent Claim** discovered in the conclusion that is sharper than the introduction's working claim.
- Flag any `[PLACEHOLDER: need evidence for X]` spots where data was thin.
- Append one line to the brief's `## Status Log` (date, `draft`, word count, any emergent claim or placeholders).
- Recommend running `audit` next (ideally after the writer steps back for fresh eyes).
