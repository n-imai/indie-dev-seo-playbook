#!/usr/bin/env python3
"""
twin-fields-check.py — title/description の twin fields 同期検証

ページタイトル・description は通常以下の複数箇所に書く必要がある:
  - <title> / <meta name="description">
  - <meta property="og:title"> / <meta property="og:description">
  - <meta name="twitter:title"> / <meta name="twitter:description">
  - JSON-LD schema の name / description / headline

これらが「片方だけ更新されている」と SNS preview / SERP / AI 検索で
表示が不一致になる。このツールは全 HTML で twin fields のズレを検出
する。

Usage:
    python3 twin-fields-check.py /path/to/site
    python3 twin-fields-check.py /path/to/site --check title
    python3 twin-fields-check.py /path/to/site --check description

Exit code:
    0  全て同期済み
    1  不一致あり (CI 連携用)

Related article:
    https://note.com/honeymarron_dev/n/n8dfd69eda0fd
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TITLE_RE = re.compile(r"<title>([^<]+)</title>", re.IGNORECASE)
OG_TITLE_RE = re.compile(r'<meta\s+property=["\']og:title["\']\s+content="([^"]+)"', re.IGNORECASE)
TW_TITLE_RE = re.compile(r'<meta\s+name=["\']twitter:title["\']\s+content="([^"]+)"', re.IGNORECASE)

META_DESC_RE = re.compile(r'<meta\s+name=["\']description["\']\s+content="([^"]+)"', re.IGNORECASE)
OG_DESC_RE = re.compile(r'<meta\s+property=["\']og:description["\']\s+content="([^"]+)"', re.IGNORECASE)
TW_DESC_RE = re.compile(r'<meta\s+name=["\']twitter:description["\']\s+content="([^"]+)"', re.IGNORECASE)

# JSON-LD blocks
JSONLD_RE = re.compile(
    r'<script\s+type=["\']application/ld\+json["\']\s*>(.+?)</script>',
    re.IGNORECASE | re.DOTALL,
)

ENT = {"&amp;": "&", "&#39;": "'", "&apos;": "'", "&quot;": '"', "&lt;": "<", "&gt;": ">"}


def decode(s: str) -> str:
    for k, v in ENT.items():
        s = s.replace(k, v)
    return s.strip()


def first(pattern: re.Pattern, html: str) -> str | None:
    m = pattern.search(html)
    return decode(m.group(1)) if m else None


def extract_jsonld_fields(html: str) -> dict[str, list[str]]:
    """Returns dict mapping field name → list of values found in JSON-LD blocks."""
    result: dict[str, list[str]] = {"name": [], "headline": [], "description": []}
    for m in JSONLD_RE.finditer(html):
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        for obj in (data if isinstance(data, list) else [data]):
            if not isinstance(obj, dict):
                continue
            for field in ("name", "headline", "description"):
                v = obj.get(field)
                if isinstance(v, str):
                    result[field].append(v)
    return result


def check_file(path: Path, mode: str) -> list[str]:
    """Returns list of mismatch messages for this file."""
    html = path.read_text(encoding="utf-8", errors="replace")
    issues: list[str] = []
    jsonld = extract_jsonld_fields(html)

    if mode in ("title", "all"):
        t = first(TITLE_RE, html)
        og = first(OG_TITLE_RE, html)
        tw = first(TW_TITLE_RE, html)
        ld_names = jsonld["name"] + jsonld["headline"]
        # 同一であることを確認するが、JSON-LD の name は entity name (Site/App) の可能性
        # もあるので headline と完全一致を強要せず、og/twitter の二者と title の三つ巴で比較
        vals = {"title": t, "og:title": og, "twitter:title": tw}
        present = {k: v for k, v in vals.items() if v}
        if len(set(present.values())) > 1:
            lines = ["  Title mismatch:"]
            for k, v in present.items():
                lines.append(f"    {k}: {v[:80]}")
            issues.append("\n".join(lines))

    if mode in ("description", "all"):
        md = first(META_DESC_RE, html)
        og = first(OG_DESC_RE, html)
        tw = first(TW_DESC_RE, html)
        ld_descs = jsonld["description"]
        vals = {"meta:description": md, "og:description": og, "twitter:description": tw}
        for i, ld_desc in enumerate(ld_descs):
            vals[f"jsonld:description[{i}]"] = ld_desc
        present = {k: v for k, v in vals.items() if v}
        if len(set(present.values())) > 1:
            lines = ["  Description mismatch:"]
            for k, v in present.items():
                short = v[:80] + ("..." if len(v) > 80 else "")
                lines.append(f"    {k} ({len(v)} chars): {short}")
            issues.append("\n".join(lines))

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify twin fields sync (title/description across meta/og/twitter/jsonld).")
    parser.add_argument("target", help="Directory to scan recursively")
    parser.add_argument("--check", choices=["title", "description", "all"], default="all",
                        help="What to check (default: all)")
    parser.add_argument("--exclude", action="append", default=[],
                        help="Path substring to exclude (can be repeated)")
    args = parser.parse_args()

    target = Path(args.target)
    if not target.is_dir():
        print(f"Error: {target} is not a directory", file=sys.stderr)
        return 2

    total = 0
    bad = 0
    for html_path in sorted(target.rglob("*.html")):
        rel = html_path.relative_to(target).as_posix()
        if any(ex in rel for ex in args.exclude):
            continue
        total += 1
        issues = check_file(html_path, args.check)
        if issues:
            bad += 1
            print(f"=== {rel} ===")
            for issue in issues:
                print(issue)
            print()

    print(f"=== twin fields sync ({args.check}) ===")
    print(f"  Checked: {total}")
    print(f"  Mismatches: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
