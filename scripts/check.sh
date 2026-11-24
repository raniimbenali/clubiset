#!/usr/bin/env bash
# Controle du projet ClubISET.
# Code de sortie : 0 si tout est OK, 1 si au moins un controle echoue.
set -uo pipefail

cd "$(dirname "$0")/.." || exit 1
PYTHON="${PYTHON:-python}"
ERRORS=0

ok()   { echo "[OK]   $1"; }
fail() { echo "[FAIL] $1"; ERRORS=$((ERRORS + 1)); }

echo "== 1. Fichiers obligatoires =="
for f in README.md requirements.txt pytest.ini .gitignore .env.example app/__init__.py tests/test_app.py; do
  if [ -f "$f" ]; then ok "$f present"; else fail "$f manquant"; fi
done

echo "== 2. Aucun secret dans le depot =="
if grep -qx ".env" .gitignore 2>/dev/null; then
  ok ".env est dans .gitignore"
else
  fail ".env n'est pas dans .gitignore"
fi

if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  fail ".env est suivi par Git (retirer avec : git rm --cached .env)"
else
  ok ".env n'est pas suivi par Git"
fi

if grep -rEiq "(password|secret|token|api[_-]?key)[[:space:]]*=[[:space:]]*['\"][^'\"]{6,}" app tests; then
  fail "mot de passe ou secret en dur dans le code"
else
  ok "aucun secret en dur dans app/ et tests/"
fi

echo "== 3. Tests =="
if "$PYTHON" -m pytest -q; then
  ok "tests reussis"
else
  fail "tests en echec"
fi

echo "=============================="
if [ "$ERRORS" -eq 0 ]; then
  echo "Resultat : SUCCES"
  exit 0
else
  echo "Resultat : ECHEC ($ERRORS controle(s) en erreur)"
  exit 1
fi