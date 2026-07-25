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
- 施策4: 外部認知の壁 — Common Crawl（**※この要約の見出しは誤解を招くので下記を参照**）
- 効果はどう測るか（GA4 で copilot.com referral、(direct) に紛れる AI 流入）
- GEO チェックリスト

→ **続きは note 記事でお読みください。**

---

## ⚠ 訂正（2026-07-25）— Common Crawl は AI 検索引用の前提条件ではない

**訂正対象は note 本文ではなく、このリポ側の記述です。**

note 本文（第二弾）は当初から正しく、「AI 検索の引用は Common Crawl ではなく**ライブのリトリーバルクローラ**が作るリアルタイムインデックスから来る」「**Copilot の引用は Bing インデックス経由**なので Common Crawl 未収録でも経路は確保できている」「CC 未収録が効くのは主に *事前学習* 段階でサイトを知っているか」と、この区別をきちんと書いています。

**誤っていたのはリポ側です:**

1. この要約の見出し「**施策4: 外部認知の壁 — Common Crawl**」が、CC を AI 引用の *前提条件* のように読ませていた（note 本文の主張と食い違う要約になっていた）
2. `tools/common-crawl-check.sh` が 0 件時に `This is a strong signal that AI search engines ... have NOT learned about your site` と**断定出力**していた
3. `README.md` が CC を「ChatGPT/Claude の training data の**中核**」「AI 検索流入の**根本原因**チェック」と書き、Backlog ch.05 を「なぜ collection 0 件だと AI 検索に出ないのか」という**誤った前提**で立てていた

つまり note の正しい記述が、リポの要約とツールの実装に落とす段階で崩れていました。以下は「note の訂正」ではなく**リポ側の是正**の記録です。

**何が違ったか（改めて整理）:**

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
- ℹ️ note 本文は正しいので書き換えていません。上の「施策4」という見出し表現のみ、この節で補足しています

### 併せて — 施策と引用増の因果は未確認（note 公開後に判明）

本章 概要には「llms.txt の設置 / FAQPage schema を 71 ページに展開 / passage 単位の文章構造」を実装したこと、およびその後 Copilot referral が観測されたことを並べて書いています。**この並びを因果として読まないでください。因果は実証されていません。**

- **llms.txt** — note 本文でも「現時点では AI 検索の引用にはほぼ効きません」「効果がいちばん不確実」と明記されているとおりです
- **passage 改稿** — note 本文は「5 つの中でいちばん確度の高い施策」と評価していました（arXiv 2311.09735 に基づく）。**ただしその後の実測では、改稿しても引用数は動きませんでした。**公開時点の評価が後の実測で下がった項目です
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
