# 01. Bing Webmaster Tools 活用ガイド — Google だけ見てると見落とすもの

> 個人開発者の検索流入の **9 割が Bing 経由**になっている、というケースは珍しくない。Google Search Console だけで運用していると、この流入を取りこぼし、改善機会を見逃す。

## なぜ Bing が個人開発者にとって重要か

新規ドメイン(立ち上げ 1〜2 年)では、Google が **domain authority 不足を理由にインデックスを遅らせる**ことがよくあります。一方、Bing は同条件でも積極的にクロール・インデックスする傾向があります。

加えて重要なのが、**Microsoft Copilot は内部的に Bing のインデックスを使っている**こと。つまり Bing で上位に出るページは、Copilot 経由で AI 検索結果にも露出します。

実際、私のサイト `honeymarron.com` の 2026-04 後半〜05 のトラフィック内訳:

| ソース | sessions (28d) | 比率 |
|---|:---:|:---:|
| Bing Organic | 191 | **64.7%** |
| (Direct) | 78 | 26.4% |
| Google Organic | 17 | 5.8% |
| その他 | 9 | 3.1% |

Google からの流入は **5.8% にすぎず**、Bing が 11 倍以上の流入を持ってきています。Google Search Console だけ見ていたら、流入の構造を完全に見誤っていた状態でした。

## セットアップ

### 1. アカウント作成 + サイト追加

1. https://www.bing.com/webmasters にアクセス
2. Microsoft / Google / Facebook いずれかでサインイン
3. **Add a site** で `https://yoursite.com/` を追加
4. **Verify** で HTML meta tag / DNS / file 配置 のいずれかを選んで検証

> 補足: Google Search Console で検証済みのサイトは **Import** ボタンで一括取り込みできます。Google で 1 回検証してから Bing にインポートが最短ルート。

### 2. sitemap.xml の登録

左メニュー → **Sitemaps** → **Submit Sitemap**

```
https://yoursite.com/sitemap.xml
```

> Google も Bing も sitemap.xml は同じ仕様 (sitemaps.org)。1 つ作って両方に送れば OK。

### 3. API Key の取得 (任意・推奨)

左メニュー → **Settings** → **API Access** → **Generate**

API Key があると、後述する **server-side でのトラフィックデータ取得** ができるようになります。`gh CLI` や `vercel CLI` と同じ要領で日次レポートを自動化できます。

API Key を `~/.config/bing-webmaster/api-key.json` のような場所に保存しておくと、毎回コンソールに行かなくて済みます。

## 日常的に使う機能 (頻度順)

### A. URL Submission (週 1〜月 1)

新しいページを公開したり、既存ページを大きく更新したら明示的に再クロール依頼を出します。

**手順:**
1. 左メニュー → **URL Submission** → **Submit URLs**
2. 1 行 1 URL で最大 10 URL/日、月 10,000 URL までペースト

```
https://yoursite.com/articles/new-post-1/
https://yoursite.com/articles/new-post-2/
```

Google Search Console の URL Inspection に比べて、Bing は **submission からインデックスまでが早い** (体感数時間〜2 日)。新規 article の早期インデックスに有効です。

### B. Search Performance (週 1)

左メニュー → **Search Performance**

Google Search Console の Performance と同等。ただし以下の違いに注意:

| 観点 | GSC (Google) | Bing Webmaster Tools |
|---|---|---|
| 集計遅延 | 2〜3 日 | **1〜2 日** (Bing の方が早い) |
| Average Position | 各検索結果での正確な順位 | impression があったクエリの平均 (やや楽観的) |
| Query データ保持 | 16 ヶ月 | 6 ヶ月 |
| API レート制限 | 50,000/day | 25,000/day |

「**直近 1 週間で impressions が増えたクエリ**」を毎週チェックして、伸びている query にコンテンツを足すのが定石です。

### C. Recommendations (週 1)

左メニュー → **Recommendations**

Bing が「あなたのサイトのここを直すべき」を Top 5 程度で提示してくれます。

過去に私が指摘されたもの:
- **"Meta descriptions on many pages are too short. Lengthen to provide better context."**
- **"Inbound links from quality domains are insufficient."**

ただし、Recommendations は **やや過剰検出する傾向**があります。「短い」と指摘された pages を全数調査したら、実際には適正範囲のものが大半で、本当に短いのは 1〜2 ページだけだった、というケースもあります。鵜呑みにせず、**自分でも数字を確認**してから対応しましょう。

### D. URL Inspection (必要時)

特定 URL のインデックス状況を確認する機能。Google Search Console の URL Inspection と同じ。

「**インデックスに登録されているはずなのに impression が出ない**」というケースで、まず URL Inspection で確認します。インデックス済みなら content / 競合の問題、未インデックスなら sitemap / crawlability の問題、と切り分けられます。

## いざという時の機能

### E. Block URLs (旧 URL の整理)

ドメイン構成を変えた際の **古い URL の検索結果除外** に使います。

たとえば、私のサイトでは以前 `awardcert.honeymarron.com/*` というサブドメイン構成でしたが、現在は `honeymarron.com/awardcert/*` 配下に統合済み (308 redirect 設定済み)。それでも Bing のクロール DB には旧サブドメイン URL が長期間残り、ユーザーが古い URL をクリック → 308 redirect → 新 URL に着地、という遠回りが発生していました。

**この遠回りが GA4 で何を起こすか:**
- Bing 検索 → 旧 URL クリック → 308 redirect → 新 URL に着地
- → GA4 で **landingPage が `(not set)` になる**(リダイレクトを跨いだ計測の限界)
- → ランディング page 別の分析ができなくなる

