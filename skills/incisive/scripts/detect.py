#!/usr/bin/env python3
"""
incisive deterministic scanner (scripts/detect.py)

Zero-dependency Python 3 analyzer for argumentative English drafts.
Detects mechanical anti-patterns and extracts structural framing checkpoints:
  1. Intro clichés (dictionary openers, grand platitudes, topic announcements, thinking-history)
  2. Hollow importance substitutes ("very interesting", "crucial question", etc.)
  3. Organization-by-number transitions ("First... Second... Third...")
  4. Tone extremes (strident absolutes & stacked mealy-mouthed hedges)
  5. Potential dropped / unpacked quotations
  6. Structural frame extraction (intro tail vs. conclusion candidate, keyword threading, title check)
  7. Optional close-paraphrase / structural-alignment check against --source files

Markdown handling: YAML frontmatter, fenced code (``` and ~~~), tables, footnote /
link definitions, and back-matter sections (References, Works Cited, Notes, ...) are
excluded from the scan. Lists are scanned for tone but never treated as the intro
or the conclusion.

Usage:
  python3 scripts/detect.py draft.md [--source ref1.txt ...] [--format md|json] [--strict]

Exit codes:
  0  scan completed (with --strict: no high-severity finding)
  1  --strict and at least one high-severity finding
  2  bad input: the draft or a --source path is missing or not a file
"""

import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Tuple

STOPWORDS = {
    "about", "above", "after", "again", "against", "almost", "already", "also",
    "although", "always", "among", "another", "because", "before", "being",
    "between", "could", "during", "every", "first", "found", "great", "having",
    "however", "into", "itself", "large", "later", "least", "might", "never",
    "other", "others", "ought", "perhaps", "quite", "rather", "really", "second",
    "several", "should", "since", "small", "something", "still", "their", "there",
    "these", "thing", "things", "think", "third", "those", "though", "through",
    "under", "until", "using", "where", "which", "while", "whose", "within",
    "without", "would", "years", "people", "state", "states", "make", "makes",
    "made", "many", "much", "more", "most", "some", "such", "than", "that",
    "them", "then", "they", "this", "very", "well", "were", "what", "when",
    "will", "with", "your", "from", "have", "been", "does", "just", "like",
    "only", "over", "same", "take", "work", "didn", "doesn", "cannot",
    "remove", "replace", "build", "create", "become", "becomes", "around",
    "beyond", "toward", "towards", "matter", "matters", "instead"
}

