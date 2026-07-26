#!/usr/bin/env sh
set -eu

BASE_URL="${AI_DESK_CARD_BASE_URL:-https://112.74.73.134}"
IP="${AI_DESK_CARD_IP:-112.74.73.134}"
AUTH_USER="${AI_DESK_CARD_AUTH_USER:-desk}"
AUTH_PASSWORD="${AI_DESK_CARD_AUTH_PASSWORD:-}"

curl_head() {
	env -u http_proxy -u https_proxy -u all_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
		curl -sS -I --connect-timeout 5 --max-time 15 \
		--retry 2 --retry-delay 1 --retry-connrefused "$1"
}

curl_head_auth() {
	env -u http_proxy -u https_proxy -u all_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
		curl -sS -I --connect-timeout 5 --max-time 15 \
		--retry 2 --retry-delay 1 --retry-connrefused \
		-u "$AUTH_USER:$AUTH_PASSWORD" "$1"
}

expect_http_redirect() {
	status="$(curl_head "http://$IP/" | awk 'NR == 1 {print $2}')"
	printf 'http / -> %s\n' "$status"
	if [ "$status" != "308" ] && [ "$status" != "301" ]; then
		printf 'expected HTTP redirect for http://%s/, got %s\n' "$IP" "$status" >&2
		exit 1
	fi
}

expect_status() {
	path="$1"
	expected="$2"
	status="$(curl_head "$BASE_URL$path" | awk 'NR == 1 {print $2}')"
	printf '%s -> %s\n' "$path" "$status"
	if [ "$status" != "$expected" ]; then
		printf 'expected %s for %s, got %s\n' "$expected" "$path" "$status" >&2
		exit 1
	fi
}

expect_header() {
	path="$1"
	header="$2"
	if ! curl_head "$BASE_URL$path" | grep -iq "^$header:"; then
		printf 'missing header %s for %s\n' "$header" "$path" >&2
		exit 1
	fi
}

expect_auth_status() {
	path="$1"
	expected="$2"
	status="$(curl_head_auth "$BASE_URL$path" | awk 'NR == 1 {print $2}')"
	printf 'auth %s -> %s\n' "$path" "$status"
	if [ "$status" != "$expected" ]; then
		printf 'expected authenticated %s for %s, got %s\n' "$expected" "$path" "$status" >&2
		exit 1
	fi
}

if [ -z "$AUTH_PASSWORD" ]; then
	printf 'AI_DESK_CARD_AUTH_PASSWORD is required for the authenticated HTTPS gate\n' >&2
	exit 1
fi

expect_http_redirect

expect_status / 401
expect_status /widgets.json 401
expect_status /README.md 401
expect_status /widgets.example.json 401
expect_status /../PLAN_web.md 401
expect_status /%2e%2e/PLAN_web.md 401

expect_auth_status / 200
expect_auth_status /widgets.json 200
expect_auth_status /README.md 404
expect_auth_status /widgets.example.json 404
expect_auth_status /../PLAN_web.md 404
expect_auth_status /%2e%2e/PLAN_web.md 404

expect_header / Cache-Control
expect_header / Content-Security-Policy
expect_header / Referrer-Policy
expect_header / Strict-Transport-Security
expect_header / X-Content-Type-Options

if ! printf '' | openssl s_client -connect "$IP:443" -brief 2>&1 | grep -q 'Verification: OK'; then
	printf 'TLS verification failed for %s\n' "$IP" >&2
	exit 1
fi

if ! echo | openssl s_client -connect "$IP:443" 2>/dev/null | openssl x509 -noout -ext subjectAltName | grep -q "IP Address:$IP"; then
	printf 'certificate SAN does not contain IP Address:%s\n' "$IP" >&2
	exit 1
fi

printf 'IP HTTPS Basic Auth gate passed for %s\n' "$BASE_URL"
