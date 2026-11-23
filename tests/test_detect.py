"""Regression tests for skills/incisive/scripts/detect.py (stdlib unittest only).

Run from the repo root:
    python3 -m unittest discover -s tests -v
"""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DETECT = REPO / "skills" / "incisive" / "scripts" / "detect.py"

_spec = importlib.util.spec_from_file_location("detect", DETECT)
detect = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(detect)


def codes(report):
    return [f["code"] for f in report["findings"]]


def scan_with_source(draft: str, source: str):
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "source.txt"
        src.write_text(source, encoding="utf-8")
        return detect.analyze_draft(draft, source_paths=[src])


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(DETECT), *map(str, args)],
        capture_output=True,
        text=True,
    )


class FrontmatterTests(unittest.TestCase):
    DRAFT = (
        "---\n"
        'title: "Throughout history: a post"\n'
        "date: 2026-11-01\n"
        "---\n"
        "\n"
        "# Repricing Bots: Why Discounts Stop Paying\n"
        "\n"
        "Repricing bots are praised for sharpening competition. Yet prices drift upward where bots dominate.\n"
        "\n"
        "Repricing removes the temporary advantage of undercutting, so discounts stop paying.\n"
    )

    def test_frontmatter_is_not_the_intro_paragraph(self):
        report = detect.analyze_draft(self.DRAFT)
        self.assertEqual(
            report["frame"]["intro_tail_sentence"],
            "Yet prices drift upward where bots dominate.",
        )

    def test_frontmatter_text_raises_no_findings(self):
        report = detect.analyze_draft(self.DRAFT)
        self.assertEqual(codes(report), [])

    def test_line_numbers_still_count_frontmatter_lines(self):
        report = detect.analyze_draft(self.DRAFT.replace("Repricing bots are praised", "Throughout history, bots are praised"))
        platitudes = [f for f in report["findings"] if f["code"] == "GRAND_PLATITUDE"]
        self.assertEqual(len(platitudes), 1)
        self.assertIn("line 8", platitudes[0]["location"])


class BackMatterTests(unittest.TestCase):
    BODY = (
        "# Repricing Bots: Why Discounts Stop Paying\n"
        "\n"
        "Repricing bots are praised for sharpening competition, yet prices drift upward where bots dominate.\n"
        "\n"
        "Repricing removes the advantage of undercutting, so discounts stop paying.\n"
        "\n"
    )

    def test_references_section_is_not_the_conclusion(self):
        draft = self.BODY + (
            "## References\n"
            "\n"
            "- Smith, J. (2020). Pricing. Journal of Things.\n"
            "- Doe, A. (2021). Bots. Another Journal.\n"
        )
        report = detect.analyze_draft(draft)
        self.assertEqual(
            report["frame"]["conclusion_last_sentence"],
            "Repricing removes the advantage of undercutting, so discounts stop paying.",
        )

    def test_quoted_titles_in_references_are_not_dropped_quotes(self):
        draft = self.BODY + (
            "## Works Cited\n"
            "\n"
            'Smith, J. "Algorithmic Pricing and the Quiet End of Discounting." 2020.\n'
        )
        self.assertEqual(codes(detect.analyze_draft(draft)), [])

    def test_trailing_footnote_definitions_are_not_the_conclusion(self):
        draft = self.BODY + "[^1]: Smith, J. (2020). Pricing. Journal of Things.\n"
        report = detect.analyze_draft(draft)
        self.assertEqual(
            report["frame"]["conclusion_last_sentence"],
            "Repricing removes the advantage of undercutting, so discounts stop paying.",
        )

    def test_trailing_bullet_list_is_not_the_conclusion(self):
        draft = self.BODY + "- Related post one\n- Related post two\n"
        report = detect.analyze_draft(draft)
        self.assertEqual(
            report["frame"]["conclusion_last_sentence"],
            "Repricing removes the advantage of undercutting, so discounts stop paying.",
        )


class CodeFenceTests(unittest.TestCase):
    def test_tilde_fenced_code_is_not_scanned(self):
        draft = "# A: B\n\nCaches trade memory for latency.\n\n~~~\nObviously everyone knows this.\n~~~\n"
        self.assertEqual(codes(detect.analyze_draft(draft)), [])


class QuoteTests(unittest.TestCase):
    def test_prose_between_two_short_quotes_is_not_a_quotation(self):
        draft = (
            "# A: B\n\n"
            'The manager said "no" and then walked away from the negotiating table '
            'before the "deal" could be signed by anyone.\n'
        )
        self.assertEqual(codes(detect.analyze_draft(draft)), [])

    def test_multi_sentence_quote_standing_alone_is_a_dropped_quote(self):
        draft = (
            "# A: B\n\n"
            "Monitoring covered uptime but not correctness.\n\n"
            '"The system failed quietly. Nobody noticed the drift until the invoices bounced."\n\n'
            "Billing errors therefore surfaced through customers.\n"
        )
        self.assertIn("DROPPED_QUOTE", codes(detect.analyze_draft(draft)))

    def test_multi_sentence_quote_with_echoed_terms_is_not_flagged(self):
        draft = (
            "# A: B\n\n"
            'The postmortem is blunt: "The system failed quietly. Nobody noticed the drift '
            'until the invoices bounced." That quiet failure, and the drift nobody noticed, '
            "is the argument for correctness alerts.\n"
        )
        self.assertEqual(codes(detect.analyze_draft(draft)), [])

    def test_sentence_after_a_closing_quote_is_split_off(self):
        sents = detect.split_sentences('She wrote, "It failed. Nobody noticed." Then the chapter ends.')
        self.assertEqual(sents, ['She wrote, "It failed. Nobody noticed."', "Then the chapter ends."])

    def test_inch_mark_does_not_open_a_quotation(self):
        draft = (
            "# A: B\n\n"
            'The 5" drive was replaced by the smaller form factor within three product cycles, '
            'and the 3" variant never shipped in volume at all.\n'
        )
        self.assertEqual(codes(detect.analyze_draft(draft)), [])


