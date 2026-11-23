---
name: incisive
description: Argumentative English writing workbench with Socratic shaping, deterministic anti-slop scanning, and surgical revision playbooks. Use when drafting, structuring, auditing, critiquing, sharpening, unpacking evidence, calibrating tone, framing intros/conclusions/titles, or polishing analytical essays, technical deep-dives, memos, or academic papers.
---

# Incisive

Incisive is an argumentative writing system modeled on a thin router shell, persistent context files, deterministic mechanical scanning, and single-concern revision playbooks. Inspired by the structural argumentation principles of Joseph M. Williams and Lawrence McEnerney, it turns rough outlines into defensible arguments and subjects drafts to objective, reader-first diagnosis.

## Permission Mandate

Default AI writing is timid, decorative, and summary-heavy. It hides behind topic announcements, hollow words like "important" and "interesting", numeric lists ("First... Second... Third..."), and unearned certainty.

When this skill is active, reject safe report-style prose:

- Demand a **point**, not a topic. A valid claim is significant, non-obvious, at least mildly contestable, and scoped to the piece's length.
- Treat writing as an **amiable, rigorous conversation** with a smart, skeptical reader who respects you but will not agree merely because you asserted something.
- Treat writing as **discovery**. Better claims often emerge at the end of a draft; promote them forward instead of protecting a weak first-draft thesis.
- Separate **evaluation** from **editing**. Diagnostic commands (`audit`, `critique`) report findings and never rewrite prose unless the user asks.

## Persistent Context Files

Two optional context files steer every command. Find the draft first (ask where the essay lives if it is not obvious), then locate both files relative to it:

- `VOICE.md`: Standing writing context created by `init` (target reader, what readers already agree on, publication venue, register, citation style, personal anti-patterns). There is one per workspace, blog, or course. Look in the draft's directory, then in each parent directory up to the workspace root; the nearest one wins.
- **The brief**: Per-piece argument specification created by `shape` (the puzzle, working claim, point strategy, section map with one-sentence points, evidence plan, anticipated counterclaims). It lives beside the draft it specifies:
  - One piece in the directory: `BRIEF.md`.
  - Several pieces in the directory: `<draft-stem>.brief.md`, so `pricing-bots.md` pairs with `pricing-bots.brief.md`.
  - Never overwrite a `BRIEF.md` that belongs to a different piece. Use the `<draft-stem>.brief.md` form for the new piece instead.

Always read `VOICE.md` and the draft's brief, if they exist, before executing any command. The playbooks write `BRIEF.md` for short; they mean the brief of the piece in play, whichever name it has.

### Status Log

Every brief ends with a `## Status Log` section. It is the only record of which commands have run on a piece, and the default behavior below depends on it. When a command finishes, append one line: the date, the command, and the outcome in a few words.

```markdown
## Status Log
- 2026-03-04 `draft`: full first draft, 1,480 words; emergent claim flagged in the conclusion
- 2026-03-05 `audit`: 2 high / 5 medium; next `sharpen`, then `unpack`
```

`audit` and `critique` are read-only with respect to the draft; this log line is the one write they make. If the piece has no brief, do not create one just to hold the log.

## Writing Modes

Set these two dimensions per piece in `BRIEF.md` (do not hard-code one template across all essays):

- **Point Strategy**:
  - `point-first` (default): State the main claim explicitly at the end of the introduction and develop it across the body.
  - `point-last` (advanced): Pose a tightly framed puzzle and anticipatory concepts in the introduction, then build methodically toward the claim in the conclusion. Never let `point-last` degenerate into a chronological diary of how the writer thought.
- **Venue Register**:
  - `essay` (humanities, social science, or analytical long-form)
  - `technical` (engineering deep-dive, architecture RFC, research analysis)
  - `memo` (strategy memo, executive decision brief)

## Command Routing

Load only the reference playbook matching the user's request, plus `references/calibration-examples.md` when that playbook asks for it. Never load all references at once.

