#!/usr/bin/env bash
#
# Local stack doctor.
#
# Answers, in one run: are the containers up, are their healthchecks passing,
# do the HTTP endpoints respond, and is the API configured to talk to the
# agents with the same keys? That last check is the usual cause of a chat that
# never starts.
#
# Usage:
#   ./scripts/doctor.sh              # one report
#   ./scripts/doctor.sh --wait 120   # poll until healthy, up to 120s
#
# Exit codes: 0 all checks pass, 1 one or more checks failed.

set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR" || exit 1

if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  RED=$'\033[31m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; BOLD=$'\033[1m'; NC=$'\033[0m'
else
  RED=""; GREEN=""; YELLOW=""; BOLD=""; NC=""
fi

FAILURES=0
WARNINGS=0

pass() { printf '  %sPASS%s  %s\n' "$GREEN" "$NC" "$1"; }
fail() { printf '  %sFAIL%s  %s\n' "$RED" "$NC" "$1"; FAILURES=$((FAILURES + 1)); }
warn() { printf '  %sWARN%s  %s\n' "$YELLOW" "$NC" "$1"; WARNINGS=$((WARNINGS + 1)); }
info() { printf '  ----  %s\n' "$1"; }
heading() { printf '\n%s%s%s\n' "$BOLD" "$1" "$NC"; }

COMPOSE_ARGS=(docker compose)
if [ -f "$ROOT_DIR/../.env" ]; then
  COMPOSE_ARGS+=(--env-file "$ROOT_DIR/../.env")
fi
compose() { "${COMPOSE_ARGS[@]}" "$@"; }

waited=0
wait_for=0
while [ $# -gt 0 ]; do
  case "$1" in
    --wait) wait_for="${2:-120}"; shift 2 ;;
    -h|--help) sed -n '2,16p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

env_get() {
  # Read KEY=value from .env without executing it (no shell expansion or
  # redirection from values such as `EMAIL_FROM="Name <addr>"`).
  local key="$1" file="$2"
  [ -f "$file" ] || return 0
  awk -F= -v key="$key" '
    $1 == key {
      value = substr($0, index($0, "=") + 1)
      gsub(/^"|"$/, "", value)
      print value
      exit
    }
  ' "$file"
}

http_probe() {
  # $1 = url, echoes status code (000 on connection failure)
  local url="$1" code
  if command -v curl >/dev/null 2>&1; then
    code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 3 "$url" 2>/dev/null)
  else
    code=$(python3 - "$url" <<'PY' 2>/dev/null
import sys, urllib.request
try:
    print(urllib.request.urlopen(sys.argv[1], timeout=3).status)
except Exception:
    print("000")
PY
)
  fi
  printf '%s' "${code:-000}"
}

http_body() {
  local url="$1"
  if command -v curl >/dev/null 2>&1; then
    curl -sS --max-time 3 "$url" 2>/dev/null
  else
    python3 - "$url" <<'PY' 2>/dev/null
import sys, urllib.request
try:
    print(urllib.request.urlopen(sys.argv[1], timeout=3).read().decode())
except Exception:
    pass
PY
  fi
}