class ToneTests(unittest.TestCase):
    def test_month_of_may_is_not_a_hedge(self):
        draft = "# A: B\n\nIn May 2020 the team could ship weekly, and by June it might scale further.\n"
        self.assertNotIn("MEALY_HEDGE_STACK", codes(detect.analyze_draft(draft)))

    def test_lowercase_may_still_counts_as_a_hedge(self):
        draft = "# A: B\n\nThe result may perhaps be somewhat unclear.\n"
        self.assertIn("MEALY_HEDGE_STACK", codes(detect.analyze_draft(draft)))

    def test_simply_vanished_is_strident(self):
        draft = "# A: B\n\nAfter the migration, deployment bottlenecks have simply vanished.\n"
        self.assertIn("STRIDENT_CERTAINTY", codes(detect.analyze_draft(draft)))


class StemTests(unittest.TestCase):
    def test_words_sharing_a_long_latin_prefix_do_not_collide(self):
        self.assertNotEqual(detect.stem_prefix("interest"), detect.stem_prefix("internal"))
        self.assertNotEqual(detect.stem_prefix("contract"), detect.stem_prefix("contrast"))
        self.assertNotEqual(detect.stem_prefix("transfer"), detect.stem_prefix("transparency"))

    def test_inflections_still_share_a_stem(self):
        self.assertEqual(detect.stem_prefix("interesting"), detect.stem_prefix("interest"))
        self.assertEqual(detect.stem_prefix("contracts"), detect.stem_prefix("contract"))
        self.assertEqual(detect.stem_prefix("governance"), detect.stem_prefix("govern"))


class StatsTests(unittest.TestCase):
    def test_average_words_per_prose_paragraph_excludes_blockquotes(self):
        draft = "# A: B\n\none two three four\n\n> five six seven eight nine ten\n\none two three four\n"
        self.assertEqual(detect.analyze_draft(draft)["stats"]["avg_words_per_prose_para"], 4.0)


class ParaphraseTests(unittest.TestCase):
    SOURCE = (
        "Because institutional memory erodes faster during rapid turnover than formal handbooks can capture, "
        "teams that rely exclusively on written wikis mistake archived decisions for shared judgment.\n"
    )

    def paraphrase_findings(self, draft, source):
        report = scan_with_source("# A: B\n\n" + draft + "\n", source)
        return [f for f in report["findings"] if f["code"] == "CLOSE_PARAPHRASE_RISK"]

    def test_synonym_swap_paraphrase_is_high(self):
        found = self.paraphrase_findings(
            "Since organizational memory fades more quickly during fast staff turnover than official manuals "
            "can record, groups relying solely on documented wikis confuse stored choices with collective judgment.",
            self.SOURCE,
        )
        self.assertEqual([f["severity"] for f in found], ["high"])

    def test_summary_from_understanding_is_not_flagged(self):
        found = self.paraphrase_findings(
            "As Author (2025) observes, static documentation cannot substitute for lived team judgment "
            "when high staff attrition outpaces what gets written down.",
            self.SOURCE,
        )
        self.assertEqual(found, [])

    def test_shared_function_word_phrase_is_not_flagged(self):
        found = self.paraphrase_findings(
            "At the end of the sprint, engineers demo unfinished work to stakeholders anyway.",
            "At the end of the quarter the finance group closed its books early.\n",
        )
        self.assertEqual(found, [])

    def test_single_shared_name_phrase_is_medium_not_high(self):
        found = self.paraphrase_findings(
            "The method borrows from Joseph Williams and Lawrence McEnerney while changing nearly "
            "everything else about delivery.",
            "Joseph Williams and Lawrence McEnerney wrote a guide for college writers decades ago.\n",
        )
        self.assertEqual([f["severity"] for f in found], ["medium"])

    def test_long_verbatim_run_is_high(self):
        found = self.paraphrase_findings(
            "Critics note that teams that rely exclusively on written wikis mistake archived decisions "
            "for something far more durable than it is.",
            self.SOURCE,
        )
        self.assertEqual([f["severity"] for f in found], ["high"])


class CliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.clean = self.tmp / "clean.md"
        self.clean.write_text(
            "# A: B\n\nCaches trade memory for latency, and the trade fails when invalidation costs more than recomputation.\n",
            encoding="utf-8",
        )

    def test_clean_draft_exits_zero_under_strict(self):
        self.assertEqual(run_cli(self.clean, "--strict").returncode, 0)

    def test_high_finding_exits_one_under_strict(self):
        bad = self.tmp / "bad.md"
        bad.write_text("# A: B\n\nIn this essay, I will discuss caching.\n", encoding="utf-8")
        self.assertEqual(run_cli(bad, "--strict").returncode, 1)

    def test_missing_source_file_is_an_error(self):
        result = run_cli(self.clean, "--strict", "--source", self.tmp / "nope.txt")
        self.assertEqual(result.returncode, 2)
        self.assertIn("nope.txt", result.stderr)

    def test_directory_as_draft_is_an_error_without_traceback(self):
        result = run_cli(self.tmp)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