| Command | Category | When to Trigger | Reference Playbook |
| :--- | :--- | :--- | :--- |
| `init` | Build | Set up standing audience, voice, and register (`VOICE.md`) | `references/init.md` |
| `shape` | Build | Turn rough notes, outline, or raw ideas into `BRIEF.md` via Socratic Q&A | `references/shape.md` |
| `draft` | Build | Write a full first draft or targeted section from `BRIEF.md` | `references/draft.md` |
| `audit` | Evaluate | Run mechanical scan (`scripts/detect.py`) + 4-part structural audit (read-only) | `references/audit.md` |
| `critique` | Evaluate | Writing-lab diagnosis: biggest blind spot, section map, written Action Plan (read-only) | `references/critique.md` |
| `sharpen` | Refine | Upgrade weak/obvious claims; align intro with stronger emergent conclusion claim | `references/sharpen.md` |
| `structure` | Refine | Reorganize into 2-4 coherent sections with logical order and section claims | `references/structure.md` |
| `unpack` | Refine | Connect quotes, numbers, and examples to claims with explicit analytical bridges | `references/unpack.md` |
| `nuance` | Refine | Fix strident absolutes or mealy-mouthed hedging; integrate plausible counterevidence | `references/nuance.md` |
| `distill` | Refine | Cut plot/background summary, replace hollow importance words, remove drafting noise | `references/distill.md` |
| `frame` | Frame & Ship | Rewrite puzzle-driven intro, "So what?" conclusion, and two-part conceptual title | `references/frame.md` |
| `polish` | Frame & Ship | Final proofread, optional close-paraphrase check against sources, and clean re-audit | `references/polish.md` |

For before/after calibration anchors during evaluation or revision, load `references/calibration-examples.md`.

## Default Behavior (No Specific Command)

If the user invokes `incisive` without naming a command:

1. Check the working directory for `VOICE.md`, a brief, and any draft markdown/text file. If several drafts are present, ask which piece the user means.
2. Read the brief's Status Log, inspect the current stage, and recommend the single best next command:
   - Only raw ideas or an outline, no brief -> recommend `shape`.
   - Brief exists, no draft -> recommend `draft`.
   - Draft exists and the Status Log shows no `audit` since the last `draft` or refine command (or there is no brief to check) -> recommend `audit`.
   - Draft is structurally sound but opening/ending/title feel flat -> recommend `frame`.
   - Draft is near final -> recommend `polish`.
3. Ask the user to confirm or choose another command before modifying files.

## Deterministic Scanner

Whenever running `audit` or `polish` (or verifying edits), run the bundled stdlib Python scanner. It ships at `scripts/detect.py` inside this skill's directory (the directory holding this `SKILL.md`), not inside the user's project, so resolve that directory to an absolute path first and substitute it for `<skill_dir>`:

```bash
python3 <skill_dir>/scripts/detect.py <draft_path> --format md
```

If source texts are available for paraphrase boundary checking, pass them via `--source`:

```bash
python3 <skill_dir>/scripts/detect.py <draft_path> --source <source1.txt> --source <source2.txt> --format md
```

Exit code 2 means the draft or a `--source` path was missing and nothing was scanned. Fix the path and rerun; never report that as a clean scan.

The scanner skips YAML frontmatter, code blocks, tables, footnote definitions, and back-matter sections such as References, so its "intro" and "conclusion" are the first and last prose paragraphs of the argument itself.

Treat scanner findings as objective evidence to triage, not blind rules to obey mechanically. Explain false positives if a flagged word serves a genuine analytical role.

## Gotchas

- Never rewrite a whole draft during `audit` or `critique`. Give surgical diagnostics and let the writer own the thinking.
- Never dump 6 questions at once during `shape`. Ask only 1-2 sharpest follow-up questions per turn.
- Never replace a writer's voice with generic "AI essay" polish. Keep prose direct, concrete, and earned.
- Always check whether the real thesis is hiding in the final paragraph before fixing anything else.
