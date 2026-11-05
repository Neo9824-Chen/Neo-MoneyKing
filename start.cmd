@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "ELECTRON_RUN_AS_NODE="
set "ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/"
if not exist "node_modules\electron\dist\electron.exe" (
  echo [Neo-MoneyKing] Installing Electron, first run may take a few minutes...
  where npm >nul 2>nul
  if errorlevel 1 (
    echo [ERROR] Node.js / npm not found. Install Node.js LTS from https://nodejs.org
    echo Or simply double-click index.html to use the browser version.
    pause
    exit /b 1
  )
  call npm install --registry=https://registry.npmmirror.com
  if errorlevel 1 call npm install
  if errorlevel 1 (
    echo [ERROR] npm install failed. Check network and retry.
    pause
    exit /b 1
  )
)
call npm start
