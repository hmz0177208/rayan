@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Running Rayyan image fixer v2...
where py >nul 2>nul
if errorlevel 1 (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python was not found. Install Python from https://www.python.org/downloads/windows/ and try again.
    pause
    exit /b 1
  )
  set PYTHON_CMD=python
) else (
  set PYTHON_CMD=py
)
%PYTHON_CMD% "fix_site_images_v2.py"
if errorlevel 1 (
  echo.
  echo The script failed. Make sure these two files are beside index.html in public_html.
)
echo.
pause
