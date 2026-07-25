#!/usr/bin/env bash
# common-crawl-check.sh — 指定ドメインの Common Crawl 収録状況を確認
#
# Common Crawl (CC) は LLM 学習データの主要ソースの一つ。収録されると、
# 次世代モデルが「学習済み知識」として自サイトを知っている可能性が上がる。
# ただしラグは数ヶ月〜年単位で、効果は不確実（各社は自前クローラも併用
# しており、CC 収録 = 学習採用でもない）。
#
# ⚠ CC 未収録は「AI 検索に出ない原因」ではない。
#   Microsoft Copilot は Bing の live index を grounding source にして
#   おり、CC とは別経路。Perplexity / ChatGPT Search は各々が自前の
#   クローラ・インデックスを持つため、こちらも CC 収録は前提ではない。
#   実測反例: honeymarron.com は CC 未収録のまま、Bing AI Performance
#   Report で Copilot 引用 8.5K / 3 か月を記録している (2026-07-25 実測)。
#   → Copilot の引用可否は Bing Webmaster Tools の "AI Performance"
#     (計測対象 = Microsoft Copilots and Partners) で確認する。他の
#     アシスタントはプラットフォーム固有の証跡で見ること。
#
# このスクリプトが答えるのは「照会した CC index に収録されているか」だけ。
# 全 index を網羅するわけではない（既定は直近 4 collection。--indexes で
# 追加指定可。全一覧は https://index.commoncrawl.org/）。
#
# Usage:
#   ./common-crawl-check.sh example.com
#   ./common-crawl-check.sh example.com --indexes "CC-MAIN-2026-30 CC-MAIN-2026-08"
#
# Exit code:
#   0  指定 index のいずれかに収録あり
#   1  指定した全 index で 0 件 (= 照会範囲では未収録。CC 全体の不在を
#      証明するものではなく、AI 検索での引用可否とも別問題)
#
# Related article:
#   https://note.com/honeymarron_dev/n/n8dfd69eda0fd
#
# Dependencies:
#   curl, awk

set -euo pipefail

domain="${1:-}"
if [ -z "$domain" ]; then
  echo "Usage: $0 <domain> [--indexes \"CC-MAIN-2026-30 CC-MAIN-2026-08\"]" >&2
  echo "Example: $0 honeymarron.com" >&2
  exit 2
fi

shift
indexes="CC-MAIN-2026-30 CC-MAIN-2026-08 CC-MAIN-2025-51 CC-MAIN-2025-38"
while [ $# -gt 0 ]; do
  case "$1" in
    --indexes)
      indexes="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

# Strip protocol if user pasted full URL
domain="${domain#http://}"
domain="${domain#https://}"
domain="${domain%/}"

echo "=== Common Crawl coverage: $domain ==="
echo "Checking indexes: $indexes"
echo ""

# Convert space-separated indexes string into an array
read -ra index_array <<< "$indexes"

total=0
hits_any=0
printf "%-20s  %s\n" "Index" "Hits"
printf "%-20s  %s\n" "--------------------" "----"
for idx in "${index_array[@]}"; do
  url="https://index.commoncrawl.org/${idx}-index?url=${domain}/*&output=json"
  # Common Crawl は 5-15s かかる事がある。30s timeout で抑える。
  count=$(curl -s --max-time 30 "$url" 2>/dev/null | grep -c '"url"' || true)
  printf "%-20s  %s\n" "$idx" "$count"
  total=$((total + count))
  if [ "$count" -gt 0 ]; then
    hits_any=1
  fi
done
echo ""
echo "Total: $total URLs found across ${#index_array[@]} indexes"

if [ "$hits_any" -eq 0 ]; then
  cat <<EOF

NOTE: domain $domain was not found in the ${#index_array[@]} Common Crawl
index(es) checked above. This does NOT prove absence from every CC
snapshot -- only from the ones queried. To widen the check, pass more
collections with --indexes (see https://index.commoncrawl.org/ for the
full list).

What this means: your site appears to be missing from these snapshots of
Common Crawl, one of the major sources of LLM training data. Future model
generations may not "know" your site from training (though labs also run
their own crawlers, so CC is not the only path). CC expansion is slow
(months to years) and the payoff is uncertain.

What this does NOT mean: it does NOT mean AI search engines cannot cite
you. Microsoft Copilot grounds its citations in Bing's live index, which
is a separate pipeline from Common Crawl, so a site absent from CC can
still be cited thousands of times. Other assistants use their own
retrieval stacks (e.g. Perplexity and ChatGPT Search operate their own
crawlers/indexes), so CC coverage is not a prerequisite there either.

  Measured counterexample: honeymarron.com was absent from the 4 CC
  indexes checked, yet Bing Webmaster Tools "AI Performance" recorded
  8.5K Copilot citations over 3 months (measured 2026-07-25).

To diagnose citation by Microsoft Copilot, use Bing Webmaster Tools ->
AI Performance (grounding queries + cited URLs); that is ground truth
for Microsoft Copilots and Partners, which is the surface it measures.
For other assistants, use platform-specific evidence instead (e.g.
referrer/source data in your analytics, or the platform's own console).
In none of these cases is Common Crawl coverage a proxy.

If you specifically want training-data inclusion:
  1. Get inbound links from sites already in CC:
     - Wikipedia / Wikidata (via citing your site)
     - GitHub README files (CC crawls GitHub heavily)
     - Hacker News / Reddit submissions
     - Independent blogs / news sites
  2. Verify your site is crawlable (robots.txt, no JS-only render)
  3. Wait 2-4 months (CC frontier expansion is slow)

EOF
  exit 1
fi
exit 0
