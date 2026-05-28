import importlib.util
import json
import unittest
from pathlib import Path

_MOD_PATH = Path(__file__).resolve().parents[1] / "tools" / "schema-faq-generator.py"
_spec = importlib.util.spec_from_file_location("schema_faq_generator", _MOD_PATH)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


class TestParseQa(unittest.TestCase):
    def test_parses_single_pair(self):
        text = "Q: What is X?\nA: X is a thing."
        self.assertEqual(m.parse_qa(text), [("What is X?", "X is a thing.")])

    def test_multiline_answer_until_next_q(self):
        text = "Q: Q1\nA: line1\nline2\nQ: Q2\nA: a2"
        self.assertEqual(
            m.parse_qa(text),
            [("Q1", "line1\nline2"), ("Q2", "a2")],
        )

    def test_ignores_blank_lines_between_blocks(self):
        text = "Q: Q1\nA: a1\n\nQ: Q2\nA: a2\n"
        self.assertEqual(m.parse_qa(text), [("Q1", "a1"), ("Q2", "a2")])


class TestBuildFaqpageJsonld(unittest.TestCase):
    def test_structure(self):
        d = m.build_faqpage_jsonld([("Q1", "a1")])
        self.assertEqual(d["@context"], "https://schema.org")
        self.assertEqual(d["@type"], "FAQPage")
        self.assertEqual(len(d["mainEntity"]), 1)
        q = d["mainEntity"][0]
        self.assertEqual(q["@type"], "Question")
        self.assertEqual(q["name"], "Q1")
        self.assertEqual(q["acceptedAnswer"], {"@type": "Answer", "text": "a1"})

    def test_json_is_valid_and_non_ascii_preserved(self):
        d = m.build_faqpage_jsonld([("表彰状とは?", "賞を授与する文書です。")])
        s = json.dumps(d, ensure_ascii=False)
        self.assertIn("表彰状とは?", s)


if __name__ == "__main__":
    unittest.main()