check_stack() {
  heading "1. Prerequisites"
  if ! command -v docker >/dev/null 2>&1; then
    fail "docker CLI not found"
    return 1
  fi
  pass "docker CLI found"
  if ! docker info >/dev/null 2>&1; then
    fail "Docker daemon is not reachable"
    return 1
  fi
  pass "Docker daemon reachable"
  if ! compose version >/dev/null 2>&1; then
    fail "docker compose is not available"
    return 1
  fi
  pass "docker compose available"

  heading "2. Environment file"
  local env_file jwt_secret auth_secret adapter_secret
  if [ -f "$ROOT_DIR/../.env" ]; then
    pass "../.env present"
    env_file="$ROOT_DIR/../.env"
    jwt_secret=$(env_get JWT_SECRET "$env_file")
    auth_secret=$(env_get AUTH_SECRET "$env_file")
    adapter_secret=$(env_get AUTH_ADAPTER_SECRET "$env_file")
    if [ -z "$jwt_secret" ] || [ "$jwt_secret" = "replace-with-a-long-random-secret" ]; then
      fail "JWT_SECRET is missing or still the placeholder value"
    else
      pass "JWT_SECRET is set"
    fi
    if [ -n "$auth_secret" ] && [ "$auth_secret" != "$jwt_secret" ]; then
      warn "AUTH_SECRET and JWT_SECRET differ; NextAuth tokens will fail API verification"
    else
      pass "AUTH_SECRET matches JWT_SECRET"
    fi
    if [ -n "$adapter_secret" ] && [ "$adapter_secret" = "replace-with-a-separate-long-random-secret" ]; then
      warn "AUTH_ADAPTER_SECRET is still the placeholder value"
    fi
  else
    warn "../.env not found; compose will use defaults (fine for a quick look, not for auth)"
  fi

  heading "3. Compose configuration"
  if compose config -q >/dev/null 2>&1; then
    pass "docker-compose.yml is valid"
  else
    fail "docker-compose.yml is invalid (run: docker compose config)"
    return 1
  fi

  heading "4. Container state"
  local rows
  rows=$(compose ps -a --format '{{.Service}}|{{.State}}|{{.Health}}' 2>/dev/null)
  if [ -z "$rows" ]; then
    fail "no containers found (start with: make up)"
    return 1
  fi
  printf '  %-16s %-12s %s\n' "SERVICE" "STATE" "HEALTH"
  while IFS='|' read -r svc state health; do
    [ -z "$svc" ] && continue
    [ -z "$health" ] && health="-"
    if [ "$state" = "running" ] && { [ "$health" = "healthy" ] || [ "$health" = "-" ]; }; then
      printf '  %-16s %-12s %s\n' "$svc" "$state" "$health"
    elif [ "$state" = "exited" ] && [ "$svc" = "migrate" ] && [ "$health" = "-" ]; then
      # The migration gate is expected to exit 0.
      local exit_code
      exit_code=$(docker inspect --format '{{.State.ExitCode}}' "$(compose ps -aq "$svc" 2>/dev/null)" 2>/dev/null)
      if [ "${exit_code:-1}" = "0" ]; then
        printf '  %-16s %-12s %s\n' "$svc" "$state (ok)" "$health"
      else
        printf '  %-16s %-12s %s\n' "$svc" "$state ($exit_code)" "$health"
        fail "$svc exited with code $exit_code"
      fi
    else
      printf '  %-16s %-12s %s\n' "$svc" "$state" "$health"
      fail "$svc is $state (health: $health)"
    fi
  done <<< "$rows"

  heading "5. Endpoints"
  local targets=(
    "api|http://localhost:8000/health"
    "api db|http://localhost:8000/health/db"
    "branding-agent|http://localhost:8001/health"
    "website-agent|http://localhost:8002/health"
    "run-engine|http://localhost:8003/health"
  )
  local entry name url code
  for entry in "${targets[@]}"; do
    name="${entry%%|*}"; url="${entry#*|}"
    code=$(http_probe "$url")
    if [ "$code" = "200" ]; then
      pass "$name  $url"
    else
      fail "$name  $url  (HTTP $code)"
    fi
  done

  heading "6. Service-to-service auth (chat start)"
  local api_key agent_key website_key run_key
  api_key=$(compose exec -T api printenv BRANDING_AGENT_API_KEY 2>/dev/null | tr -d '\r')
  agent_key=$(compose exec -T branding-agent printenv SERVICE_API_KEY 2>/dev/null | tr -d '\r')
  website_key=$(compose exec -T api printenv WEBSITE_AGENT_API_KEY 2>/dev/null | tr -d '\r')
  run_key=$(compose exec -T api printenv RUN_ENGINE_API_KEY 2>/dev/null | tr -d '\r')
  if [ -z "$api_key" ] || [ -z "$agent_key" ]; then
    warn "could not read service keys (stack not fully running)"
  else
    if [ "$api_key" = "$agent_key" ]; then
      pass "API <-> branding-agent key matches"
    else
      fail "API BRANDING_AGENT_API_KEY != branding-agent SERVICE_API_KEY (chat will get 401)"
    fi
    local website_svc_key run_svc_key
    website_svc_key=$(compose exec -T website-agent printenv SERVICE_API_KEY 2>/dev/null | tr -d '\r')
    run_svc_key=$(compose exec -T run-engine printenv SERVICE_API_KEY 2>/dev/null | tr -d '\r')
    if [ "$website_key" = "$website_svc_key" ]; then
      pass "API <-> website-agent key matches"
    else
      fail "API WEBSITE_AGENT_API_KEY != website-agent SERVICE_API_KEY"
    fi
    if [ "$run_key" = "$run_svc_key" ]; then
      pass "API <-> run-engine key matches"
    else
      fail "API RUN_ENGINE_API_KEY != run-engine SERVICE_API_KEY"
    fi
  fi

  heading "7. Dependency report (/health/deps)"
  local deps_code deps_body
  deps_code=$(http_probe "http://localhost:8000/health/deps")
  deps_body=$(http_body "http://localhost:8000/health/deps")
  if [ "$deps_code" = "200" ]; then
    pass "all API dependencies healthy"
  else
    fail "API dependencies degraded (HTTP $deps_code)"
  fi
  if [ -n "$deps_body" ] && command -v python3 >/dev/null 2>&1; then
    printf '%s' "$deps_body" | python3 -m json.tool 2>/dev/null | sed 's/^/  /' || printf '  %s\n' "$deps_body"
  fi

  if [ "$FAILURES" -gt 0 ]; then
    heading "Recent logs for failing services"
    compose ps -a --format '{{.Service}}|{{.State}}|{{.Health}}' 2>/dev/null \
      | awk -F'|' '$2 != "running" && $1 != "migrate" || ($2 == "running" && $3 != "healthy" && $3 != "") { print $1 }' \
      | while read -r svc; do
          [ -z "$svc" ] && continue
          printf '\n  --- %s (last 40 lines) ---\n' "$svc"
          compose logs --tail=40 "$svc" 2>&1 | sed 's/^/  /'
        done
  fi

  [ "$FAILURES" -eq 0 ]
}

if [ "$wait_for" -gt 0 ]; then
  printf 'Waiting up to %ss for the stack to become healthy...\n' "$wait_for"
  report=$(mktemp)
  while :; do
    FAILURES=0; WARNINGS=0
    rc=0
    check_stack > "$report" 2>&1 || rc=$?
    if [ "$rc" -eq 0 ]; then
      cat "$report"
      rm -f "$report"
      printf '\n%sStack is healthy.%s\n' "$GREEN" "$NC"
      exit 0
    fi
    if [ "$waited" -ge "$wait_for" ]; then
      cat "$report"
      rm -f "$report"
      printf '\n%sStack did not become healthy within %ss.%s\n' "$RED" "$wait_for" "$NC"
      exit 1
    fi
    sleep 5
    waited=$((waited + 5))
    printf '.'
  done
else
  check_stack
fi

printf '\n%sSummary:%s %d failure(s), %d warning(s)\n' "$BOLD" "$NC" "$FAILURES" "$WARNINGS"
[ "$FAILURES" -eq 0 ] || exit 1
