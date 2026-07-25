# 02. GEO — AI 検索に引用される実装（ChatGPT / Copilot / Perplexity）

> 📝 **本文は note で公開しています**
>
> [個人開発者が AI 検索に引用されるためにやったこと — Bing の次のステップ](https://note.com/honeymarron_dev/n/nf2ed909fa321)

---

## 概要

個人開発者が AI 検索 (ChatGPT/Copilot/Perplexity) に引用されるための実装ノウハウをまとめた章です。第一弾「Bing から始める」の続編であり、Bing で indexed になることが Copilot に引用される前提条件になります。`honeymarron.com` では llms.txt の設置・FAQPage schema を 71 ページに展開・passage 単位で引用されやすい文章構造を実装しました。直近 2 週間で Copilot からの referral が 2 件観測できています（n=2 の兆候レベルであり、効果が出たとは言えない段階です）。

### この章でカバーする内容

- なぜ今 GEO か（AI 検索は答えを合成し引用元を出す / 新規ドメインでも情報の質で拾われる余地）
- 施策1: llms.txt を置く
- 施策2: 引用されやすい文章構造（passage-level citability）
- 施策3: FAQPage schema で passage を機械可読にする
- 施策4: 外部認知の壁 — Common Crawl（**※下記の訂正を参照**）
- 効果はどう測るか（GA4 で copilot.com referral、(direct) に紛れる AI 流入）
- GEO チェックリスト

→ **続きは note 記事でお読みください。**

---

## ⚠ 訂正（2026-07-25）— Common Crawl は AI 検索引用の前提条件ではない

上記 note 記事の「施策4: 外部認知の壁 — Common Crawl」は、**Common Crawl 未収録が AI 検索に引用されない原因**だという前提で書いています。**この前提は誤りでした。**その後の実測で否定されたので、ここに訂正を残します。

**何が違ったか:**

| | 実体 | ラグ |
|---|---|---|
| **Common Crawl** | LLM の *学習データ* 母体。次世代モデルの「学習済み知識」に効く可能性がある（不確実）| 数ヶ月〜年 |
| **Bing live index** | リアルタイムの AI 引用（Copilot / ChatGPT Search / Perplexity）の grounding source | 即時 |

この 2 つは**別経路**です。AI 検索が回答を生成するとき参照するのは live index 側で、Common Crawl ではありません。

**実測反例（自サイト）:** `honeymarron.com` は Common Crawl の直近 4 index すべてで 0 件（未収録）のままです。にもかかわらず Bing Webmaster Tools の "AI Performance" レポートでは **Copilot 引用が 3 ヶ月で約 7,700 回**記録されています（2026-07 実測）。**CC 収録は AI 引用の必要条件ではありません。**

**なので、この章の実務上の結論はこう差し替えます:**

- ❌ 「Common Crawl に入らないと AI 検索に出ない」→ 誤り。CC を AI 引用の成果指標にしない
- ✅ AI 引用の前提は **Bing の live index に入っていること**（＝第一弾 ch.01 の Bing Webmaster Tools が正しい入口だった）
- ✅ 引用されているかは **Bing Webmaster Tools → AI Performance**（grounding queries + cited URLs）で**実測**する。推測しない
- ⚠ 上記の note 本文は公開当時のまま残しています（後から書き換えず、訂正をこちらに追記する方針）

### 併せて訂正 — 施策と引用増の因果は未確認

本章 概要には「llms.txt の設置 / FAQPage schema を 71 ページに展開 / passage 単位の文章構造」を実装したこと、およびその後 Copilot referral が観測されたことを並べて書いています。**この並びを因果として読まないでください。因果は実証されていません。**

- **llms.txt** — 現状 AI 検索エンジンはほぼ参照していません（効果不確実。README にも明記）
- **passage 改稿** — その後の実測では、改稿しても引用数は動きませんでした
- **引用が伸びた事実はある**（上記 7,700 回 / 3 ヶ月）が、**どの施策が効いたかは未確認**です

なお本章 概要の「Copilot referral 2 件（n=2）」は 2026-06 時点の記述です。その後も referral（クリック）自体は依然小さい一方、引用回数は大きく伸びました。**引用は増えているのにクリックが増えない = zero-click** が実態で、ここが次の課題です。

---

## なぜ note と GitHub の両方にあるのか

- **note**: 記事本文を公開する場所 (Google/Bing の SEO 流入を狙う、note プラットフォーム内の拡散を狙う)
- **GitHub (このリポ)**: 記事の目次・補足ツール・コード例の置き場所 (developer コミュニティから fork/star)

役割を分離して、それぞれのプラットフォームの strength を活かす構成にしています。**記事本文を両方に置くと duplicate content として SEO 上どちらかが suppress されるため**、こちらは要約 + リンクのみにしています。

## 関連ツール

このリポの [`tools/`](../tools/README.md) 配下に、記事中で言及した処理を実行可能な形で置いています:

- [`tools/llms-txt-generator.py`](../tools/llms-txt-generator.py) — sitemap.xml から llms.txt skeleton 生成
- [`tools/schema-faq-generator.py`](../tools/schema-faq-generator.py) — Q&A テキストから FAQPage JSON-LD 生成
- [`tools/common-crawl-check.sh`](../tools/common-crawl-check.sh) — Common Crawl（LLM 学習データ）収録確認 ※上記の訂正を必ず参照

## 関連

- [← 01. Bing Webmaster Tools](01-bing-webmaster-tools.md)
- [トップに戻る](../README.md)

## Author

[honeymarron](https://honeymarron.com) | [表彰状クリエイター](https://apps.apple.com/jp/app/id6748368413) | [VoicyCare](https://apps.apple.com/jp/app/id6749561636) | GitHub: [@n-imai](https://github.com/n-imai) | note: [@honeymarron_dev](https://note.com/honeymarron_dev)
