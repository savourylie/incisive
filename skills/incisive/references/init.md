# Playbook: init

Create a standing `VOICE.md` file in the current writing workspace so every subsequent command calibrates to the real reader rather than a generic audience.

## Workflow

Ask concise, concrete questions across 1-2 short turns (at most 2 questions per turn if the user prefers conversational pacing, or infer from existing writing samples if the user provides them):

1. **Reader & Venue**: Who reads your finished piece, and where does it live (academic journal/course, engineering blog, Substack, executive memo)?
2. **Shared Baseline**: What do your readers already take for granted, so we never waste space proving the obvious?
3. **Register & Citation**: Preferred tone (formal academic, sharp analytical essay, pragmatic technical memo) and citation style (inline links, APA/Chicago, footnotes, none).
4. **Personal Pet Peeves**: Any clichés, structures, or stylistic tics you want banned permanently.

## Output: `VOICE.md`

Write `VOICE.md` with these sections:

```markdown
# Writing Voice & Audience Context

## Target Reader
- Who they are:
- What they already know and agree on:
- What makes them skeptical:

## Default Venue & Register
- Primary venue:
- Register (`essay` | `technical` | `memo`):
- Typical length target:
- Citation convention:

## Stylistic Guardrails
- Tone target:
- Explicit taboos / anti-patterns:
```

Save `VOICE.md` at the root of the writing workspace (the blog, course, or project folder), not inside a single essay's directory, so every piece beneath it finds the same file.

After saving `VOICE.md`, suggest running `shape` with an outline or rough idea to create `BRIEF.md`.
