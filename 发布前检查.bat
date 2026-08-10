@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -3 tools\validate_public_site.py index.html
echo.
pause

