#!/usr/bin/env bash
set -e

echo "============================================"
echo "  BUILD TIKTOK AUCTION TOOL (uv + pyinstaller)"
echo "============================================"
echo

if ! command -v uv &>/dev/null; then
    echo "[LOI] Chua cai uv. Cai bang:"
    echo '  curl -LsSf https://astral.sh/uv/install.sh | sh'
    exit 1
fi

echo "[1/4] Sync dependencies..."
uv sync --dev

echo
echo "[2/4] Don dep build cu..."
rm -rf build dist TikTokAuction.spec

echo
echo "[3/4] Build exe (co the mat 2-5 phut)..."
uv run pyinstaller \
  --name TikTokAuction \
  --onefile \
  --windowed \
  --add-data "overlay.html:." \
  --hidden-import aiohttp \
  --hidden-import TikTokLive \
  --hidden-import TikTokLive.events \
  --collect-all TikTokLive \
  --collect-all PySide6 \
  --noconfirm \
  app.py

echo
echo "[4/4] HOAN THANH!"
echo
echo "File output: dist/TikTokAuction"