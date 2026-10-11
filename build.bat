@echo off
setlocal
echo ============================================
echo   BUILD TIKTOK AUCTION TOOL
echo ============================================
echo.

where uv >nul 2>nul
if errorlevel 1 (
    echo [ERROR] uv not installed.
    pause
    exit /b 1
)

echo [1/4] Sync dependencies...
uv sync --dev
if errorlevel 1 goto :error

echo.
echo [2/4] Cleaning...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "TikTokAuction.spec" del "TikTokAuction.spec"

echo.
echo [3/4] Building exe...
uv run pyinstaller ^
  --name TikTokAuction ^
  --onefile ^
  --windowed ^
  --add-data "overlay.html;." ^
  --add-data "overlay.css;." ^
  --add-data "cmt.html;." ^
  --add-data "cmt.css;." ^
  --add-data "gift-fx.html;." ^
  --add-data "gift-fx.css;." ^
  --add-data "gift-text.html;." ^
  --add-data "gift-text.css;." ^
  --add-data "assets;assets" ^
  --hidden-import aiohttp ^
  --hidden-import TikTokLive ^
  --hidden-import TikTokLive.events ^
  --collect-all TikTokLive ^
  --collect-all PySide6 ^
  --noconfirm ^
  app.py

if errorlevel 1 goto :error

echo.
echo [4/4] DONE!
echo File: dist\TikTokAuction.exe
pause
exit /b 0

:error
echo.
echo [ERROR] Build failed.
pause
exit /b 1