#!/usr/bin/env sh
set -eu

BASE_URL="${1:-${AI_DESK_CARD_URL:-http://112.74.73.134}}"

fail() {
  printf '%s\n' "FAIL: $*" >&2
  exit 1
}

check_status() {
  path="$1"
  expected="$2"
  status="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 10 "${BASE_URL}${path}")"
  printf '%s -> %s\n' "$path" "$status"
  [ "$status" = "$expected" ] || fail "${path} expected ${expected}, got ${status}"
}

check_header() {
  name="$1"
  headers="$2"
  printf '%s' "$headers" | grep -qi "^${name}:" || fail "missing header ${name}"
}

check_status "/" "200"
check_status "/widgets.json" "200"
check_status "/README.md" "404"
check_status "/widgets.example.json" "404"
check_status "/../PLAN_web.md" "404"
check_status "/%2e%2e/PLAN_web.md" "404"

headers="$(curl -sSI --max-time 10 "${BASE_URL}/")"
check_header "Cache-Control" "$headers"
check_header "Content-Security-Policy" "$headers"
check_header "Referrer-Policy" "$headers"
check_header "X-Content-Type-Options" "$headers"

printf '%s\n' "IP-only demo gate passed for ${BASE_URL}"
