# Playbook: audit

Run an objective, two-layer mechanical diagnostic on a draft. **This command is strictly read-only**: diagnose and locate flaws, but do not rewrite the full draft.

Load `references/calibration-examples.md` if you need reference anchors for judgment calls.

## Step 1: Run Deterministic Scanner

Execute the Python scanner first. `<skill_dir>` is the absolute path of the directory holding this skill's `SKILL.md`:

```bash
python3 <skill_dir>/scripts/detect.py <draft_path> --format md
```

If source texts are provided, append `--source <path>` for each source file. Exit code 2 means a path was wrong and nothing was scanned; fix it and rerun.

Review every automated flag and filter out genuine false positives before reporting.

## Step 2: Run the Four-Part Mechanical Structural Audit

Simulate a reader who has zero background knowledge of what the author *meant* to say and can rely only on the text on the page.

### Check 1: Frame & Best-Point Comparison
- Extract the single sentence in the introduction closest to the main claim (usually the final sentence).
- Extract the single sentence in the conclusion closest to the main claim (could be anywhere).
- Place them side by side:
  - Do they contradict each other?
  - Is the conclusion sentence more specific, insightful, and contestable than the introduction sentence?
  - Evaluate the best candidate against the 4 claim criteria: **Significant**, **Non-obvious**, **Contestable**, **Scoped**.
  - Verify whether the draft's `point-first` or `point-last` execution actually works, or if it reads like a messy chronological history of the writer's thought process.

### Check 2: Section Coherence & Ordering Rationale
- Divide the body into its major sections (a 1,200-2,000 word essay typically needs 2-4 sections).
- For each section, quote or mark its section-level claim sentence (or flag `[MISSING SECTION CLAIM]`).
- Audit section order: Is there a substantive logical progression, or is it merely numeric ("First / Second / Third"), copied from the source text's chronology (summary trap), or copied blindly from the prompt's wording?

### Check 3: Evidence Unpacking
- Inspect every quotation, metric, chart reference, and concrete example.
- Flag every instance where primary data is dropped in without explicit prose connecting its key terms to the claim it supposedly proves.

### Check 4: Nuance & Counterevidence
- Diagnose tone extremes:
  - **Strident certainty** (sweeping absolutes, zero qualifications).
  - **Mealy-mouthed hedging** (stacked qualifiers that evaporate the claim).
- Identify the strongest plausible objection or contradictory piece of evidence that the draft currently ignores.

## Output Format

Present the audit in this exact structure:

```markdown
# Mechanical Audit Report

## 1. Automated Scan Summary (scripts/detect.py)
- [Condensed verified findings with line/paragraph references]

## 2. Frame & Main Claim Check
- **Intro candidate**: "..." (Para X)
- **Conclusion candidate**: "..." (Para Y)
- **Verdict**: [Aligned / Conclusion Stronger / Contradictory / Topic-Only]
- **4-Criteria Score**: Significant | Non-obvious | Contestable | Scoped

## 3. Section Map & Ordering Audit
- Section 1 (Paras X-Y): [Claim found or MISSING]
- Section 2 ...
- **Ordering diagnosis**: [Substantive logic vs. numeric/chronological/summary]

## 4. Unpacked Evidence Flags
- [Para X]: [Quote/data] -> Why the logical bridge is missing.

## 5. Tone Calibration & Missing Counterevidence
- **Tone flags**: [Strident or over-hedged sentences]
- **Unaddressed objection**: [Specific challenge a skeptical reader will raise]

## Recommended Next Commands (Priority Order)
1. `sharpen` / `structure` / `unpack` / `nuance` / `distill` / `frame` (list top 2-3 with one-line rationale)
```

## Record the Audit

If the piece has a brief, append one line to its `## Status Log` (date, `audit`, flag counts, recommended next commands). This is the only file write `audit` makes; the draft stays untouched.
