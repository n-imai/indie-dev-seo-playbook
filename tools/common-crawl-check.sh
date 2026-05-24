#!/usr/bin/env bash
# common-crawl-check.sh — 指定ドメインの Common Crawl 収録状況を確認
#
# Common Crawl は ChatGPT/Claude/Perplexity の training data の中核。
# 自分のサイトが CC に収録されていないと、AI 検索結果に出てこない原因
# になり得る。このスクリプトは直近の 4 つの CC index に対して、指定
# ドメインの URL がどれだけ収録されているかを確認する。
#
# Usage:
#   ./common-crawl-check.sh example.com
#   ./common-crawl-check.sh example.com --indexes "CC-MAIN-2026-30 CC-MAIN-2026-08"
#
# Exit code:
#   0  指定 index のいずれかに収録あり
#   1  全 index で 0 件 (AI 検索流入ゼロの原因の可能性)
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

WARNING: domain $domain is not found in any recent Common Crawl index.

This is a strong signal that AI search engines (ChatGPT, Claude.ai,
Perplexity) have NOT learned about your site. Common Crawl is the
core dataset for LLM training, and crawls primarily come from links
on already-indexed sites.

To get into Common Crawl:
  1. Get inbound links from sites already in CC:
     - Wikipedia / Wikidata (via citing your site)
     - GitHub README files (CC crawls GitHub heavily)
     - Hacker News / Reddit submissions
     - Independent blogs / news sites
  2. Verify your site is crawlable (robots.txt, no JS-only render)
  3. Add llms.txt with canonical content for AI crawlers
  4. Wait 2-4 months (CC frontier expansion is slow)

EOF
  exit 1
fi
exit 0
