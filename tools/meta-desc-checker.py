#!/usr/bin/env python3
"""
meta-desc-checker.py — meta description の文字数を全 HTML で監査

SEO/SERP 表示のためには meta description は 120〜160 文字程度が推奨。
このツールは指定ディレクトリ配下の全 HTML を再帰的に検査し、長さ
分布と「短すぎ」「長すぎ」のリストを出力する。

Usage:
    python3 meta-desc-checker.py /path/to/site
    python3 meta-desc-checker.py /path/to/site --min 120 --max 160

Exit code:
    0  全て適正範囲
    1  範囲外のページあり (CI 連携用)

Related article:
    https://note.com/honeymarron_dev/n/n8dfd69eda0fd
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

META_DESC_RE = re.compile(
    r'<meta\s+name=["\']description["\']\s+content="([^"]+)"',
    re.IGNORECASE,
)
HTML_ENTITY_MAP = {
    "&amp;": "&", "&#39;": "'", "&apos;": "'",
    "&quot;": '"', "&lt;": "<", "&gt;": ">",
}


def decode_entities(s: str) -> str:
    for k, v in HTML_ENTITY_MAP.items():
        s = s.replace(k, v)
    return s


def extract_meta_desc(html: str) -> str | None:
    m = META_DESC_RE.search(html)
    if not m:
        return None
    return decode_entities(m.group(1))


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit meta description lengths in HTML files.")
    parser.add_argument("target", help="Directory to scan recursively")
    parser.add_argument("--min", type=int, default=120, dest="min_len",
                        help="Minimum recommended length (default: 120)")
    parser.add_argument("--max", type=int, default=160, dest="max_len",
                        help="Maximum recommended length (default: 160)")
    parser.add_argument("--exclude", action="append", default=[],
                        help="Path substring to exclude (can be repeated)")
    args = parser.parse_args()

    target = Path(args.target)
    if not target.is_dir():
        print(f"Error: {target} is not a directory", file=sys.stderr)
        return 2

    out_of_range = []
    in_range = 0
    no_meta = []

    for html_path in sorted(target.rglob("*.html")):
        rel = html_path.relative_to(target).as_posix()
        if any(ex in rel for ex in args.exclude):
            continue
        try:
            text = html_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"Warning: failed to read {rel}: {e}", file=sys.stderr)
            continue
        desc = extract_meta_desc(text)
        if desc is None:
            no_meta.append(rel)
            continue
        length = len(desc)
        if args.min_len <= length <= args.max_len:
            in_range += 1
        else:
            out_of_range.append((length, rel, desc))

    print(f"=== meta description audit ({target}) ===")
    print(f"Recommended range: {args.min_len}〜{args.max_len} chars")
    print(f"  In range: {in_range}")
    print(f"  Out of range: {len(out_of_range)}")
    print(f"  Missing meta desc: {len(no_meta)}")
    print()

    if out_of_range:
        print("--- Out of range (sorted by length) ---")
        for length, rel, desc in sorted(out_of_range):
            tag = "TOO SHORT" if length < args.min_len else "TOO LONG"
            print(f"  [{tag}] {length:4d}  {rel}")
        print()

    if no_meta:
        print("--- Missing meta description ---")
        for rel in no_meta:
            print(f"  {rel}")
        print()

    return 1 if out_of_range or no_meta else 0


if __name__ == "__main__":
    sys.exit(main())
