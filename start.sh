#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
unset ELECTRON_RUN_AS_NODE
export ELECTRON_MIRROR="${ELECTRON_MIRROR:-https://npmmirror.com/mirrors/electron/}"
if [ ! -d node_modules/electron ]; then
  if ! command -v npm >/dev/null 2>&1; then
    echo "[ERROR] Node.js / npm not found. Install from https://nodejs.org, or open index.html in a browser."
    exit 1
  fi
  echo "[Neo-MoneyKing] Installing Electron (first run may take a few minutes)..."
  npm install --registry=https://registry.npmmirror.com || npm install
fi
exec npm start
