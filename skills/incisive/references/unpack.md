# Playbook: unpack

Eliminate "dropped quotes" and unexplained data by building explicit analytical bridges between primary evidence and the claims they support.

Load `references/calibration-examples.md` for evidence-unpacking anchors.

## Core Principle

Primary data (quotations, statistics, code benchmarks, historical episodes, case studies) rarely speaks for itself. If readers must guess how a piece of evidence connects to a claim, the essay reads like a scrapbook of pasted fragments rather than critical analysis.

## Workflow

1. **Inventory All Evidence**:
   - Scan every quotation, block quote, number, metric, and factual citation in the draft (use `scripts/detect.py` output if available).

2. **Test the Logical Bridge**:
   - For each item, ask: *"Suppose a skeptical reader accepts this fact/quote as true. Why does it compel them to accept the writer's specific claim?"*
   - Flag any hidden leap in reasoning (unstated assumptions, anachronisms, or ambiguous pronouns like "This shows that...").

3. **Apply the Unpacking Moves**:
   - **Lead-in frame**: State what the reader should notice *before* encountering the quote or metric.
   - **Keyword echo**: Repeat or directly analyze 1-3 pivotal words/figures from the quotation or data immediately before or after it.
   - **Trim bloat**: Cut sprawling block quotes down to the exact phrases being analyzed; never paste six lines when one phrase carries the analytical load.
   - **Verify sufficiency**: If a piece of evidence genuinely does not support the claim even after unpacking, flag it for replacement or claim qualification instead of forcing a weak link.

## Deliverable

Apply the unpacked revisions directly and summarize which quotes/metrics were bridged, trimmed, or flagged as insufficient.
