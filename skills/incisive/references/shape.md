# Playbook: shape

Transform rough ideas, reading notes, or a loose outline into a tight, defensible `BRIEF.md` through surgical Socratic interrogation.

## Core Interaction Rule

- **Ask ONLY 1-2 sharpest follow-up questions per turn.** Never send a wall of 5-8 survey questions.
- Each question must target the single biggest unresolved gap in the argument right now.
- Push back respectfully when the user offers a topic instead of a claim, data instead of evidence, or a list instead of a logical order.

## Interrogation Sequence (Across 3-5 Short Turns)

Progress through these four layers adaptively (skip any layer the user has already nailed):

1. **Surface the Puzzle**:
   - Identify what is puzzling, overlooked, contradictory, or commonly misunderstood about the subject.
   - If the user's draft prompt is binary ("agree or disagree") or descriptive ("discuss X"), push past yes/no or inventory toward a genuine analytical tension.

2. **Pressure-Test the Working Claim**:
   - Ask the user to complete: *"I am addressing [topic] in order to show how/why [indirect question]."*
   - Convert that into a single testable claim sentence and check it against four criteria:
     - **Significant**: Helps the reader understand something that matters.
     - **Non-obvious**: Not something informed readers already believe.
     - **Contestable**: A reasonable person could push back or offer an alternative reading.
     - **Scoped**: Provable within the target word count.

3. **Separate Data from Evidence & Lock Section Order**:
   - Distinguish raw *data* (facts, quotes, benchmarks, events) from *evidence* (data mobilized to justify a specific sub-claim).
   - Force an explicit rationale for section ordering (causal, contrastive, escalating complexity, objection-then-resolution). Reject arbitrary order or "three reasons: first, second, third".

4. **Plant the Strongest Objection & Choose Point Strategy**:
   - Ask: *"What piece of evidence or counter-perspective would a smart, respectful critic use against you?"*
   - Decide between `point-first` (default) and `point-last` (only if the writer wants deliberate analytical suspense and commits to an anticipatory intro).

## Output: `BRIEF.md`

Once the four layers converge, draft the brief and ask the user to approve before running `draft`.

Save it beside where the draft will live. Use `BRIEF.md` when the directory holds a single piece. When the directory already holds another piece or another piece's `BRIEF.md`, save it as `<draft-stem>.brief.md` instead (for example `pricing-bots.brief.md` for `pricing-bots.md`) and never overwrite the existing brief.

```markdown
# Argument Brief: [Working Title]

## Configuration
- Register: essay | technical | memo
- Point Strategy: point-first | point-last
- Target Length: [word count or pages]

## The Puzzle
[What readers misunderstand, overlook, or find puzzling]

## Working Main Claim
[One concrete, contestable sentence]

## Section Blueprint (2-4 Major Sections)
1. **[Section Name]**
   - Section claim: [One sentence]
   - Evidence to unpack: [Key data/quotes/examples + how they support the claim]
   - Order rationale: [Why this section belongs here]
2. ...

## Anticipated Objection / Limit
- Strongest counterclaim or contradictory data:
- Planned response (rebut, qualify, or concede-and-weigh):

## Open Uncertainties to Explore While Drafting
- [Bullets for questions that drafting itself should resolve]

## Status Log
- [YYYY-MM-DD] `shape`: brief approved
```

Every later command appends one line to the Status Log, so keep it as the final section.
