# Playbook: polish

Execute the final pre-publication verification pass: prose mechanics, source-integrity / close-paraphrase verification, and a clean deterministic re-scan.

Load `references/calibration-examples.md` if verifying paraphrase boundaries.

## Workflow

1. **Deterministic Anti-Slop Scan**:
   - Run the scanner on the draft (`<skill_dir>` is the absolute path of the directory holding this skill's `SKILL.md`):
     ```bash
     python3 <skill_dir>/scripts/detect.py <draft_path> --format md
     ```
   - If the user has source documents in the workspace, include `--source <file>` for every source used.

2. **Close-Paraphrase Integrity Check (When Sources Are Present)**:
   - Inspect every `CLOSE_PARAPHRASE_RISK` flag from `detect.py` and manually check heavily referenced passages. High flags mean the sentence tracks the source's structure or repeats eight or more words verbatim. Medium flags mean one short shared phrase, which is fine when it is a name, a title, or a standard term.
   - Remember the strict standard: **close paraphrase counts as plagiarism even when the source is cited.** If a reader could trace a finger down the draft and swap synonyms back into the original sentence structure, rewrite it completely from understanding without mirroring the source syntax, or convert the exact wording into a properly bounded quotation with attribution.
   - Verify exact quotes have unambiguous opening/closing marks (or block indentation), exact wording (using `[brackets]` and `...` for any modification), and clear attribution.

3. **Sentence-Level Proofread**:
   - Fix cut-and-paste scars (broken transitions, dangling pronouns, subject-verb mismatches, fragments created during editing).
   - Check commonly confused homophones (`its/it's`, `their/there/they're`, `your/you're`, `affect/effect`, `principle/principal`).
   - Verify punctuation, citation consistency, and alignment with `VOICE.md`.

4. **Verification Loop**:
   - Re-run `python3 <skill_dir>/scripts/detect.py <draft_path> --format md` after edits.
   - Confirm zero unresolved high-severity flags (or explicitly document why any remaining flag is an intentional stylistic choice).

## Deliverable

Save the polished draft and output a concise **Ship Checklist** confirming: scanner status, paraphrase/citation check status, and mechanical fixes applied.
