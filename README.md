# Indie Dev SEO Playbook

> ChatGPT / Claude / Perplexity 時代の個人開発者向け SEO/ASO 実践集
>
> 個人開発で iOS アプリ 2 本を 175 カ国に流通させた [honeymarron](https://honeymarron.com) が、SEO・ASO・AI 検索対応で実際に効いた施策を備忘録としてまとめています。

[English version is planned — Japanese first because most learnings were derived in JP/EN bilingual context.]

## なぜこの Playbook を作ったか

ChatGPT・Claude・Perplexity の登場で、検索流入の構造は静かに変わりました。

- Google だけでなく **Bing** — リアルタイムの AI 引用（Copilot / ChatGPT Search / Perplexity）の主な grounding source はここ。**AI 検索対応の本命**
- **Common Crawl** — LLM 学習データの主要ソースの一つ。**リアルタイムの AI 引用とは別経路**で、ラグは数ヶ月〜年単位・効果は不確実
- **llms.txt** (AI 向けのサイト要約仕様 — ただし現状 AI 検索エンジンはほぼ参照しておらず、効果は不確実)

への対応と「何が効いて何がまだ効かないか」の見極めが、これからの個人開発者には重要です。

しかし「個人開発者が一人でできる現実的な施策」のまとまった資料が見当たりません。Google Search Console と sitemap.xml の話までは Web に大量にあるけれど、その先 (Bing Webmaster Tools の本気の使い方、AI 検索向けの構造化、AI 引用の実測方法) を一気通貫で書いた資料は少ない。

このリポは、`honeymarron.com` 運営で実際に試して効いた / 効かなかった施策を、Before/After の数字とコマンド付きで書き残しています。

## 開発者の実績 (2026-05 時点)

- [**表彰状クリエイター**](https://apps.apple.com/jp/app/id6748368413) — 175 カ国流通 / App Store ★4.3
- [**VoicyCare**](https://apps.apple.com/jp/app/id6749561636) — 175 カ国流通 / App Store ★5.0
- 公式サイト: [honeymarron.com](https://honeymarron.com) — Vercel + バニラ HTML/CSS

すべて個人で企画・開発・運営。Tech stack: Flutter / Swift / Ruby on Rails / Node.js / TypeScript / Go / AWS。

## Table of Contents

### Published

- **01. Bing Webmaster Tools 活用ガイド — Google だけ見てると見落とすもの** — [note で読む](https://note.com/honeymarron_dev/n/n8dfd69eda0fd) / [リポ内 summary](chapters/01-bing-webmaster-tools.md)
- **02. GEO — AI 検索に引用される実装（ChatGPT / Copilot / Perplexity）** — [note で読む](https://note.com/honeymarron_dev/n/nf2ed909fa321) / [リポ内 summary](chapters/02-geo-ai-search-citation.md)

## Tools

note 記事で言及した監査タスクを実行可能な形にしたツール群が [`tools/`](tools/README.md) にあります。

- [`meta-desc-checker.py`](tools/meta-desc-checker.py) — meta description 長さ監査
- [`twin-fields-check.py`](tools/twin-fields-check.py) — meta/og/twitter/JSON-LD の同期検証
- [`common-crawl-check.sh`](tools/common-crawl-check.sh) — Common Crawl（LLM 学習データ）収録確認 ※AI 検索引用の診断ツールではありません（[理由](tools/README.md#cc-scope)）
- [`bing-resubmit.sh`](tools/bing-resubmit.sh) — Bing Webmaster URL 一括再送信
- [`llms-txt-generator.py`](tools/llms-txt-generator.py) — sitemap.xml から llms.txt skeleton 生成
- [`schema-faq-generator.py`](tools/schema-faq-generator.py) — Q&A テキストから FAQPage JSON-LD 生成

すべて単一ファイル・標準ライブラリのみで動作。`git clone` してそのまま自分のサイトに対して走らせられます。詳細は [`tools/README.md`](tools/README.md)。

### Backlog（時期未定）

書く予定のトピック。**執筆時期は約束しません**（このリポは実運用の副産物として不定期に更新しています）。

- 03. meta タグの twin fields 同期 — JSON-LD / og: / twitter: の罠
- 04. www → non-www の 301 化 — Vercel Dashboard と vercel.json の優先順位
- 05. AI 引用を実測する — Bing Webmaster "AI Performance" の読み方と、Common Crawl を成果指標にしてはいけない理由
- 06. ASC `ct` パラメータの分離設計 — `lp_hero` / `lp_main` / `lp_footer` で fold above/below を計測する
- 07. 多言語対応の落とし穴 — App Store URL の `/jp/` パスと `l=en` パラメータの罠
- 08. GA4 / GSC / Bing / DataForSEO の測定スタック — 1 ソースだけでは見えない真実（と、小母数では何が判定不能か）

> 章はランダム順ではなく **「個人開発者が日次・週次・月次で取り組むべき順」** に並べています。01 から順に読むと、無理なくセットアップが完了する想定。

## License

| 対象 | License | ファイル |
|---|---|---|
| コード（`tools/` の `*.py` / `*.sh`, `tests/`）| **MIT** | [`LICENSE`](LICENSE) |
| 文章・ドキュメント（README, `chapters/`, `tools/README.md`）| **CC BY 4.0** | [`LICENSE-DOCS`](LICENSE-DOCS) |

コードを CC ではなく MIT にしているのは、[Creative Commons 自身がソフトウェアへの CC 適用を推奨していない](https://creativecommons.org/faq/#can-i-apply-a-creative-commons-license-to-software)ためです。

どちらも引用・転載・改変・商用利用 OK。条件だけ守ってください。

- **文章（CC BY 4.0）** — attribution（出典表記）。下記の推奨表記を使えば OK
- **コード（MIT）** — 実質的な部分を再配布する場合は、**著作権表示と MIT 許諾文（[`LICENSE`](LICENSE) 全文）の両方**を同梱

文章を引用する場合の推奨表記:

> "Indie Dev SEO Playbook" by honeymarron ([honeymarron.com](https://honeymarron.com)),
> licensed under CC BY 4.0.
> Source: https://github.com/n-imai/indie-dev-seo-playbook

## Author

[honeymarron](https://honeymarron.com) — 日本を拠点とする個人 iOS アプリ開発者・フルスタックソフトウェアエンジニア。GitHub: [@n-imai](https://github.com/n-imai)
