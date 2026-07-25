# tools/

note 記事で言及した SEO/ASO 監査タスクを実行可能な形にしたツール群。
個人開発者が `git clone` してそのまま自分のサイトに対して走らせることを想定。

## ツール一覧

| ツール | 用途 | 言語 | 依存 |
|---|---|---|---|
| [`meta-desc-checker.py`](meta-desc-checker.py) | 全 HTML の meta description 文字数監査 | Python 3.10+ | 標準ライブラリのみ |
| [`twin-fields-check.py`](twin-fields-check.py) | meta/og/twitter/JSON-LD の twin fields 同期検証 | Python 3.10+ | 標準ライブラリのみ |
| [`common-crawl-check.sh`](common-crawl-check.sh) | Common Crawl（LLM 学習データ）収録状況の確認 | Bash | `curl` |
| [`bing-resubmit.sh`](bing-resubmit.sh) | Bing Webmaster URL 一括再送信 | Bash | `curl`, `jq` |
| [`llms-txt-generator.py`](llms-txt-generator.py) | sitemap.xml から llms.txt skeleton 生成 | Python 3.10+ | 標準ライブラリのみ |
| [`schema-faq-generator.py`](schema-faq-generator.py) | Q&A テキストから FAQPage JSON-LD 生成 | Python 3.10+ | 標準ライブラリのみ |

## meta-desc-checker.py

```bash
# 基本: 推奨範囲 (120〜160 文字) でチェック
python3 tools/meta-desc-checker.py /path/to/your/site

# 範囲をカスタマイズ
python3 tools/meta-desc-checker.py /path/to/your/site --min 100 --max 180

# 特定ディレクトリを除外
python3 tools/meta-desc-checker.py /path/to/your/site --exclude drafts/ --exclude tmp/
```

出力例:

```
=== meta description audit (/path/to/site) ===
Recommended range: 120〜160 chars
  In range: 90
  Out of range: 6
  Missing meta desc: 0

--- Out of range (sorted by length) ---
  [TOO SHORT]   79  404.html
  [TOO SHORT]  117  articles/foo.html
  [TOO LONG]   276  articles/bar.html
  [TOO LONG]   316  articles/baz.html
```

CI で使う場合は exit code (0 = OK, 1 = 範囲外あり) を見れば良い。

## twin-fields-check.py

ページタイトルや description は複数の場所 (`<title>`, `og:title`,
`twitter:title`, JSON-LD `name`/`headline`/`description`) に同じ
内容を書く必要がある。1 つだけ更新するともう一方とズレて、SERP /
SNS preview / AI 検索結果で表示が不一致になる。

```bash
# 全ての twin fields (title + description) を検証
python3 tools/twin-fields-check.py /path/to/your/site

# title のみ検証
python3 tools/twin-fields-check.py /path/to/your/site --check title

# description のみ検証
python3 tools/twin-fields-check.py /path/to/your/site --check description
```

出力例 (mismatch あり):

```
=== articles/foo.html ===
  Title mismatch:
    title: Award Certificate Creator - Free iPhone Certificate Maker
    og:title: Award Certificate Creator - Free iPhone App | Certificate Maker
    twitter:title: Award Certificate Creator - Free iPhone App | Certificate Maker

=== twin fields sync (all) ===
  Checked: 96
  Mismatches: 1
```

### 既知の制限: JSON-LD の false positive

1 つの HTML に複数の JSON-LD blocks (例: Person + Organization + WebSite +
Article) が含まれる場合、それぞれの `description` は entity ごとに
異なって良い (Person の自己紹介と Article の要約は別物)。

現在の実装は全 JSON-LD `description` を比較対象にするため、こうした
ページで false positive が出る。CI で使う場合は `--check title` のみ
利用するか、最初に手動で確認することを推奨。

将来的には `@type=Article|BlogPosting|NewsArticle` のみ抽出する改善
を検討中 (PR welcome)。

## common-crawl-check.sh

```bash
# 基本: 直近 4 つの index でチェック
./tools/common-crawl-check.sh yoursite.com

# index を絞り込み
./tools/common-crawl-check.sh yoursite.com --indexes "CC-MAIN-2026-30 CC-MAIN-2026-08"
```

出力例 (収録あり):

