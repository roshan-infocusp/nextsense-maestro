#!/bin/bash

# Usage: bash run_tests.sh [dev|staging|prod] [app_id]
# Defaults to dev if no argument is provided.
# APP_ID can also be passed as an env var: APP_ID=com.my.app bash run_tests.sh dev

ENV=${1:-dev}
CUSTOM_APP_ID=${2:-$APP_ID}   # CLI arg takes priority, then env var

case "$ENV" in
  dev)
    APP_ID="${CUSTOM_APP_ID:-io.nextsense.android.budz}"
    TEST_NAME="Dev_User"
    TEST_EMAIL="infocuspqapune@gmail.com"
    TEST_PASSWORD="Test@123"
    ;;
  staging)
    APP_ID="${CUSTOM_APP_ID:-io.nextsense.android.budz}"
    TEST_NAME="Stage_User"
    TEST_EMAIL="infocuspqapune@gmail.com"
    TEST_PASSWORD="Test@123"
    ;;
  prod)
    APP_ID="${CUSTOM_APP_ID:-io.nextsense.android.budz}"
    TEST_NAME="Prod_User"
    TEST_EMAIL="infocuspqapune@gmail.com"
    TEST_PASSWORD="Test@123"
    ;;
  *)
    echo "Unknown environment: $ENV"
    echo "Usage: bash run_tests.sh [dev|staging|prod] [app_id]"
    exit 1
    ;;
esac

# ── Clean previous reports ────────────────────────────────────
echo "Cleaning previous reports..."
find reports/ -mindepth 1 -maxdepth 1 -type d ! -name "screenshots" -exec rm -rf {} +
rm -f reports/*.html
rm -f reports/screenshots/*.png
mkdir -p reports/screenshots

echo "Running onboarding smoke test on [$ENV] environment..."

# ── Run tests ─────────────────────────────────────────────────
maestro test \
  --config config/env.yaml \
  --device emulator-5556 \
  --format html-detailed \
  --output reports/report.html \
  --env APP_ID="$APP_ID" \
  --env TEST_NAME="$TEST_NAME" \
  --env TEST_EMAIL="$TEST_EMAIL" \
  --env TEST_PASSWORD="$TEST_PASSWORD" \
  flows/onboarding_smoke.yaml

open reports/report.html
