#!/usr/bin/env bash
# Mise en service d'une version publiee : ./scripts/deploy.sh 1.0.0
set -euo pipefail
cd "$(dirname "$0")/.."

VERSION="${1:?Usage: ./scripts/deploy.sh <version>  (exemple : 1.0.0)}"
export APP_VERSION="$VERSION"
COMPOSE="docker compose -f docker-compose.deploy.yml"
URL="http://localhost:8080/health"

echo "== Mise en service de la version $VERSION =="
$COMPOSE pull app
$COMPOSE up -d --no-build --wait

echo "== Controle de sante =="
for i in $(seq 1 15); do
  if RESPONSE=$(curl -fsS "$URL" 2>/dev/null); then
    echo "$RESPONSE"
    if echo "$RESPONSE" | grep -q "\"version\":\"$VERSION\""; then
      echo "[OK]   version $VERSION en service"
      exit 0
    fi
    echo "[FAIL] une autre version est en service"
    exit 1
  fi
  sleep 2
done

echo "[FAIL] /health ne repond pas"
exit 1