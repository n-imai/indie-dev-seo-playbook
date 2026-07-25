#!/usr/bin/env bash
# common-crawl-check.sh — 指定ドメインの Common Crawl 収録状況を確認
#
# Common Crawl (CC) は LLM の *学習データ* 母体。収録されると、次世代
# モデルが「学習済み知識」として自サイトを知っている可能性が上がる。
# ただしラグは数ヶ月〜年単位で、効果は不確実。
#
# ⚠ CC 未収録は「AI 検索に出ない原因」ではない。
#   リアルタイムの AI 検索引用 (Copilot / ChatGPT Search / Perplexity)
#   は主に Bing の live index を grounding source にしており、CC とは
#   別経路。実測反例: honeymarron.com は CC 未収録のまま、Bing AI
#   Performance Report で Copilot 引用 8.5K / 3 か月を記録している
#   (2026-07-25 実測)。
#   → AI 検索での引用可否を診断したいなら、CC ではなく Bing Webmaster
#     Tools の "AI Performance" レポートを見ること。
#
# このスクリプトが答えるのは「学習データに入っているか」だけ。
#
# Usage:
#   ./common-crawl-check.sh example.com
#   ./common-crawl-check.sh example.com --indexes "CC-MAIN-2026-30 CC-MAIN-2026-08"
#
# Exit code:
#   0  指定 index のいずれかに収録あり
#   1  全 index で 0 件 (= 学習データ未収録。AI 検索での引用可否とは別問題)
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

NOTE: domain $domain is not found in any recent Common Crawl index.

What this means: your site is likely absent from the LLM *training data*
corpus. Future model generations may not "know" your site from training.
Common Crawl expansion is slow (months to years) and the payoff is
uncertain.

What this does NOT mean: it does NOT mean AI search engines cannot cite
you. Real-time AI citation (Microsoft Copilot, ChatGPT Search,
Perplexity) is grounded mainly in Bing's live index, which is a separate
pipeline from Common Crawl. A site absent from CC can still be cited
thousands of times.

  Measured counterexample: honeymarron.com is absent from Common Crawl,
  yet Bing Webmaster Tools "AI Performance" recorded 8.5K Copilot
  citations over 3 months (measured 2026-07-25).

To diagnose AI search citation, use Bing Webmaster Tools -> AI
Performance (grounding queries + cited URLs). That is the ground truth;
Common Crawl coverage is not a proxy for it.

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
