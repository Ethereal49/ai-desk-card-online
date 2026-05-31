#!/usr/bin/env sh
set -eu

BASE_URL="${1:-${AI_DESK_CARD_URL:-http://112.74.73.134}}"

fail() {
  printf '%s\n' "FAIL: $*" >&2
  exit 1
}

check_redirect() {
	path="$1"
	status="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 10 "${BASE_URL}${path}")"
	printf '%s -> %s\n' "$path" "$status"
	if [ "$status" != "301" ] && [ "$status" != "308" ]; then
		fail "${path} expected HTTP redirect, got ${status}"
	fi
}

check_location() {
	path="$1"
	headers="$(curl -sSI --max-time 10 "${BASE_URL}${path}")"
	printf '%s' "$headers" | grep -qi "^Location: https://" || fail "missing HTTPS Location header for ${path}"
}

check_redirect "/"
check_redirect "/widgets.json"
check_redirect "/README.md"
check_redirect "/widgets.example.json"
check_redirect "/../PLAN_web.md"
check_redirect "/%2e%2e/PLAN_web.md"

check_location "/"

printf '%s\n' "IP HTTP redirect gate passed for ${BASE_URL}"
