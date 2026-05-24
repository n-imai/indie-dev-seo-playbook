# 01. Bing Webmaster Tools 活用ガイド — Google だけ見てると見落とすもの

> 📝 **本文は note で公開しています**
>
> [個人開発者の SEO は Bing Webmaster Tools から始める — Google だけ見てると見落とすもの](https://note.com/honeymarron_dev/n/n8dfd69eda0fd)

---

## 概要

個人開発で iOS アプリ 2 本(Award Certificate Creator ★4.3 / VoicyCare ★5.0)を 175 カ国に流通させた経験から、サイト運営の検索流入の **9 割が Bing 経由**になっていたという気付きをベースに、Bing Webmaster Tools の活用ノウハウを解説した記事です。

### この章でカバーする内容

- なぜ Bing が個人開発者にとって重要か (`honeymarron.com` の実例: Bing 64.7% vs Google 5.8%)
- Bing Webmaster Tools のセットアップ
- 日常的に使う機能 (URL Submission / Search Performance / Recommendations)
- いざという時の機能 (Block URLs で `landingPage = (not set)` を解消)
- API Key を使ったトラフィック取得の自動化
- 個人開発者にとっての落とし穴

→ **続きは [note 記事](https://note.com/honeymarron_dev/n/n8dfd69eda0fd) でお読みください。**

---

## なぜ note と GitHub の両方にあるのか

- **note**: 記事本文を公開する場所 (Google/Bing の SEO 流入を狙う、note プラットフォーム内の拡散を狙う)
- **GitHub (このリポ)**: 記事の目次・補足ツール・コード例の置き場所 (developer コミュニティから fork/star、Common Crawl seed)

役割を分離して、それぞれのプラットフォームの strength を活かす構成にしています。**記事本文を両方に置くと duplicate content として SEO 上どちらかが suppress されるため**、こちらは要約 + リンクのみにしています。

## 関連ツール (将来追加予定)

このリポの `tools/` 配下に、記事中で言及した処理を実行可能な形で追加していく予定です:

- `tools/meta-desc-length-checker.py` — 全 HTML の meta description 長さチェック
- `tools/twin-fields-sync-check.py` — JSON-LD / og: / twitter: の同期検証
- `tools/common-crawl-coverage-check.sh` — Common Crawl 収録確認

## 関連

- [トップに戻る](../README.md)
- 次の章 (近日公開): meta タグの twin fields 同期

## Author

[honeymarron](https://honeymarron.com) | [表彰状クリエイター](https://apps.apple.com/jp/app/id6748368413) | [VoicyCare](https://apps.apple.com/jp/app/id6749561636) | GitHub: [@n-imai](https://github.com/n-imai) | note: [@honeymarron_dev](https://note.com/honeymarron_dev)
