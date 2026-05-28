import importlib.util
import unittest
from pathlib import Path

import io
import os
import sys
import http.client
import tempfile
import contextlib
from unittest import mock

# ハイフン入りファイル名を import するため spec_from_file_location を使う
_MOD_PATH = Path(__file__).resolve().parents[1] / "tools" / "llms-txt-generator.py"
_spec = importlib.util.spec_from_file_location("llms_txt_generator", _MOD_PATH)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


class TestParseSitemap(unittest.TestCase):
    def test_extracts_loc_urls(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <url><loc>https://example.com/</loc></url>
          <url><loc>https://example.com/a/</loc></url>
        </urlset>"""
        self.assertEqual(
            m.parse_sitemap(xml),
            ["https://example.com/", "https://example.com/a/"],
        )

    def test_empty_sitemap_returns_empty_list(self):
        xml = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>'
        self.assertEqual(m.parse_sitemap(xml), [])

    def test_ignores_image_extension_loc(self):
        xml = """<?xml version="1.0"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
          <url><loc>https://example.com/p/</loc>
            <image:image><image:loc>https://cdn.example.com/i.jpg</image:loc></image:image>
          </url>
        </urlset>"""
        self.assertEqual(m.parse_sitemap(xml), ["https://example.com/p/"])

    def test_sitemapindex_returns_empty(self):
        xml = """<?xml version="1.0"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <sitemap><loc>https://example.com/sitemap-0.xml</loc></sitemap>
        </sitemapindex>"""
        self.assertEqual(m.parse_sitemap(xml), [])

    def test_parses_namespaceless_urlset(self):
        xml = "<urlset><url><loc>https://nons.example/</loc></url></urlset>"
        self.assertEqual(m.parse_sitemap(xml), ["https://nons.example/"])


class TestExtractTitleDesc(unittest.TestCase):
    def test_extracts_title_and_description(self):
        html = ('<html><head><title>My Page</title>'
                '<meta name="description" content="A short desc."></head></html>')
        self.assertEqual(m.extract_title_desc(html), ("My Page", "A short desc."))

    def test_missing_fields_return_none(self):
        self.assertEqual(m.extract_title_desc("<html><head></head></html>"),
                         (None, None))

    def test_single_quoted_description(self):
        html = ('<head><title>T</title>'
                '<meta name="description" content=\'single quoted\'></head>')
        self.assertEqual(m.extract_title_desc(html), ("T", "single quoted"))


class TestFormatLlmsTxt(unittest.TestCase):
    def test_formats_markdown(self):
        out = m.format_llms_txt(
            "My Site", "Site summary.",
            [("https://example.com/a/", "Page A", "Desc A")],
        )
        self.assertIn("# My Site", out)
        self.assertIn("> Site summary.", out)
        self.assertIn("- [Page A](https://example.com/a/): Desc A", out)

    def test_missing_title_falls_back_to_url(self):
        out = m.format_llms_txt("S", "", [("https://ex.com/p/", "", "")])
        self.assertIn("- [https://ex.com/p/](https://ex.com/p/)", out)
        self.assertNotIn("> ", out)  # empty summary -> no blockquote line

    def test_missing_desc_omits_suffix(self):
        out = m.format_llms_txt("S", "sum", [("https://ex.com/p/", "Title", "")])
        self.assertIn("- [Title](https://ex.com/p/)", out)
        self.assertNotIn("[Title](https://ex.com/p/):", out)  # no trailing ": desc"


class TestMainFetchFailure(unittest.TestCase):
    def test_all_fetches_fail_returns_2(self):
        sitemap = ('<?xml version="1.0"?>'
                   '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                   '<url><loc>https://example.com/a/</loc></url></urlset>')
        with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False,
                                         encoding="utf-8") as f:
            f.write(sitemap)
            path = f.name
        try:
            def boom(url, timeout=10):
                raise http.client.RemoteDisconnected("closed without response")
            argv = ["llms-txt-generator.py", path, "--site-name", "X"]
            with mock.patch.object(m, "_fetch", side_effect=boom), \
                 mock.patch.object(sys, "argv", argv):
                with contextlib.redirect_stdout(io.StringIO()), \
                     contextlib.redirect_stderr(io.StringIO()):
                    rc = m.main()
            self.assertEqual(rc, 2)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
