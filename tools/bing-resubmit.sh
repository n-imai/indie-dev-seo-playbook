#!/usr/bin/env bash
# bing-resubmit.sh — Bing Webmaster API 経由で URL 一括再送信
#
# Bing は URL Submission を毎日 10 URL/日まで受け付ける。
# このスクリプトは API key を使って、新規/更新した URL を素早く
# Bing インデックスに再登録する。
#
# Usage:
#   echo "https://example.com/article1" | ./bing-resubmit.sh
#   cat urls.txt | ./bing-resubmit.sh
#   ./bing-resubmit.sh < urls.txt
#
# Environment:
#   BING_API_KEY     Bing Webmaster API key (required)
#   BING_SITE_URL    Site URL as registered in Bing (e.g., "https://example.com/")
#
# Setup:
#   1. https://www.bing.com/webmasters → Settings → API Access → Generate
#   2. export BING_API_KEY="your-api-key"
#   3. export BING_SITE_URL="https://yoursite.com/"
#
# Exit code:
#   0  全ての URL を正常送信
#   1  少なくとも 1 つの URL でエラー
#
# Related article:
#   https://note.com/honeymarron_dev/n/n8dfd69eda0fd
#
# Dependencies:
#   curl, jq

set -euo pipefail

if [ -z "${BING_API_KEY:-}" ]; then
  echo "Error: BING_API_KEY environment variable is not set" >&2
  echo "  1. Get key at https://www.bing.com/webmasters → Settings → API Access" >&2
  echo "  2. export BING_API_KEY=\"...\"" >&2
  exit 2
fi
if [ -z "${BING_SITE_URL:-}" ]; then
  echo "Error: BING_SITE_URL environment variable is not set" >&2
  echo "  Example: export BING_SITE_URL=\"https://yoursite.com/\"" >&2
  exit 2
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is not installed (brew install jq / apt-get install jq)" >&2
  exit 2
fi

# Read URLs from stdin, one per line
urls_list=()
while IFS= read -r url; do
  # Skip empty lines and comments
  url="$(echo "$url" | sed -e 's/[[:space:]]*$//' -e 's/^[[:space:]]*//')"
  [ -z "$url" ] && continue
  [[ "$url" =~ ^# ]] && continue
  urls_list+=("$url")
done

count=${#urls_list[@]}
if [ "$count" -eq 0 ]; then
  echo "Error: no URLs provided on stdin" >&2
  exit 2
fi
if [ "$count" -gt 10 ]; then
  echo "Warning: $count URLs provided, Bing limits 10/day. Only first 10 will be sent." >&2
  urls_list=("${urls_list[@]:0:10}")
fi

echo "=== Bing Webmaster URL Submission ==="
echo "Site: $BING_SITE_URL"
echo "URLs to submit: ${#urls_list[@]}"
echo ""

# Build JSON payload using jq (handles escaping safely)
payload=$(jq -n \
  --arg site "$BING_SITE_URL" \
  --argjson urls "$(printf '%s\n' "${urls_list[@]}" | jq -R . | jq -s .)" \
  '{siteUrl: $site, urlList: $urls}')

response=$(curl -s -w "\n%{http_code}" \
  -X POST \
  -H "Content-Type: application/json; charset=utf-8" \
  --data "$payload" \
  "https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlBatch?apikey=${BING_API_KEY}")

body=$(echo "$response" | sed '$d')
http_code=$(echo "$response" | tail -1)

if [ "$http_code" = "200" ]; then
  # Bing returns {"d": null} on success
  if echo "$body" | jq -e '.d == null' >/dev/null 2>&1; then
    echo "Success: ${#urls_list[@]} URLs submitted to Bing."
    for u in "${urls_list[@]}"; do
      echo "  ✓ $u"
    done
    exit 0
  else
    echo "Warning: 200 OK but unexpected body:" >&2
    echo "$body" >&2
    exit 1
  fi
else
  echo "Error: HTTP $http_code" >&2
  echo "Response body:" >&2
  echo "$body" >&2
  exit 1
fi