これを解消するには、**Bing 側で旧 URL を deindex 申請**します。

**手順:**
1. **Configure My Site** → **Block URLs**
2. **Add URL to Block**
3. URL を `https://awardcert.yourdomain.com/` のように入力
4. URL Type: **Directory** (パス全体を対象)
5. Block Type: **URL and Cache** (キャッシュも消す)
6. **Submit**

90 日間有効。期限が来る前にもう一度 submit すれば延長できます。

> 注意: Block URLs は「**そのサブドメインを本当に使っていない**」場合のみ実行してください。たとえば www → non-www 統合中なら、www 側の Block は避けるべきです (DNS では生きているサブドメインの「特定 URL だけ」を block する別の機能があります)。

### F. Crawl Control (重い処理対策)

サーバが弱い小規模サイトで、Bingbot のアクセス頻度を抑えたい場合に使います。逆に、新しいページの早期発見を望む場合は最大値に設定します。

個人開発の Vercel + 静的サイトの構成なら、**いじらないでデフォルト**で問題ありません。

## トラフィック取得の自動化 (API)

API Key を取得済みなら、サーバ側でトラフィックデータを取得できます。Bing は **GA4 と違ってサーバ側計測**なので、JavaScript を動かさない AI クローラー / bot 由来のトラフィックも捕捉します。

### サンプル: 過去 7 日のクリック・インプレッション

```bash
curl -s "https://ssl.bing.com/webmaster/api.svc/json/GetRankAndTrafficStats?siteUrl=https%3A%2F%2Fyoursite.com%2F&apikey=YOUR_API_KEY"
```

レスポンスの `daily_stats` 配列に、日別の clicks / impressions が入っています。日付フォーマットが `/Date(epoch_ms-tz)/` の **奇妙な形式** で来るので、Asia/Tokyo に変換する小スクリプトを書いておくと便利です。

```js
const fmt = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Tokyo' });
const m = dateStr.match(/\/Date\((\d+)/);
const jstDate = fmt.format(new Date(parseInt(m[1])));
```

### 上位クエリ・上位ページ

```bash
# Top queries
curl -s "https://ssl.bing.com/webmaster/api.svc/json/GetQueryStats?siteUrl=https%3A%2F%2Fyoursite.com%2F&apikey=YOUR_API_KEY"

# Top pages
curl -s "https://ssl.bing.com/webmaster/api.svc/json/GetPageStats?siteUrl=https%3A%2F%2Fyoursite.com%2F&apikey=YOUR_API_KEY"
```

これらは **期間指定ができず**、Bing が保持する直近 6 ヶ月の累計値を返します。「直近 7 日の上位クエリ」を取りたい場合は GetRankAndTrafficStats と組み合わせて、自前で差分計算する必要があります。

### API レスポンスの罠

GetQueryStats / GetPageStats のレスポンスには時々 **CTR が 100% を超える値**が出ます (例: `clicks: 7, impressions: 6, ctr: 116.67`)。これは Bing 内部の集計バグで、`clicks > impressions` の組合せが返ることがあります。

そのため、これらの API の数字は **絶対値より相対的な大小** で読むのが安全です。実数を信用するなら GetRankAndTrafficStats の集計値の方が確実。

## 個人開発者にとっての落とし穴

### ❌ Google Search Console と同じ感覚で Sitemap を放置

GSC は sitemap を一度送ると基本放置で OK ですが、Bing は **コンテンツ更新の度に「Resubmit」ボタンを押す**と早く反映されます。コンテンツ追加直後に GSC + Bing の両方で Resubmit する習慣をつけましょう。

### ❌ Recommendations を全部対応する

前述の通り、Bing の Recommendations は過剰検出傾向あり。 全部潰しに行くと工数を浪費します。「クリックでアクセス可能な具体的な数字」を本当に確認してから対応するのが鉄則。

### ❌ Bing 自身からのクロールトラフィックを「ユーザー流入」と勘違いする

Bing search → Click → User landing は、GA4 の `sessionSource=bing / sessionMedium=organic` でカウントされます。一方、Bingbot のクロール自体は GA4 では計測されません (JavaScript 動かないため)。

ただし **Vercel Analytics などのサーバサイド計測**を入れていると、Bingbot のアクセスも raw count に含まれます。GA4 と Vercel Analytics の数字が乖離していたら、bot crawl 由来の差分の可能性があります。

## まとめ

Bing Webmaster Tools は、特に **新規ドメインの個人開発者にとって Google Search Console より重要なツール**になり得ます:

- 個人開発サイトの主要流入が Bing になることが多い (5〜10 倍珍しくない)
- Microsoft Copilot (AI 検索) の母体である
- インデックス速度が Google より早い
- Recommendations は鵜呑みにせず数値確認してから対応
- 旧 URL の Block で landingPage `(not set)` を解消できる
- API Key + サーバ側スクリプトで日次レポート自動化可能

「**Google Search Console は週次、Bing Webmaster Tools は日次**」くらいの優先度で運用するのが、個人開発者には合っていると思います。

## 関連

- [トップに戻る](../README.md)
- 次の章 (近日公開): meta タグの twin fields 同期

## Author

[honeymarron](https://honeymarron.com) | [Award Certificate Creator](https://apps.apple.com/app/id6748368413) | [VoicyCare](https://apps.apple.com/app/id6749561636) | GitHub: [@n-imai](https://github.com/n-imai)
