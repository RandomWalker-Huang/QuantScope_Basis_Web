@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 请把从 QuantScope r13 导出的升贴水HTML完整路径粘贴到下面。
echo 例如：C:\Users\19398\Downloads\QuantScope_Basis_Interactive_20260809_120000.html
echo.
set /p HTML_PATH=HTML路径：
if "%HTML_PATH%"=="" (
  echo 未输入路径，操作已取消。
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File tools\update_site.ps1 -HtmlPath "%HTML_PATH%"
echo.
pause

