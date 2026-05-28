#!/usr/bin/env python3
"""
schema-faq-generator.py — Q&A テキストから FAQPage JSON-LD を生成

シンプルな Q:/A: 形式のテキストを読み、schema.org FAQPage の JSON-LD を出力する。
AI 検索 (ChatGPT/Perplexity 等) は Q&A 構造を passage 単位で引用しやすいため、
記事末尾の FAQ を構造化するのに使う。出力は HTML の <script type="application/ld+json">
にそのまま貼れる。

入力形式 (例):
    Q: 表彰状の敬称は?
    A: 個人なら「殿」または「様」、団体なら「御中」を使います。
    複数行で書いても次の Q: までが 1 つの回答になります。

    Q: 句読点は付ける?
    A: 賞状本文では句読点を省くのが慣例です。

Usage:
    python3 schema-faq-generator.py faq.txt
    python3 schema-faq-generator.py - < faq.txt   # 標準入力

Exit code:
    0  生成成功
    2  入力エラー (Q&A ペアが 0 件)

Related article:
    (note 第二弾 GEO 記事 — 公開後に URL を記入)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_qa(text: str) -> list[tuple[str, str]]:
    """Q:/A: 形式のテキストを (question, answer) のリストに変換する。"""
    pairs: list[tuple[str, str]] = []
    question: str | None = None
    answer_lines: list[str] = []

    def flush() -> None:
        if question is not None and answer_lines:
            pairs.append((question, "\n".join(answer_lines).strip()))

    for raw in text.splitlines():
        line = raw.rstrip("\n")
        if line.startswith("Q:"):
            flush()
            question = line[2:].strip()
            answer_lines = []
        elif line.startswith("A:"):
            answer_lines = [line[2:].strip()]
        elif question is not None and answer_lines:
            if line.strip() == "":
                continue
            answer_lines.append(line)
    flush()
    return pairs


def build_faqpage_jsonld(qa_pairs: list[tuple[str, str]]) -> dict:
    """(q, a) のリストから schema.org FAQPage の dict を組み立てる。"""
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in qa_pairs
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate FAQPage JSON-LD from Q:/A: text.")
    parser.add_argument("input", help="Path to Q&A text file, or '-' for stdin")
    args = parser.parse_args()

    if args.input == "-":
        text = sys.stdin.read()
    else:
        path = Path(args.input)
        if not path.is_file():
            print(f"Error: {path} is not a file", file=sys.stderr)
            return 2
        text = path.read_text(encoding="utf-8")

    pairs = parse_qa(text)
    if not pairs:
        print("Error: no Q:/A: pairs found", file=sys.stderr)
        return 2

    jsonld = build_faqpage_jsonld(pairs)
    print(json.dumps(jsonld, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