```
=== Common Crawl coverage: example.com ===
Checking indexes: CC-MAIN-2026-30 CC-MAIN-2026-08 ...

Index                 Hits
--------------------  ----
CC-MAIN-2026-30       142
CC-MAIN-2026-08       87
CC-MAIN-2025-51       62
CC-MAIN-2025-38       45

Total: 336 URLs found across 4 indexes
```

出力例 (収録なし):

```
=== Common Crawl coverage: newsite.com ===
...
Total: 0 URLs found across 4 indexes

NOTE: domain newsite.com is not found in any recent Common Crawl index.

What this means: your site is likely absent from the LLM *training data*
corpus...
What this does NOT mean: it does NOT mean AI search engines cannot cite
you...
```

<a id="cc-scope"></a>

### ⚠ このツールで分かること / 分からないこと

**分かること:** LLM の *学習データ*（Common Crawl）に自サイトが入っているか。
入っていれば、次世代モデルが学習済み知識として自サイトを知っている可能性が
上がる。ただしラグは数ヶ月〜年単位で、効果は不確実。

**分からないこと:** AI 検索で引用されるかどうか。**CC 未収録は「AI 検索に
出ない原因」ではありません。** リアルタイムの AI 引用（Copilot / ChatGPT
Search / Perplexity）は主に **Bing の live index** を grounding source に
しており、Common Crawl とは別経路です。

実測反例: `honeymarron.com` は Common Crawl 未収録のまま、Bing Webmaster
Tools の "AI Performance" レポートで **Copilot 引用 7,700 回 / 3 ヶ月**を
記録しています（2026-07 実測）。CC 収録は AI 引用の必要条件ではありません。

→ AI 検索での引用を診断したいなら、**Bing Webmaster Tools → AI Performance**
（grounding queries + cited URLs）を見てください。これが ground truth です。

## bing-resubmit.sh

Bing Webmaster API key を取得済みなら、`vercel CLI` のような
コマンドラインから URL 再送信ができる。デプロイ後の post-hook に
組み込むのが効果的。

```bash
# セットアップ
# 1. https://www.bing.com/webmasters → Settings → API Access → Generate
# 2. ~/.bashrc または ~/.zshrc に export を追加
export BING_API_KEY="abc123..."
export BING_SITE_URL="https://yoursite.com/"

# 単発で 1 URL 送信
echo "https://yoursite.com/articles/new-post" | ./tools/bing-resubmit.sh

# 複数 URL を一括 (Bing 制限: 10 URL/日)
cat <<EOF | ./tools/bing-resubmit.sh
https://yoursite.com/articles/post1
https://yoursite.com/articles/post2
https://yoursite.com/articles/post3
EOF

# ファイルから
./tools/bing-resubmit.sh < updated-urls.txt
```

出力例:

```
=== Bing Webmaster URL Submission ===
Site: https://yoursite.com/
URLs to submit: 3

Success: 3 URLs submitted to Bing.
  ✓ https://yoursite.com/articles/post1
  ✓ https://yoursite.com/articles/post2
  ✓ https://yoursite.com/articles/post3
```

## llms-txt-generator.py

```bash
# sitemap.xml から llms.txt の skeleton を生成 (ページを fetch して title/description も取得)
python3 tools/llms-txt-generator.py /path/to/sitemap.xml --site-name "My Site" --summary "サイトの一行説明"

# fetch せず URL だけ並べる
python3 tools/llms-txt-generator.py /path/to/sitemap.xml --site-name "My Site" --no-fetch
```

## schema-faq-generator.py

```bash
# Q:/A: テキストファイルから FAQPage JSON-LD を生成
python3 tools/schema-faq-generator.py faq.txt

# 標準入力から
printf 'Q: 質問?\nA: 回答。\n' | python3 tools/schema-faq-generator.py -
```

## License

これらのツールは記事と同じく [CC BY 4.0](../LICENSE) で公開。
attribution を付けてもらえれば、改変・商用利用・組み込み自由です。

## Related

- [トップに戻る](../README.md)
- 元記事: [個人開発者の SEO は Bing Webmaster Tools から始める](https://note.com/honeymarron_dev/n/n8dfd69eda0fd)
- 開発者: [honeymarron](https://honeymarron.com)
