# Incisive

**An Impeccable-style argumentative English writing workbench for coding and writing agents.**

`incisive` translates the structural argumentation and mechanical revision methodology inspired by Joseph M. Williams and Lawrence McEnerney (*Writing in College*) into a cross-tool Agent Skill package: a thin router `SKILL.md`, 12 on-demand command playbooks, persistent context files (`VOICE.md`, `BRIEF.md`), and a zero-dependency Python deterministic anti-slop scanner (`scripts/detect.py`).

## Design Architecture

- **Thin Router Shell (`SKILL.md`)**: Loads only the single playbook you invoke so context stays lean.
- **Persistent Context (`VOICE.md` + `BRIEF.md`)**: Separates standing reader/register preferences from per-essay argument specs. `VOICE.md` sits at the workspace root; each brief sits beside its draft (`BRIEF.md`, or `<draft-stem>.brief.md` when one directory holds several pieces) and ends with a Status Log of the commands run on that piece.
- **Socratic Shaping (`shape`)**: Asks only 1-2 sharpest follow-up questions per turn until your outline hardens into a defensible, contestable claim.
- **Read-Only Evaluation (`audit`, `critique`)**: Diagnoses flaws without hijacking your voice.
- **Deterministic First Pass (`scripts/detect.py`)**: Pure Python 3 stdlib scanner catches intro clichés, hollow importance words, numeric listing, strident absolutes, stacked hedges, dropped/unpacked quotes, title/frame drift, and close-paraphrase risk against source files.

## Command Vocabulary (12 Commands)

| Stage | Command | Purpose |
| :--- | :--- | :--- |
| **Build** | `init` | Create `VOICE.md` (target reader, baseline assumptions, register, taboos) |
| **Build** | `shape` | Socratic 1-2 question/turn interrogation from rough outline to `BRIEF.md` |
| **Build** | `draft` | Draft full essay or section from `BRIEF.md`, flagging emergent claims |
| **Evaluate** | `audit` | Run `scripts/detect.py` + 4-part mechanical structural audit (read-only) |
| **Evaluate** | `critique` | Writing-lab tutor review: blind spot, maturity map, written Action Plan (read-only) |
| **Refine** | `sharpen` | Strengthen weak claims and align intro with emergent conclusion claim |
| **Refine** | `structure` | Build 2-4 coherent sections with logical order and section claims |
| **Refine** | `unpack` | Bridge quotes, metrics, and examples to claims with explicit analysis |
| **Refine** | `nuance` | Fix strident absolutes & stacked hedges; add plausible counterevidence |
| **Refine** | `distill` | Strip summary bloat, empty importance words, and drafting-diary noise |
| **Frame & Ship** | `frame` | Rewrite puzzle-driven intro, "So what?" conclusion, and two-part title |
| **Frame & Ship** | `polish` | Proofread, run close-paraphrase check against sources, re-scan to clean |

## Installation

Unzip and run the included installer. It symlinks to this checkout by default; add `--copy` for standalone files. Flags can go before or after the target.

```bash
chmod +x install.sh

# Install for a single agent (the target defaults to claude)
./install.sh claude     # ~/.claude/skills/incisive
./install.sh cursor     # ~/.cursor/skills/incisive
./install.sh codex      # ~/.codex/skills/incisive
./install.sh opencode   # ~/.config/opencode/skills/incisive
./install.sh agents     # ~/.agents/skills/incisive

# Or install for every supported tool whose config directory already exists
./install.sh all
```

Re-running the installer replaces a previous incisive install. If the destination holds anything else, the installer leaves it alone and exits with an error; pass `--force` to replace it.

For project-local installation, copy `skills/incisive` into your repo's `.claude/skills/incisive` or `.cursor/skills/incisive`.

## Running the Deterministic Scanner Standalone

```bash
# Scan a markdown or text draft
python3 skills/incisive/scripts/detect.py path/to/draft.md

# JSON output for automation or CI
python3 skills/incisive/scripts/detect.py path/to/draft.md --format json --strict

# Include reference sources to detect close-paraphrase plagiarism risk
python3 skills/incisive/scripts/detect.py path/to/draft.md --source notes/paper1.txt --source notes/paper2.txt
```

Exit codes: `0` when the scan completes, `1` under `--strict` when any high-severity finding remains, and `2` when the draft or a `--source` path is missing (nothing is scanned).

The scanner skips YAML frontmatter, fenced code, tables, footnote definitions, and back-matter sections (References, Works Cited, Notes, Appendix). Lists are scanned for tone but are never treated as the introduction or the conclusion.

`CLOSE_PARAPHRASE_RISK` is high when a sentence tracks a source's structure or repeats eight or more words verbatim, and medium when it shares one short phrase, which is usually a name, a title, or a standard term.

## Tests

The scanner and the installer have stdlib-only regression tests:

```bash
python3 -m unittest discover -s tests
```

## Typical End-to-End Flow

1. `incisive init` (once per workspace/blog/course)
2. `incisive shape` (paste your rough outline -> answer 1-2 sharp questions per round -> approve `BRIEF.md`)
3. `incisive draft` (generate full first draft)
4. `incisive audit` (run `scripts/detect.py` + 4-part mechanical diagnosis)
5. Surgical passes as needed: `sharpen` -> `structure` -> `unpack` -> `nuance` -> `distill`
6. `incisive frame` (rewrite intro, conclusion, and two-part title)
7. `incisive polish` (final proofread + close-paraphrase check + clean scan)

## License

Apache License 2.0. See [LICENSE](LICENSE).
