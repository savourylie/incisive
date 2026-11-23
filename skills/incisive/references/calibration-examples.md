# Calibration Examples (Original Before / After Anchors)

Use these original examples to calibrate judgment during `audit`, `sharpen`, `unpack`, `nuance`, `frame`, and `polish`.

---

## 1. Weak vs. Strong Claims

### Fail: Topic announcement (uncontestable)
> In this essay, I will examine how remote work policies affect software engineering teams.

*Why it fails*: Announces an intention rather than a claim. Nobody can disagree that you are about to examine the topic.

### Fail: Obvious truism + empty importance word
> Remote work is an extremely important trend that raises crucial questions about collaboration and productivity.

*Why it fails*: Every reader already agrees; "extremely important" and "crucial" assert value instead of stating substance.

### Pass: Significant, non-obvious, contestable, scoped
> While distributed-work debates focus on real-time communication friction, asynchronous documentation actually fails first at architectural boundary decisions—not because engineers write too little, but because written RFCs reward premature consensus over productive disagreement.

*Why it passes*: Names a specific mechanism, challenges a common assumption, invites reasonable debate, and is provable in a focused essay.

---

## 2. Intro vs. Emergent Conclusion Alignment

### First-draft intro sentence (too broad)
> Urban transit agencies have used dynamic pricing to shape commuter behavior in major metropolitan areas.

### First-draft conclusion sentence (where the real insight surfaced)
> Although congestion pricing is usually defended as a revenue mechanism for rail expansion, Stockholm and London show that its political durability depends less on fare-box revenue than on visibly reallocating freed street space to buses within the first six months.

### Fix A (Point-First): Promote the conclusion claim into the intro
> Congestion pricing is routinely sold to voters as a funding stream for future rail projects. Yet the contrast between stalled proposals and durable programs in Stockholm and London suggests that political survival depends less on long-term capital revenue than on visibly converting cleared traffic lanes into faster bus service within the first six months.

### Fix B (Point-Last): Anticipatory intro sentence (uses key terms without spoiling the verdict)
> While city planners routinely pitch congestion pricing as a funding engine for future rail, the divergent political fates of Stockholm and London point to a more immediate test: what voters actually experience on street-level transit during the policy's first six months.

---

## 3. Dropped Evidence vs. Unpacked Evidence

### Fail: Dropped quote (forces reader to guess the link)
> Early open-source maintainers treated governance as a social norm rather than a legal contract. As one core developer wrote in 2004, "A license tells strangers what they cannot steal, not who shows up on Sunday."

*Why it fails*: The reader sees a colorful quote, but the writer never unpacks how "Sunday" or "strangers" supports the specific claim about governance vs. law.

### Pass: Unpacked with keyword echo and analytical warrant
> Early open-source maintainers relied on informal reciprocity rather than legal enforcement to sustain critical projects. When a core developer remarked in 2004 that "a license tells strangers what they cannot steal, not who shows up on Sunday," he drew a sharp boundary between legal permission and voluntary stewardship: copyright could deter hostile "strangers," yet day-to-day maintenance depended on an unwritten social obligation to keep "showing up" without contractual pay.

---

## 4. Tone Calibration: Strident vs. Mealy-Mouthed vs. Calibrated

### Fail A: Strident certainty (unnuanced)
> For the past decade, every enterprise software team has completely abandoned monolithic architectures. Microservices have proved so undeniably superior that no serious engineer still defends single-codebase deployments, and deployment bottlenecks have simply vanished.

### Fail B: Mealy-mouthed hedging (evaporates the claim)
> For almost a decade, many enterprise teams have somewhat moved away from most monolithic architectures, and microservices have seemed fairly persuasive to quite a few engineers. Today, certain kinds of deployment bottlenecks have just about more or less disappeared in many organizations.

### Pass: Calibrated precision (scoped, authoritative)
> Over the past decade, large engineering organizations have shifted aggressively toward microservices to decouple release cycles across independent teams. That shift eased coordination bottlenecks between squads, yet it rarely eliminated operational complexity; instead, it relocated friction from shared codebases into distributed debugging and network reliability.

---

## 5. Report-Style Intro vs. Puzzle-Driven Intro

### Fail: Report-style opener (echoes prompt + hollow adjectives)
> Algorithmic pricing is one of the most important and interesting developments in modern retail. Throughout the past decade, many airlines and e-commerce platforms have adopted automated pricing models. This very significant shift shows how companies use data to set prices. By examining retail pricing software, its effects on markets can be understood.

### Pass: Puzzle-driven opener (challenges a surface assumption)
> Automated pricing tools are commonly praised for making consumer markets more competitive by matching rivals' discounts in milliseconds. When a competitor cuts a fare, an algorithm responds instantly, seemingly handing buyers the lowest possible price. Yet empirical studies of online retail reveal a stubborn paradox: in categories dominated by rapid repricing bots, average prices often drift upward rather than down. Far from intensifying price wars, high-frequency repricing eliminates the temporary advantage of undercutting a rival, teaching competing algorithms to avoid discounts altogether.

---

## 6. Two-Part Conceptual Title

- **Weak (echoes prompt)**: *An Analysis of Algorithmic Pricing in Retail Markets*
- **Strong (previews conclusion's key concepts)**: *Instant Matching, Quiet Collusion: Why Repricing Algorithms Discourage Price Wars*

---

## 7. Paraphrase Boundary Check

### Original source passage
> Because institutional memory erodes faster during rapid turnover than formal handbooks can capture, teams that rely exclusively on written wikis mistake archived decisions for shared judgment.

### Fail: Close paraphrase (plagiarism even if cited)
> Since organizational memory fades more quickly during fast staff turnover than official manuals can record, groups relying solely on documented wikis confuse stored choices with collective judgment (Author, 2025).

*Why it fails*: Tracks the original syntax clause-for-clause with synonym swaps ("institutional" -> "organizational", "erodes" -> "fades", "handbooks" -> "manuals", "mistake" -> "confuse").

### Pass: True synthesis / summary from understanding
> As Author (2025) observes, static documentation cannot substitute for lived team judgment when high staff attrition outpaces what gets written down.