INTRO_PATTERNS: List[Tuple[str, str, re.Pattern]] = [
    (
        "DICTIONARY_OPENER",
        "Avoid opening with a generic dictionary definition; engage a domain thinker's definition if needed.",
        re.compile(
            r"\b(?:Webster(?:'s)?|Merriam-Webster|Oxford(?:\s+English)?\s+Dictionary|Cambridge\s+Dictionary|the\s+dictionary)\s+defines\b"
            r"|\baccording\s+to\s+(?:the\s+)?(?:Merriam-Webster|Oxford|Cambridge|dictionary)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "GRAND_PLATITUDE",
        "Grandly banal opening statement; narrow quickly into a specific puzzle or misconception.",
        re.compile(
            r"\b(?:throughout\s+(?:human\s+)?history|since\s+the\s+dawn\s+of|from\s+time\s+immemorial|"
            r"in\s+today'?s\s+(?:modern\s+|fast-paced\s+|ever-changing\s+)?(?:world|society)|"
            r"is\s+one\s+of\s+the\s+(?:most\s+important|greatest|most\s+significant)\s+\w+\s+(?:ever|in\s+history))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "TOPIC_ANNOUNCEMENT",
        "Meta-announcement names a topic/intent rather than making a contestable claim.",
        re.compile(
            r"\b(?:in\s+this\s+(?:paper|essay|article|piece|post),?\s+I\s+(?:will\s+|am\s+going\s+to\s+)?(?:discuss|explore|examine|analyze|look\s+at|talk\s+about|write\s+about)|"
            r"this\s+(?:paper|essay|article)\s+(?:will\s+)?(?:discuss|examine|explore|analyze|focus\s+on|look\s+at|is\s+about))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "THINKING_HISTORY",
        "Avoid narrating your personal research/thinking process in the opening; lead with the analytical issue.",
        re.compile(
            r"\b(?:in\s+analyzing\s+.{3,60}?,?\s+it\s+is\s+first\s+necessary\s+to|"
            r"in\s+my\s+analysis,?\s+I\s+found\s+that|"
            r"when\s+I\s+first\s+(?:began|started)\s+(?:reading|researching|thinking\s+about))\b",
            re.IGNORECASE,
        ),
    ),
]

HOLLOW_IMPORTANCE_RE = re.compile(
    r"\b(?:"
    r"(?:very|really|extremely|truly|particularly|most)\s+(?:important|interesting|significant|crucial|essential|noteworthy|vital)"
    r"|(?:an?|the)\s+(?:important|crucial|essential|significant|interesting|key|vital)\s+(?:question|issue|concern|point|aspect|role|factor|shift|development|topic|theme)"
    r"|it\s+is\s+(?:important|crucial|essential|vital|imperative|interesting|noteworthy)\s+(?:to\s+(?:note|consider|examine|understand|remember|recognize)|that)"
    r"|(?:is|are|was|were)\s+(?:very\s+|really\s+|quite\s+)?(?:interesting|important|crucial|essential|significant|noteworthy)\b(?!\s+(?:at\s+p|p\s*[<>=]|difference|correlation|effect))"
    r")\b",
    re.IGNORECASE,
)

NUMERIC_OPENER_RE = re.compile(
    r"^(?:First(?:ly)?|Second(?:ly)?|Third(?:ly)?|Fourth(?:ly)?|Fifth(?:ly)?|Finally|Lastly)\b[,\s:]",
    re.IGNORECASE,
)

NUMERIC_FRAMING_RE = re.compile(
    r"\b(?:for\s+(?:two|three|four|five|several)\s+(?:main\s+|key\s+|primary\s+)?reasons|"
    r"the\s+(?:first|second|third|fourth)\s+(?:reason|point|factor)\s+is)\b",
    re.IGNORECASE,
)

STRIDENT_RE = re.compile(
    r"\b(?:"
    r"obviously|undoubtedly|unquestionably|undeniably|indisputably|irrefutably|"
    r"proves?\s+beyond\s+(?:a\s+)?doubt|clearly\s+proves?|"
    r"everyone\s+(?:knows|agrees)|no\s+one\s+(?:can\s+deny|disputes|questions|remembers|doubts)|"
    r"every\s+(?:single\s+)?(?:person|scholar|expert|engineer|critic|liberal|conservative|reader)|"
    r"simply\s+(?:ceased\s+to\s+exist|vanished|disappeared)|completely\s+(?:abandoned|eliminated|destroyed|false|true)|"
    r"utterly\s+(?:false|wrong|meaningless|impossible)|"
    r"it\s+is\s+(?:an\s+)?(?:undeniable|obvious|indisputable)\s+fact"
    r")\b",
    re.IGNORECASE,
)

SOFT_HEDGE_WORDS_RE = re.compile(
    r"\b(?:almost|fairly|somewhat|rather|quite|arguably|seemingly|apparently|"
    r"perhaps|possibly|probably|might|may|could|seems?\s+to|appears?\s+to|"
    r"tends?\s+to|generally|largely|mostly|nearly|virtually|"
    r"just\s+about|more\s+or\s+less|kind\s+of|sort\s+of|to\s+some\s+extent|in\s+a\s+way)\b",
    re.IGNORECASE,
)

MEALY_PHRASES_RE = re.compile(
    r"\b(?:just\s+about|more\s+or\s+less|kind\s+of|sort\s+of|in\s+a\s+sense|to\s+some\s+extent|somewhat\s+fairly|fairly\s+somewhat)\b",
    re.IGNORECASE,
)

# A quotation shorter than this (in characters between the marks) is a scare-quoted
# term, not evidence that needs unpacking.
MIN_QUOTE_CHARS = 12

# A straight double quote opens a quotation only after one of these and closes one
# only before one of these, so inch marks (5" drive) never pair up with a later quote.
_QUOTE_OPEN_AFTER = set(" \t\n([{—–-/*_>")
_QUOTE_CLOSE_BEFORE = set(" \t\n.,;:!?)]}—–-*_'’")

LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\S")
DEFINITION_RE = re.compile(r"^\s*\[[^\]]+\]:\s")
THEMATIC_BREAK_RE = re.compile(r"^\s*([-*_])(?:\s*\1){2,}\s*$")
FENCE_RE = re.compile(r"^(`{3,}|~{3,})")
BACK_MATTER_RE = re.compile(
    r"^(?:references?|bibliography|works\s+cited|sources|notes|footnotes|endnotes|"
    r"further\s+reading|acknowledge?ments?|appendix\b.*|appendices)$",
    re.IGNORECASE,
)

# Sentence-ending punctuation inside a quotation is masked while splitting so a
# multi-sentence quotation stays inside the sentence that introduces it.
_MASK = {".": "", "!": "", "?": ""}
_UNMASK = {v: k for k, v in _MASK.items()}


def find_quote_spans(text: str) -> List[Tuple[int, int]]:
    """Return (start, end) offsets of each double-quoted span, marks included."""
    spans: List[Tuple[int, int]] = []
    open_at: Optional[int] = None
    n = len(text)
    for i, ch in enumerate(text):
        if ch == "“":
            open_at = i
        elif ch == "”":
            if open_at is not None:
                spans.append((open_at, i + 1))
                open_at = None
        elif ch == '"':
            prev = text[i - 1] if i else " "
            nxt = text[i + 1] if i + 1 < n else " "
            can_open = prev in _QUOTE_OPEN_AFTER and not nxt.isspace()
            can_close = not prev.isspace() and nxt in _QUOTE_CLOSE_BEFORE
            if open_at is not None and can_close:
                spans.append((open_at, i + 1))
                open_at = None
            elif can_open:
                open_at = i
    return spans


def substantive_quote_spans(text: str) -> List[Tuple[int, int]]:
    return [(a, b) for a, b in find_quote_spans(text) if b - a - 2 >= MIN_QUOTE_CHARS]


def remove_spans(text: str, spans: List[Tuple[int, int]]) -> str:
    out: List[str] = []
    pos = 0
    for a, b in spans:
        out.append(text[pos:a])
        out.append(" ")
        pos = b
    out.append(text[pos:])
    return "".join(out)


def split_sentences(text: str) -> List[str]:
    """Split a paragraph into rough sentences, keeping each quotation in one piece."""
    chars = list(text.strip())
    for start, end in find_quote_spans("".join(chars)):
        # Leave the quotation's final character alone: `."` may still end the sentence.
        for i in range(start + 1, end - 2):
            if chars[i] in _MASK:
                chars[i] = _MASK[chars[i]]
    protected = re.sub(r"\b(Mr|Mrs|Ms|Dr|Prof|Jr|Sr|vs|etc|e\.g|i\.e|p|pp|Fig|No)\.", r"\1<DOT>", "".join(chars))
    parts = re.split(r"(?:(?<=[.!?])|(?<=[.!?][\"”]))\s+(?=[A-Z\"“(\[])", protected)
    restored = ("".join(_UNMASK.get(c, c) for c in p.replace("<DOT>", ".")).strip() for p in parts)
    return [p for p in restored if p]


def _line_kind(line: str) -> Optional[str]:
    if DEFINITION_RE.match(line):
        return "definition"
    if LIST_ITEM_RE.match(line):
        return "list"
    return None


def _frontmatter_end(lines: List[str]) -> int:
    """Return the number of leading lines that form a YAML frontmatter block (0 if none)."""
    if not lines or lines[0].strip() != "---":
        return 0
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            return i + 1
    return 0


def parse_document(text: str) -> Dict:
    """Parse markdown/plain text into title, headings, and numbered paragraphs.

    Each paragraph carries a `kind` (prose, list, blockquote, table, definition) and
    a `back_matter` flag for anything under a References / Notes / Appendix heading.
    """
    lines = text.splitlines()
    title: Optional[str] = None
    headings: List[Dict] = []
    paragraphs: List[Dict] = []

    buf: List[str] = []
    buf_start = 1
    open_fence: Optional[str] = None
    back_matter_level: Optional[int] = None
    skip_until = _frontmatter_end(lines)

    def flush(end_line: int):
        nonlocal buf
        if not buf:
            return
        raw = "\n".join(buf).strip()
        if raw:
            is_blockquote = all(l.lstrip().startswith(">") for l in buf if l.strip())
            if is_blockquote:
                kind = "blockquote"
            elif all(l.lstrip().startswith("|") for l in buf if l.strip()):
                kind = "table"
            else:
                kind = _line_kind(buf[0]) or "prose"
            clean = "\n".join(re.sub(r"^\s*>\s?", "", l) for l in buf).strip() if is_blockquote else re.sub(r"\s+", " ", raw)
            paragraphs.append({
                "index": len(paragraphs) + 1,
                "start_line": buf_start,
                "end_line": end_line,
                "text": clean,
                "is_blockquote": is_blockquote,
                "kind": kind,
                "back_matter": back_matter_level is not None,
            })
        buf = []

    for i, line in enumerate(lines, start=1):
        if i <= skip_until:
            continue
        stripped = line.strip()
        fence = FENCE_RE.match(stripped)
        if fence and (open_fence is None or fence.group(1)[0] == open_fence):
            flush(i - 1)
            open_fence = None if open_fence else fence.group(1)[0]
            continue
        if open_fence:
            continue

        h_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if h_match:
            flush(i - 1)
            level = len(h_match.group(1))
            htext = h_match.group(2).strip()
            label = re.sub(r"^[\d.)\s]+", "", htext).strip(" #:*_")
            if BACK_MATTER_RE.match(label):
                if back_matter_level is None or level < back_matter_level:
                    back_matter_level = level
            elif back_matter_level is not None and level <= back_matter_level:
                back_matter_level = None
            if level == 1 and title is None:
                title = htext
            else:
                headings.append({"line": i, "level": level, "text": htext})
            continue

        if not stripped or THEMATIC_BREAK_RE.match(line):
            flush(i - 1)
            continue

        # A list or a footnote definition starts a new block even without a blank line.
        if buf and _line_kind(line) and _line_kind(buf[0]) != _line_kind(line):
            flush(i - 1)

        if not buf:
            buf_start = i
        buf.append(line)

    flush(len(lines))
    return {"title": title, "headings": headings, "paragraphs": paragraphs}


def content_tokens(text: str, min_len: int = 4) -> List[str]:
    words = re.findall(r"[a-zA-Z]{2,}", text.lower())
    return [w for w in words if len(w) >= min_len and w not in STOPWORDS]


def stem_variants(word: str) -> List[str]:
    """Return lightweight morphological stem candidates (handles common prefixes)."""
    w = word.lower()
    variants = [w[:5] if len(w) >= 5 else w]
    for pref in ("de", "re", "un", "in", "dis", "mis", "non", "pre", "sub"):
        if w.startswith(pref) and len(w) - len(pref) >= 5:
            stripped = w[len(pref):]
            variants.append(stripped[:5])
    return variants


# A five-letter stem cannot tell these families apart (interest / internal /
# interface all become "inter"), so words that start with one keep four more letters.
LONG_PREFIXES = ("inter", "contr", "trans", "under", "super", "count", "micro", "multi", "extra", "over")


def stem_prefix(word: str) -> str:
    w = word.lower()
    for suf in ("ingly", "ation", "ment", "ness", "ing", "ied", "ies", "ed", "es", "ly", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            w = w[: -len(suf)]
            break
    for pref in LONG_PREFIXES:
        if w.startswith(pref):
            return w[: len(pref) + 4]
    return w[:5] if len(w) >= 5 else w


def strip_quotes(text: str) -> str:
    return remove_spans(text, substantive_quote_spans(text))


def is_content_phrase(gram: Tuple[str, ...]) -> bool:
    """True when an n-gram carries at least two content words (not "at the end of the")."""
    return sum(1 for w in gram if len(w) >= 4 and w not in STOPWORDS) >= 2


def anchor_clusters(seq_a: List[str], seq_b: List[str]) -> int:
    """Count the separate runs of shared, in-order items between two sequences."""
    blocks = SequenceMatcher(None, seq_a, seq_b, autojunk=False).get_matching_blocks()
    return sum(1 for b in blocks if b.size)


def ngrams(tokens: List[str], n: int) -> set:
    if len(tokens) < n:
        return set()
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def ordered_common_anchors(seq_a: List[str], seq_b: List[str]) -> int:
    """Longest common subsequence length of shared anchor stems/words."""
    b_set = set(seq_b)
    a_filt = [x for x in seq_a if x in b_set]
    a_set = set(a_filt)
    b_filt = [x for x in seq_b if x in a_set]
    if not a_filt or not b_filt:
        return 0
    dp = [0] * (len(b_filt) + 1)
    for x in a_filt:
        prev = 0
        for j, y in enumerate(b_filt, start=1):
            cur = dp[j]
            if x == y:
                dp[j] = prev + 1
            elif dp[j - 1] > dp[j]:
                dp[j] = dp[j - 1]
            prev = cur
    return dp[-1]


def check_close_paraphrase(paragraphs: List[Dict], source_paths: List[Path]) -> List[Dict]:
    """Detect both near-verbatim overlap and clause-tracking synonym-swap paraphrases.

    High severity needs structural tracking or a verbatim run of 8+ words. A single
    shared five-word phrase is medium (often a name, title, or standard term), and a
    shared phrase made of function words is ignored.
    """
    findings: List[Dict] = []
    source_sentences: List[Dict] = []

    for sp in source_paths:
        if not sp.exists():
            findings.append({
                "code": "SOURCE_NOT_FOUND",
                "severity": "warning",
                "location": str(sp),
                "snippet": "",
                "message": f"Source file not found: {sp}",
            })
            continue
        src_text = sp.read_text(encoding="utf-8", errors="ignore")
        for para in re.split(r"\n\s*\n", src_text):
            para_clean = re.sub(r"\s+", " ", para).strip()
            if not para_clean:
                continue
            for sent in split_sentences(para_clean):
                toks = re.findall(r"[a-zA-Z]+", sent.lower())
                if len(toks) >= 8:
                    content = [stem_prefix(w) for w in content_tokens(sent, min_len=4)]
                    source_sentences.append({
                        "name": sp.name,
                        "text": sent,
                        "toks": toks,
                        "stems": [stem_prefix(w) for w in toks],
                        "grams": ngrams(toks, 5),
                        "content": content,
                        "content_set": set(content),
                    })

    if not source_sentences:
        return findings

    for p in paragraphs:
        if p["is_blockquote"]:
            continue
        unquoted = strip_quotes(p["text"])
        for sent in split_sentences(unquoted):
            dtoks = re.findall(r"[a-zA-Z]+", sent.lower())
            if len(dtoks) < 8:
                continue
            dstems = [stem_prefix(w) for w in dtoks]
            d5 = ngrams(dtoks, 5)
            d_content = [stem_prefix(w) for w in content_tokens(sent, min_len=4)]
            d_content_set = set(d_content)

            best_rank: Tuple[bool, float] = (False, 0.0)
            best: Optional[Dict] = None

            for src in source_sentences:
                stoks, sstems, s_content = src["toks"], src["stems"], src["content"]
                shared_phrases = [g for g in d5 & src["grams"] if is_content_phrase(g)]
                longest_run = 0
                if shared_phrases:
                    longest_run = SequenceMatcher(None, dtoks, stoks, autojunk=False).find_longest_match(
                        0, len(dtoks), 0, len(stoks)
                    ).size
                seq_ratio = SequenceMatcher(None, dstems, sstems).ratio()

                union_len = len(d_content_set | src["content_set"]) or 1
                jaccard = len(d_content_set & src["content_set"]) / union_len

                # Structural synonym-swap signal: similar length, >=4 shared content stems in
                # the same order, an aligned function-word skeleton ("during ... than ... can"),
                # and anchors spread across the sentence rather than sitting in one phrase
                # (one phrase is a shared name or term, which the verbatim check covers).
                len_ratio = min(len(dtoks), len(stoks)) / max(len(dtoks), len(stoks))
                ordered_content_lcs = ordered_common_anchors(d_content, s_content)
                ordered_all_lcs = ordered_common_anchors(dstems, sstems)
                lcs_coverage = ordered_all_lcs / min(len(dstems), len(sstems))

                synonym_swap_hit = (
                    len_ratio >= 0.70
                    and ordered_content_lcs >= 4
                    and lcs_coverage >= 0.25
                    and anchor_clusters(d_content, s_content) >= 3
                )

                structural = seq_ratio >= 0.55 or (jaccard >= 0.50 and seq_ratio >= 0.38) or synonym_swap_hit
                if not (shared_phrases or structural):
                    continue

                is_high = structural or longest_run >= 8
                score = max(seq_ratio, jaccard, lcs_coverage, 0.75 if shared_phrases else 0.0)
                if (is_high, score) > best_rank:
                    best_rank = (is_high, score)
                    reasons = []
                    if shared_phrases:
                        reasons.append(f"verbatim run of {longest_run} words")
                    if synonym_swap_hit:
                        reasons.append(f"ordered structure alignment ({ordered_content_lcs} shared content anchors in order, {lcs_coverage:.0%} token-order match)")
                    elif structural:
                        reasons.append(f"sequence similarity {seq_ratio:.2f}")
                        reasons.append(f"content overlap {jaccard:.2f}")
                    best = {"src": src, "high": is_high, "reason": "; ".join(reasons)}

            if best:
                src_text = best["src"]["text"]
                quoted_source = f"\"{src_text[:140]}{'...' if len(src_text) > 140 else ''}\""
                if best["high"]:
                    message = (
                        f"Tracks source '{best['src']['name']}' closely ({best['reason']}). "
                        f"Source: {quoted_source}. "
                        "Rewrite from understanding without mirroring source syntax, or quote exact wording."
                    )
                else:
                    message = (
                        f"Shares a short phrase with source '{best['src']['name']}' ({best['reason']}). "
                        f"Source: {quoted_source}. "
                        "Fine if it is a name, title, or standard term; otherwise quote it or reword."
                    )
                findings.append({
                    "code": "CLOSE_PARAPHRASE_RISK",
                    "severity": "high" if best["high"] else "medium",
                    "location": f"Para {p['index']} (line {p['start_line']})",
                    "snippet": sent[:180] + ("..." if len(sent) > 180 else ""),
                    "message": message,
                })
    return findings


def analyze_draft(text: str, source_paths: Optional[List[Path]] = None) -> Dict:
    doc = parse_document(text)
    # Body = what the reader is argued at. Back matter, tables, and footnote / link
    # definitions are not part of the argument and are never scanned.
    paragraphs = [
        p for p in doc["paragraphs"]
        if not p["back_matter"] and p["kind"] not in ("table", "definition")
    ]
    # Scanned for tone; lists included.
    prose_paras = [p for p in paragraphs if p["kind"] in ("prose", "list")]
    # Candidates for the intro and the conclusion; a trailing list is neither.
    frame_paras = [p for p in paragraphs if p["kind"] == "prose"]
    findings: List[Dict] = []

    def count_words(paras: List[Dict]) -> int:
        return sum(len(re.findall(r"\b\w+\b", p["text"])) for p in paras)

    total_words = count_words(paragraphs)

    # 1. Intro Anti-Patterns (scan first 2 prose paragraphs)
    for p in frame_paras[:2]:
        for code, msg, pat in INTRO_PATTERNS:
            for m in pat.finditer(p["text"]):
                findings.append({
                    "code": code,
                    "severity": "high",
                    "location": f"Para {p['index']} (line {p['start_line']})",
                    "snippet": m.group(0),
                    "message": msg,
                })

    # 2. Hollow Importance Words
    for p in prose_paras:
        unquoted = strip_quotes(p["text"])
        for m in HOLLOW_IMPORTANCE_RE.finditer(unquoted):
            findings.append({
                "code": "HOLLOW_IMPORTANCE",
                "severity": "medium",
                "location": f"Para {p['index']} (line {p['start_line']})",
                "snippet": m.group(0),
                "message": "Asserts significance instead of showing it; replace with the substantive mechanism or stake.",
            })

    # 3. Organization by Number
    numeric_hits = []
    for p in prose_paras:
        m_open = NUMERIC_OPENER_RE.match(p["text"])
        if m_open:
            numeric_hits.append((p, m_open.group(0)))
        for m in NUMERIC_FRAMING_RE.finditer(strip_quotes(p["text"])):
            findings.append({
                "code": "NUMERIC_ORGANIZATION",
                "severity": "medium",
                "location": f"Para {p['index']} (line {p['start_line']})",
                "snippet": m.group(0),
                "message": "Check whether reasons have a substantive logical relationship rather than mere enumeration.",
            })
    if len(numeric_hits) >= 2:
        locs = ", ".join(f"Para {p['index']} ('{tok.strip()}')" for p, tok in numeric_hits)
        findings.append({
            "code": "NUMERIC_PROGRESSION",
            "severity": "medium",
            "location": locs,
            "snippet": " / ".join(tok.strip() for _, tok in numeric_hits),
            "message": "Multiple paragraphs open with numeric sequence markers; replace with conceptual transitions showing how claims build on each other.",
        })

    # 4. Tone Extremes: Strident Absolutes & Stacked Hedges
    for p in prose_paras:
        unquoted = strip_quotes(p["text"])
        for sent in split_sentences(unquoted):
            for m in STRIDENT_RE.finditer(sent):
                findings.append({
                    "code": "STRIDENT_CERTAINTY",
                    "severity": "medium",
                    "location": f"Para {p['index']} (line {p['start_line']})",
                    "snippet": m.group(0),
                    "message": f"Potentially unnuanced absolute in: \"{sent[:140]}{'...' if len(sent) > 140 else ''}\". Scope precisely instead of overstating.",
                })

            # Capitalized "May" is the month ("In May 2020"), not a hedge.
            hedges = [m.group(0) for m in SOFT_HEDGE_WORDS_RE.finditer(sent) if m.group(0) != "May"]
            mealy = [m.group(0) for m in MEALY_PHRASES_RE.finditer(sent)]
            if len(hedges) >= 3 or (len(hedges) >= 2 and mealy):
                findings.append({
                    "code": "MEALY_HEDGE_STACK",
                    "severity": "medium",
                    "location": f"Para {p['index']} (line {p['start_line']})",
                    "snippet": ", ".join(hedges),
                    "message": f"Stacked qualifiers weaken the sentence: \"{sent[:140]}{'...' if len(sent) > 140 else ''}\". Replace vague hedges with a single precise boundary.",
                })

    # 5. Potential Dropped / Unpacked Quotations
    for idx, p in enumerate(paragraphs):
        if p["is_blockquote"]:
            prev_text = paragraphs[idx - 1]["text"] if idx > 0 else ""
            next_text = paragraphs[idx + 1]["text"] if idx + 1 < len(paragraphs) else ""
            q_stems = {stem_prefix(w) for w in content_tokens(p["text"], min_len=5)}
            surrounding_stems = {stem_prefix(w) for w in content_tokens(prev_text + " " + next_text, min_len=5)}
            if q_stems and not (q_stems & surrounding_stems):
                findings.append({
                    "code": "UNPACKED_BLOCKQUOTE",
                    "severity": "high",
                    "location": f"Para {p['index']} (line {p['start_line']})",
                    "snippet": p["text"][:120] + ("..." if len(p["text"]) > 120 else ""),
                    "message": "Blockquote shares no echoed key terms with adjacent prose; unpack how this quotation counts as evidence.",
                })
            continue

        sents = split_sentences(p["text"])
        for s_idx, sent in enumerate(sents):
            spans = substantive_quote_spans(sent)
            own_words = remove_spans(sent, spans).strip(" .,;:()-")
            for start, end in spans:
                quoted = sent[start:end]
                q_text = sent[start + 1 : end - 1]
                q_words = re.findall(r"[a-zA-Z]+", q_text)
                if len(q_words) < 4:
                    continue
                if len(own_words.split()) <= 2:
                    findings.append({
                        "code": "DROPPED_QUOTE",
                        "severity": "high",
                        "location": f"Para {p['index']} (line {p['start_line']})",
                        "snippet": quoted[:120],
                        "message": "Quotation stands almost alone without analytical framing; integrate it into your own sentence and explain its warrant.",
                    })
                    continue
                next_sent = sents[s_idx + 1] if s_idx + 1 < len(sents) else ""
                context_prose = sent[:start] + " " + sent[end:] + " " + next_sent
                q_stems = {stem_prefix(w) for w in content_tokens(q_text, min_len=5)}
                c_stems = {stem_prefix(w) for w in content_tokens(context_prose, min_len=5)}
                if len(q_stems) >= 2 and not (q_stems & c_stems):
                    findings.append({
                        "code": "POTENTIAL_UNPACKED_QUOTE",
                        "severity": "medium",
                        "location": f"Para {p['index']} (line {p['start_line']})",
                        "snippet": quoted[:120],
                        "message": "Quoted passage has no echoed key words in surrounding prose; verify that you explicitly explain how it proves your claim.",
                    })

    # 6. Frame, Intro-to-Body Keyword Threading, & Title Check
    frame = {
        "title": doc["title"],
        "intro_tail_sentence": None,
        "conclusion_first_sentence": None,
        "conclusion_last_sentence": None,
        "intro_key_terms_threaded": {},
    }
    if frame_paras:
        intro_sents = split_sentences(frame_paras[0]["text"])
        if intro_sents:
            frame["intro_tail_sentence"] = intro_sents[-1]
            intro_terms = []
            seen = set()
            for w in content_tokens(intro_sents[-1], min_len=5):
                st = stem_prefix(w)
                if st not in seen:
                    seen.add(st)
                    intro_terms.append((w, st))
            body_paras = [p for p in prose_paras if p["index"] > frame_paras[0]["index"]]
            for word, st in intro_terms[:8]:
                hits = [
                    p["index"] for p in body_paras
                    if st in {stem_prefix(bw) for bw in content_tokens(p["text"], min_len=4)}
                ]
                frame["intro_key_terms_threaded"][word] = hits

        concl_sents = split_sentences(frame_paras[-1]["text"])
        if concl_sents:
            frame["conclusion_first_sentence"] = concl_sents[0]
            frame["conclusion_last_sentence"] = concl_sents[-1]

    if doc["title"]:
        if ":" not in doc["title"]:
            findings.append({
                "code": "SINGLE_PART_TITLE",
                "severity": "low",
                "location": "H1 Title",
                "snippet": doc["title"],
                "message": "Consider a two-part conceptual title (Concept Anchor: Specific Tension) drawn from your conclusion's key terms.",
            })
        body_text = " ".join(p["text"] for p in prose_paras)
        body_stems = set()
        for bw in content_tokens(body_text, min_len=4):
            body_stems.update(stem_variants(bw))
        title_words = content_tokens(doc["title"], min_len=5)
        missing_title_terms = sorted({
            w for w in title_words
            if not (set(stem_variants(w)) & body_stems)
        })
        if title_words and (len(missing_title_terms) / len(set(title_words))) >= 0.35:
            findings.append({
                "code": "UNANCHORED_TITLE_TERMS",
                "severity": "low",
                "location": "H1 Title",
                "snippet": ", ".join(missing_title_terms),
                "message": "Several concept words in the title do not prominently appear in the essay body; ensure the title previews central concepts.",
            })

    # 7. Close-Paraphrase Check (Optional)
    if source_paths:
        findings.extend(check_close_paraphrase(paragraphs, source_paths))

    severity_counts = {"high": 0, "medium": 0, "low": 0, "warning": 0}
    for f in findings:
        severity_counts[f["severity"]] = severity_counts.get(f["severity"], 0) + 1

    return {
        "stats": {
            "word_count": total_words,
            "paragraph_count": len(paragraphs),
            "prose_paragraph_count": len(prose_paras),
            "section_heading_count": len(doc["headings"]),
            "avg_words_per_prose_para": round(count_words(prose_paras) / len(prose_paras), 1) if prose_paras else 0,
        },
        "frame": frame,
        "severity_counts": severity_counts,
        "findings": findings,
    }


def render_markdown(report: Dict, target: str) -> str:
    s = report["stats"]
    c = report["severity_counts"]
    fr = report["frame"]

    out = [
        f"# Incisive Deterministic Scan: `{target}`",
        "",
        "## Document Snapshot",
        f"- **Words**: {s['word_count']} | **Paragraphs**: {s['prose_paragraph_count']} prose ({s['paragraph_count']} total) | **Subheadings**: {s['section_heading_count']} | **Avg words/para**: {s['avg_words_per_prose_para']}",
        f"- **Flags**: {c['high']} high | {c['medium']} medium | {c['low']} low",
        "",
        "## Frame Extraction (For Side-by-Side Claim Check)",
        f"- **Title**: {fr['title'] or '(none)'}",
        f"- **Intro closing sentence**: {fr['intro_tail_sentence'] or '(none)'}",
        f"- **Conclusion opening sentence**: {fr['conclusion_first_sentence'] or '(none)'}",
        f"- **Conclusion closing sentence**: {fr['conclusion_last_sentence'] or '(none)'}",
    ]

    if fr["intro_key_terms_threaded"]:
        thread_str = ", ".join(
            f"`{k}` -> {('Para ' + ','.join(map(str, v))) if v else 'NONE'}"
            for k, v in fr["intro_key_terms_threaded"].items()
        )
        out.append(f"- **Intro concept threading**: {thread_str}")

    out.extend(["", "## Mechanical Findings"])

    if not report["findings"]:
        out.append("- Zero mechanical flags detected.")
    else:
        for i, f in enumerate(report["findings"], start=1):
            out.append(
                f"{i}. **[{f['severity'].upper()}] `{f['code']}`** ({f['location']}) -- `{f['snippet']}`  \n"
                f"   {f['message']}"
            )
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic anti-slop & structural scanner for argumentative English drafts.")
    parser.add_argument("draft", type=Path, help="Path to the markdown or plain-text draft file.")
    parser.add_argument("--source", type=Path, action="append", default=[], help="Optional reference source file(s) to check for close paraphrase.")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format (default: md).")
    parser.add_argument("--strict", action="store_true", help="Exit with code 1 if any high-severity finding exists.")
    args = parser.parse_args()

    if not args.draft.is_file():
        reason = "is a directory, not a file" if args.draft.is_dir() else "not found"
        print(f"Error: draft {reason}: {args.draft}", file=sys.stderr)
        return 2

    # A missing source would silently skip the paraphrase check, so it is a hard error.
    missing_sources = [s for s in args.source if not s.is_file()]
    if missing_sources:
        for s in missing_sources:
            print(f"Error: source file not found: {s}", file=sys.stderr)
        return 2

    text = args.draft.read_text(encoding="utf-8", errors="ignore")
    report = analyze_draft(text, source_paths=args.source)

    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(report, str(args.draft)))

    if args.strict and report["severity_counts"]["high"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
