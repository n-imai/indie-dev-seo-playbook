#!/usr/bin/env python3
"""
llms-txt-generator.py — sitemap.xml から llms.txt の skeleton を生成

AI クローラー (ChatGPT/Claude/Perplexity 等) 向けにサイト構造を要約する
llms.txt (https://llmstxt.org/) の下書きを、既存の sitemap.xml と各ページの
<title> / <meta description> から自動生成する。生成後は人手で要約を磨く前提。

Usage:
    # ローカルの sitemap.xml + 各 URL をネット取得
    python3 llms-txt-generator.py sitemap.xml --site-name "My Site" --summary "..."
    # 取得せず URL/title だけ並べる (--no-fetch)
    python3 llms-txt-generator.py sitemap.xml --site-name "My Site" --no-fetch

Exit code:
    0  生成成功
    2  入力エラー

Related article:
    (note 第二弾 GEO 記事 — 公開後に URL を記入)
"""
from __future__ import annotations

import argparse
import http.client
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

_SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

# 注意: title/description は正規表現ベースの heuristic 抽出。第三者ページでは
# 属性順 (content 先) や name/content 間の別属性、<script> 内の <title> 等で
# 取りこぼす場合がある。skeleton 生成後の人手チェックを前提とする。
_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_DESC_RE = re.compile(
    r'<meta\s+name=["\']description["\']\s+content=(["\'])(.*?)\1',
    re.IGNORECASE,
)


def parse_sitemap(xml: str) -> list[str]:
    """sitemap.xml 文字列から <loc> の URL を取り出す。

    sitemap 標準名前空間 (0.9) と名前空間なしの <loc> を対象とする。image:/video:/news: 拡張の
    <loc> は別名前空間なので除外される。sitemapindex (子 sitemap を列挙する
    ファイル) が渡された場合は対象外なので警告して空リストを返す。
    """
    root = ET.fromstring(xml)
    local_root = root.tag.split("}")[-1] if "}" in root.tag else root.tag
    if local_root == "sitemapindex":
        print("Warning: sitemap index detected; run against a leaf sitemap",
              file=sys.stderr)
        return []
    locs = []
    # 名前空間付き (標準) と 名前空間なし の両方の <loc> を拾う (image:loc 等は除外)
    for tag in (f"{{{_SITEMAP_NS}}}loc", "loc"):
        for el in root.iter(tag):
            if el.text:
                locs.append(el.text.strip())
    return locs


def extract_title_desc(html: str) -> tuple[str | None, str | None]:
    """HTML 文字列から (title, meta description) を取り出す。無ければ None。"""
    t = _TITLE_RE.search(html)
    d = _DESC_RE.search(html)
    title = t.group(1).strip() if t else None
    desc = d.group(2).strip() if d else None
    return (title, desc)


def format_llms_txt(site_name: str, site_summary: str,
                    entries: list[tuple[str, str, str]]) -> str:
    """llms.txt 形式の Markdown を組み立てる。entries は (url, title, desc)。"""
    lines = [f"# {site_name}", ""]
    if site_summary:
        lines += [f"> {site_summary}", ""]
    lines += ["## Pages", ""]
    for url, title, desc in entries:
        label = title or url
        suffix = f": {desc}" if desc else ""
        lines.append(f"- [{label}]({url}){suffix}")
    return "\n".join(lines) + "\n"


def _fetch(url: str, timeout: int = 10) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "llms-txt-generator"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate an llms.txt skeleton from a sitemap.xml.")
    parser.add_argument("sitemap", help="Path to local sitemap.xml")
    parser.add_argument("--site-name", required=True, help="Site name for the H1")
    parser.add_argument("--summary", default="", help="One-line site summary")
    parser.add_argument("--no-fetch", action="store_true",
                        help="Do not fetch pages; emit URLs/titles only")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max URLs to include (0 = all)")
    args = parser.parse_args()

    path = Path(args.sitemap)
    if not path.is_file():
        print(f"Error: {path} is not a file", file=sys.stderr)
        return 2

    try:
        urls = parse_sitemap(path.read_text(encoding="utf-8"))
    except ET.ParseError as e:
        print(f"Error: {path} is not valid XML: {e}", file=sys.stderr)
        return 2
    if args.limit > 0:
        urls = urls[: args.limit]

    if not urls:
        print("Error: no <loc> URLs found in sitemap", file=sys.stderr)
        return 2

    entries: list[tuple[str, str, str]] = []
    fetch_attempts = 0
    fetch_failures = 0
    for url in urls:
        title, desc = ("", "")
        if not args.no_fetch:
            fetch_attempts += 1
            html = None
            try:
                html = _fetch(url)
            except (urllib.error.URLError, http.client.HTTPException,
                    TimeoutError, OSError, ValueError) as e:
                fetch_failures += 1
                print(f"Warning: failed to fetch {url}: {e}", file=sys.stderr)
            if html is not None:
                t, d = extract_title_desc(html)
                title, desc = (t or ""), (d or "")
        entries.append((url, title, desc))

    if fetch_attempts > 0 and fetch_failures == fetch_attempts:
        print(f"Error: all {fetch_attempts} page fetches failed; "
              f"no titles/descriptions extracted", file=sys.stderr)
        return 2
    if fetch_failures:
        print(f"Note: {fetch_failures}/{fetch_attempts} page fetches failed",
              file=sys.stderr)

    print(format_llms_txt(args.site_name, args.summary, entries))
    return 0


if __name__ == "__main__":
    sys.exit(main())
